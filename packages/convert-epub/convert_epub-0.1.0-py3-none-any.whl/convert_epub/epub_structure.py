from __future__ import annotations

from typing import Any

from ebooklib import epub
from pydantic import BaseModel, ConfigDict, Field


class MetadataEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: str
    attributes: dict[str, str] = Field(default_factory=dict)


class ManifestItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    href: str
    media_type: str
    properties: list[str] = Field(default_factory=list)
    fallback: str | None = None
    fallback_style: str | None = None


class SpineItemRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    idref: str
    linear: bool = True
    properties: list[str] = Field(default_factory=list)


class TocEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    href: str | None = None
    uid: str | None = None
    children: list["TocEntry"] = Field(default_factory=list)


class Epub3Book(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str = "3.0"
    metadata: dict[str, dict[str, list[MetadataEntry]]] = Field(default_factory=dict)
    manifest: list[ManifestItem] = Field(default_factory=list)
    spine: list[SpineItemRef] = Field(default_factory=list)
    toc: list[TocEntry] = Field(default_factory=list)
    nav_item_id: str | None = None
    cover_item_id: str | None = None

    def manifest_by_id(self) -> dict[str, ManifestItem]:
        return {item.id: item for item in self.manifest}

    @classmethod
    def from_ebooklib(cls, book: epub.EpubBook) -> "Epub3Book":
        return cls(
            version=str(book.version),
            metadata=_parse_metadata(book),
            manifest=_parse_manifest(book),
            spine=_parse_spine(book),
            toc=_parse_toc(book),
            nav_item_id=_get_nav_item_id(book),
            cover_item_id=_get_cover_item_id(book),
        )


def _clean_attrs(attrs: dict[str, Any] | None) -> dict[str, str]:
    if not attrs:
        return {}
    return {str(key): str(value) for key, value in attrs.items()}


def _parse_metadata(book: epub.EpubBook) -> dict[str, dict[str, list[MetadataEntry]]]:
    metadata: dict[str, dict[str, list[MetadataEntry]]] = {}
    for namespace, names in book.metadata.items():
        namespace_map: dict[str, list[MetadataEntry]] = {}
        for name, values in names.items():
            entries = [
                MetadataEntry(value=str(value), attributes=_clean_attrs(attrs))
                for value, attrs in values
            ]
            namespace_map[str(name)] = entries
        metadata[str(namespace)] = namespace_map
    return metadata


def _parse_manifest(book: epub.EpubBook) -> list[ManifestItem]:
    manifest: list[ManifestItem] = []
    for item in book.get_items():
        manifest.append(
            ManifestItem(
                id=str(item.get_id()),
                href=str(item.get_name()),
                media_type=str(item.get_type()),
                properties=list(getattr(item, "properties", []) or []),
                fallback=getattr(item, "fallback", None),
                fallback_style=getattr(item, "fallback_style", None),
            )
        )
    return manifest


def _parse_spine(book: epub.EpubBook) -> list[SpineItemRef]:
    spine: list[SpineItemRef] = []
    for item, linear in book.spine:
        item_id = item if isinstance(item, str) else getattr(item, "id", None)
        if not item_id:
            continue
        spine.append(
            SpineItemRef(
                idref=str(item_id),
                linear=bool(linear),
                properties=list(getattr(item, "properties", []) or []),
            )
        )
    return spine


def _parse_toc(book: epub.EpubBook) -> list[TocEntry]:
    def parse_entry(entry: Any) -> TocEntry:
        if isinstance(entry, epub.Link):
            return TocEntry(title=entry.title, href=entry.href, uid=entry.uid)
        if isinstance(entry, epub.Section):
            return TocEntry(title=entry.title, href=entry.href)
        if isinstance(entry, tuple) and len(entry) == 2:
            head, children = entry
            parsed = parse_entry(head)
            parsed.children = [parse_entry(child) for child in children]
            return parsed
        if isinstance(entry, list):
            return TocEntry(
                title="",
                children=[parse_entry(child) for child in entry],
            )
        return TocEntry(title=str(entry))

    return [parse_entry(entry) for entry in (book.toc or [])]


def _get_nav_item_id(book: epub.EpubBook) -> str | None:
    for item in book.get_items():
        if epub.ITEM_NAV == item.get_type():
            return str(item.get_id())
    return None


def _get_cover_item_id(book: epub.EpubBook) -> str | None:
    cover_id = getattr(book, "cover", None)
    if cover_id:
        return str(cover_id)
    for item in book.get_items():
        if epub.ITEM_COVER == item.get_type():
            return str(item.get_id())
    return None
