"""Public package exports."""

from importlib.metadata import PackageNotFoundError, version

from .epub_extract import Chapter, extract_chapters, store_chapters_in_duckdb
from .epub_structure import Epub3Book

try:
    __version__ = version("convert-epub")
except PackageNotFoundError:  # pragma: no cover - runtime metadata only
    __version__ = "0.0.0"

__all__ = [
    "Chapter",
    "Epub3Book",
    "__version__",
    "extract_chapters",
    "store_chapters_in_duckdb",


