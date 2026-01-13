from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable, Optional

import duckdb
import typer
from ebooklib import epub  # type: ignore
from rich.console import Console
from rich.console import Group
from rich.live import Live
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

console = Console()
progress = Progress(
    TextColumn("[progress.description]{task.description}"),
    SpinnerColumn("dots"),
    BarColumn(bar_width=None),
    MofNCompleteColumn(),
    TimeElapsedColumn(),
    console=console,
)


@dataclass(frozen=True)
class Chapter:
    """Structured chapter data extracted from an EPUB."""

    title: str
    file_path: str
    chapter_number: int
    order: int
    html: str
    markdown: Optional[str] = None


def extract_chapters(epub_path: str | Path) -> list[Chapter]:
    """Extract chapters from an EPUB3 file using ebooklib."""
    book = epub.read_epub(str(epub_path))
    toc_map = _build_toc_map(book.toc)

    chapters: list[Chapter] = []
    order = 1
    chapter_number = 1
    for spine_item, _linear in book.spine:
        item_id = spine_item if isinstance(spine_item, str) else spine_item.get_id()
        item = book.get_item_with_id(item_id)
        if item is None or not _is_document_item(item):
            continue

        href = item.get_name()
        title = toc_map.get(href) or toc_map.get(_strip_fragment(href)) or href
        content_html = item.get_content().decode("utf-8", errors="replace")
        chapters.append(
            Chapter(
                title=title,
                file_path=href,
                chapter_number=chapter_number,
                order=order,
                html=content_html,
            )
        )
        order += 1
        chapter_number += 1

    return chapters


def _is_document_item(item: object) -> bool:
    item_type = getattr(item, "get_type", lambda: None)()
    nav_type = getattr(epub, "ITEM_NAV", None) or getattr(epub, "ITEM_NAVIGATION", None)
    if nav_type is not None and item_type == nav_type:
        return False

    doc_type = getattr(epub, "ITEM_DOCUMENT", None)
    if doc_type is not None:
        return item_type == doc_type

    nav_class = getattr(epub, "EpubNav", None)
    if nav_class is not None and isinstance(item, nav_class):
        return False

    html_class = getattr(epub, "EpubHtml", None)
    if html_class is not None:
        return isinstance(item, html_class)

    return False


def store_chapters_in_duckdb(
    chapters: Iterable[Chapter], db_path: str | Path, table_name: str = "chapters"
) -> None:
    """Store chapter data in a DuckDB table, creating it if needed."""
    db_path = str(db_path)
    safe_table = _validate_table_name(table_name)
    with duckdb.connect(db_path) as conn:
        conn.execute(
            f"""
            create table if not exists {safe_table} (
                title text,
                file_path text,
                chapter_number integer,
                order_number integer,
                html text,
                markdown text
            )
            """
        )
        conn.executemany(
            f"""
            insert into {safe_table} (
                title,
                file_path,
                chapter_number,
                order_number,
                html,
                markdown
            )
            values (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    chapter.title,
                    chapter.file_path,
                    chapter.chapter_number,
                    chapter.order,
                    chapter.html,
                    chapter.markdown,
                )
                for chapter in chapters
            ],
        )


def _strip_fragment(href: str) -> str:
    return href.split("#", 1)[0]


def _validate_table_name(table_name: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table_name):
        raise ValueError(f"Invalid table name: {table_name!r}")
    return table_name


def _build_toc_map(toc: Iterable[object]) -> dict[str, str]:
    """Flatten the EPUB TOC into an href->title map."""
    mapping: dict[str, str] = {}

    def walk(entry: object) -> None:
        if isinstance(entry, epub.Link):
            mapping[_strip_fragment(entry.href)] = entry.title
            return
        if isinstance(entry, epub.Section):
            if entry.href:
                mapping[_strip_fragment(entry.href)] = entry.title
            return
        if isinstance(entry, tuple) and len(entry) == 2:
            head, children = entry
            walk(head)
            for child in children:
                walk(child)
            return
        if isinstance(entry, list):
            for child in entry:
                walk(child)
            return

    for entry in toc or []:
        walk(entry)

    return mapping


def main(
    epub_path: Path = typer.Argument(..., help="Path to the EPUB file", metavar="EPUB_PATH"),
    table: str = typer.Option(
        "chapters",
        "--table",
        help="DuckDB table name to store chapters in",
    ),
) -> None:
    """Extract chapters from an EPUB and store them in DuckDB."""
    ebook_path: Path = Path(epub_path)
    ebook_stem: str = _slugify(ebook_path.stem)
    db_path: Path = Path("static") / f"{ebook_stem}.duckdb"
    chapters = extract_chapters(ebook_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    store_chapters_in_duckdb(chapters, db_path, table_name=table)

    ordered_chapters = sorted(chapters, key=lambda c: c.order)
    progress_table = Table("Extracted Chapters", show_header=True, header_style="bold white")
    progress_table.add_column("Chapter", style="bold #9f0", width=8, justify="right")
    progress_table.add_column("Title", style="bold rgb(87 188 255)", justify="left")
    progress_table.add_column("File Path", style="dim italic", justify="left")
    extract_ch_task = progress.add_task("Extracting Chapters...", total=len(ordered_chapters))
    render_group = Group(progress_table, progress)
    with Live(render_group, console=console, refresh_per_second=4) as live:
        for chapter in ordered_chapters:
            progress_table.add_row(
                str(chapter.chapter_number),
                chapter.title,
                chapter.file_path,
            )

            progress.advance(extract_ch_task)
            live.refresh()


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-")
    return cleaned.lower() or "ebook"

if __name__ == "__main__":
    typer.run(main)
