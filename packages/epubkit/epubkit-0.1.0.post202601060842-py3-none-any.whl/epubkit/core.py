"""
Core EPUB processing classes.
"""

from typing import Any, Dict, List, Optional

from .backends import ZipContentReader
from .epub.toc_builder import TOCBuilder
from .hooks import HookManager
from .interfaces import ContentReader


class EPUB:
    """
    Main EPUB processing class providing a high-level API.

    This is the primary interface for users of epubkit.
    """

    def __init__(self, path: str, trace: bool = False):
        """
        Open an EPUB file.

        Args:
            path: Path to the EPUB file
            trace: Enable trace logging for debugging
        """
        self._path = path
        self._trace = trace
        self._reader: Optional[ContentReader] = None
        self._toc_builder: Optional[TOCBuilder] = None
        self._toc_cache: Optional[Dict] = None
        self._layout_properties: Optional[Dict[str, Any]] = None
        self._spine_items: Optional[List] = None
        self._hooks: Optional[HookManager] = None

        self._open()

    def _open(self) -> None:
        """Initialize the EPUB reader and components."""
        self._reader = ZipContentReader(self._path, self._trace)
        self._toc_builder = TOCBuilder(self._reader)

    @property
    def path(self) -> str:
        """Path to the EPUB file."""
        return self._path

    @property
    def title(self) -> Optional[str]:
        """Book title extracted from metadata."""
        toc = self.toc
        return toc.get("book_title")

    @property
    def toc(self) -> Dict:
        """
        Table of contents data.

        Returns a dictionary containing:
        - book_title: Book title
        - nodes: Hierarchical TOC structure
        - spine_order: Reading order from OPF spine
        - toc_source: Source of TOC data (nav.xhtml, toc.ncx, spine)
        - raw_chapters: Flat list of chapters
        - layout_properties: Layout-related properties from OPF
        """
        if self._toc_cache is None:
            self._toc_cache = self._toc_builder.build_toc()
            # Extract layout properties for easy access
            self._layout_properties = self._toc_cache.get("layout_properties", {})
            # Extract spine items for easy access
            self._spine_items = self._toc_cache.get("spine_items", [])

            # Trigger hooks after TOC is built
            if self.hooks.toc_built.has_handlers():
                self.hooks.toc_built.trigger(self, self._toc_cache)

        return self._toc_cache

    @property
    def spine(self) -> List[Dict]:
        """Chapters in reading order."""
        return self.toc.get("raw_chapters", [])

    @property
    def metadata(self) -> Dict[str, Any]:
        """
        Basic metadata extracted from the EPUB.

        Returns a dictionary with available metadata fields.
        """
        toc = self.toc
        return {
            "title": toc.get("book_title"),
            "toc_source": toc.get("toc_source"),
            "spine_count": len(toc.get("spine_order", [])),
            "chapter_count": len(toc.get("raw_chapters", [])),
        }

    @property
    def layout_properties(self) -> Dict[str, Any]:
        """
        Layout properties extracted from the OPF file.

        Returns a dictionary containing layout-related properties such as:
        - layout: rendition:layout (pre-paginated, reflowable)
        - flow: rendition:flow (auto, paginated, scrolled-continuous)
        - orientation: rendition:orientation (auto, landscape, portrait)
        - spread: rendition:spread (auto, none, landscape, portrait, both)
        - page_progression_direction: reading direction (ltr, rtl)
        """
        # Ensure toc is loaded to populate layout_properties
        if self._layout_properties is None:
            _ = self.toc  # This will populate _layout_properties
        return self._layout_properties or {}

    @property
    def spine_items(self) -> List:
        """
        Enhanced spine items with properties (from epub.js approach).

        Returns a list of SpineItem objects containing:
        - href: Content href
        - idref: Manifest item ID
        - linear: Whether item is in linear reading order
        - properties: Additional properties from OPF
        """
        # Ensure toc is loaded to populate spine_items
        if self._spine_items is None:
            _ = self.toc  # This will populate _spine_items
        return self._spine_items or []

    @property
    def hooks(self) -> HookManager:
        """
        Hook system for extensibility (from epub.js approach).

        Provides hooks for various EPUB processing events:
        - content_parsed: After chapter content is parsed
        - chapter_loaded: After chapter is loaded from disk
        - toc_built: After TOC is built
        - toc_parsed: After TOC structure is parsed
        - metadata_extracted: After metadata is extracted
        - layout_parsed: After layout properties are parsed
        - spine_processed: After spine items are processed

        Returns:
            HookManager instance for registering event handlers
        """
        if self._hooks is None:
            self._hooks = HookManager()
        return self._hooks

    def get_spine_cfi(self, spine_index: int) -> str:
        """
        Generate CFI for a spine item (from epub.js approach).

        This creates a CFI that points to the beginning of a spine item,
        useful for bookmarking or navigation.

        Args:
            spine_index: Zero-based index of the spine item

        Returns:
            CFI string pointing to the spine item, or empty string if invalid
        """
        from .cfi import CFIGenerator

        if 0 <= spine_index < len(self.spine_items):
            item = self.spine_items[spine_index]
            return CFIGenerator.generate_chapter_cfi(spine_index, item.idref)
        return ""

    def read_chapter(self, href: str) -> str:
        """
        Read a chapter by its href.

        Args:
            href: The href of the chapter to read

        Returns:
            Chapter content as a string
        """
        content = self._reader.read_chapter(href)

        # Trigger hooks after chapter is loaded
        if self.hooks.chapter_loaded.has_handlers():
            self.hooks.chapter_loaded.trigger(self, href, content)

        return content

    def get_chapter_by_index(self, index: int) -> Optional[Dict]:
        """
        Get chapter by index in spine order.

        Args:
            index: Zero-based index in reading order

        Returns:
            Chapter info dictionary or None if index is invalid
        """
        spine = self.spine
        if 0 <= index < len(spine):
            return spine[index]
        return None

    def find_chapter_by_href(self, href: str) -> Optional[Dict]:
        """
        Find chapter by href.

        Args:
            href: Chapter href to search for

        Returns:
            Chapter info dictionary or None if not found
        """
        for chapter in self.spine:
            if chapter.get("src") == href:
                return chapter
        return None

    def close(self) -> None:
        """Close the EPUB file and clean up resources."""
        if self._reader:
            self._reader.close()
            self._reader = None
        self._toc_cache = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __repr__(self) -> str:
        title = self.title or "Unknown Title"
        return f"EPUB(title='{title}', path='{self.path}')"
