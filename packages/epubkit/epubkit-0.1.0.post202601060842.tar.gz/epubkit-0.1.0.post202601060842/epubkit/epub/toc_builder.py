"""
TOC Builder - Specialized component for EPUB table of contents parsing
"""

import logging
import os
import re
from typing import Any, Dict, List

from ..interfaces import ContentReader
from .metadata_parser import extract_book_title
from .opf_parser import parse_opf, parse_spine_items, _parse_layout_properties_et
from .path_resolver import normalize_src_for_matching
from .toc_parser import (
    parse_nav_document_robust,
    parse_ncx_document_robust,
    parse_landmarks,
    parse_page_list,
)

logger = logging.getLogger(__name__)

try:
    from bs4 import BeautifulSoup

    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


class TOCBuilder:
    """
    Specialized component for building EPUB table of contents.

    Handles EPUB2/3 TOC parsing with proper fallbacks:
    - nav.xhtml (EPUB3)
    - toc.ncx (EPUB2)
    - spine fallback (emergency)
    """

    def __init__(self, reader: ContentReader):
        """
        Initialize TOC builder with content reader interface.

        Args:
            reader: Content reader interface for accessing EPUB content
        """
        self.reader = reader

    def build_toc(self) -> Dict:
        """
        Build comprehensive TOC with proper EPUB standard support.

        Returns:
            Dict containing 'book_title', 'nodes', 'spine_order', 'toc_source', 'raw_chapters', 'layout_properties', 'spine_items'
        """
        try:
            return self._extract_structured_toc()
        except Exception as e:
            logger.warning(f"Structured TOC extraction failed: {e}")
            return self._spine_fallback_toc()

    def _extract_structured_toc(self) -> Dict:
        """
        Extract structured TOC following EPUB standards.
        Priority: nav.xhtml (EPUB3) → toc.ncx (EPUB2) → spine fallback
        """
        if not self.reader.zf or not self.reader.opf_path:
            raise RuntimeError("EPUB not properly opened")

        if self.reader.trace:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("--- Starting TOC Build Process ---")

        # Read OPF file
        opf_bytes = self._read_opf_file()
        opf = self._parse_opf_content(opf_bytes)

        # Extract metadata
        book_title = extract_book_title(opf, self.reader.epub_path)
        basedir = os.path.dirname(self.reader.opf_path)
        basedir = f"{basedir}/" if basedir else ""

        # Parse OPF structure and reuse results to avoid duplicate parsing
        # Unpack the results that parse_opf already logged about
        manifest, spine_order, ncx, navdoc, layout_properties = parse_opf(
            opf_bytes, basedir)

        # Parse enhanced spine items (from epub.js approach)
        spine_items = parse_spine_items(opf_bytes, basedir, manifest)

        if self.reader.trace:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    f"TOC Builder: Reusing parsed OPF data - spine has {len(spine_order)} items."
                )

        # Parse TOC from various sources
        toc_result = self._parse_toc_sources(navdoc, ncx, basedir, spine_order)
        nodes, raw_chapters, toc_source = toc_result

        # Parse additional navigation elements (enhanced from foliate-js)
        landmarks = []
        page_list = []

        if navdoc:
            landmarks = parse_landmarks(self.reader, navdoc)
            page_list = parse_page_list(self.reader, navdoc)

        if self.reader.trace:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    f"--- TOC Build Process Finished. Final source: {toc_source} ---"
                )
                logger.debug(
                    f"Additional navigation: {len(landmarks)} landmarks, {len(page_list)} pages")

        return {
            "book_title": book_title,
            "nodes": nodes,
            "spine_order": spine_order,
            "toc_source": toc_source,
            "raw_chapters": raw_chapters,
            "layout_properties": layout_properties,
            "spine_items": spine_items,
            "landmarks": landmarks,
            "page_list": page_list,
        }

    def _read_opf_file(self) -> bytes:
        """Read and return OPF file content."""
        try:
            return self.reader.zf.read(self.reader.opf_path)
        except KeyError:
            # Try case-insensitive search
            opf_path = self.reader.opf_path
            if opf_path:
                for name in self.reader.zip_namelist:
                    if name.lower() == opf_path.lower():
                        return self.reader.zf.read(name)
            raise FileNotFoundError(f"OPF file not found: {opf_path}")

    def _parse_opf_content(self, opf_bytes: bytes) -> Any:
        """Parse OPF content based on available XML parser."""
        if HAS_BS4:
            return BeautifulSoup(opf_bytes.decode("utf-8", errors="replace"), "xml")
        else:
            import xml.etree.ElementTree as ET

            return ET.fromstring(opf_bytes)

    def _parse_toc_sources(
        self, navdoc: str, ncx: str, basedir: str, spine_order: List[str]
    ) -> tuple[List[Dict], List[Dict], str]:
        """Parse TOC from various sources with proper fallbacks."""
        raw_chapters = []
        nodes = []
        toc_source = "None"

        # Try NAV document first (EPUB3)
        if navdoc:
            raw_chapters = self._parse_nav_toc(navdoc, ncx, basedir)
            if raw_chapters:
                # Check if we need to fallback to NCX for better grouping
                # Now also check for hierarchical groups (from flat_grouped parsing)
                has_groups = any(
                    chap.get("type") in ("group_header", "group") for chap in raw_chapters
                )
                if not has_groups and ncx:
                    nodes = parse_ncx_document_robust(
                        self.reader, ncx, basedir)
                    if nodes:
                        toc_source = "toc.ncx"
                        raw_chapters = self._flatten_toc_nodes_for_raw_list(
                            nodes)
                        return nodes, raw_chapters, toc_source
                # Build nodes from raw chapters for NAV
                nodes = self._build_node_hierarchy(raw_chapters)
                toc_source = "nav.xhtml"
                return nodes, raw_chapters, toc_source

        # Try NCX document (EPUB2)
        if not raw_chapters and ncx:
            nodes = parse_ncx_document_robust(self.reader, ncx, basedir)
            if nodes:
                toc_source = "toc.ncx"
                raw_chapters = self._flatten_toc_nodes_for_raw_list(nodes)
                return nodes, raw_chapters, toc_source

        # Fallback to spine parsing
        if not raw_chapters and spine_order:
            toc_source = "spine"
            raw_chapters = self._build_spine_chapters(spine_order)
            nodes = raw_chapters.copy()  # For spine fallback, nodes are simple chapters

        return nodes, raw_chapters, toc_source

    def _parse_nav_toc(self, navdoc: str, ncx: str, basedir: str) -> List[Dict]:
        """Parse NAV document and fallback logic."""
        raw_chapters = parse_nav_document_robust(self.reader, navdoc)
        return raw_chapters

    def _build_spine_chapters(self, spine_order: List[str]) -> List[Dict]:
        """Build raw chapters from spine order as last resort."""
        raw_chapters = []
        for spine_href in spine_order:
            title = os.path.basename(spine_href)
            title = os.path.splitext(title)[0]
            title = title.replace("_", " ").replace("-", " ")
            title = " ".join(word.capitalize() for word in title.split())

            if self.reader.trace:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(
                        f"  item: Creating chapter from spine: '{title}' -> '{spine_href}'"
                    )

            raw_chapters.append(
                {
                    "type": "chapter",
                    "title": title,
                    "src": spine_href,
                    "normalized_src": normalize_src_for_matching(spine_href),
                }
            )
        return raw_chapters

    def _build_node_hierarchy(self, raw_chapters: List[Dict]) -> List[Dict]:
        """
        Build hierarchical node structure from raw chapters with level support.

        This method now handles two types of input:
        1. Flat list with group_header/chapter items (legacy)
        2. Already hierarchical structure with children (from parse_flat_grouped_nav)
        """
        # Check if input is already hierarchical (has groups with children)
        has_hierarchical_groups = any(
            chap.get("type") == "group" and chap.get("children")
            for chap in raw_chapters
        )

        if has_hierarchical_groups:
            # Input is already hierarchical, just clean it up and return
            if self.reader.trace:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(
                        "--- Input already hierarchical, using as-is ---")
            return self._clean_hierarchical_nodes(raw_chapters)
        else:
            # Input is flat, build hierarchy using legacy logic
            return self._build_hierarchy_from_flat(raw_chapters)

    def _clean_hierarchical_nodes(self, nodes: List[Dict]) -> List[Dict]:
        """Clean up already hierarchical nodes and ensure proper structure."""
        cleaned_nodes = []

        for node in nodes:
            if node.get("type") == "group":
                # Ensure group has required fields
                clean_group = {
                    "type": "group",
                    "title": node.get("title", "Group"),
                    "expanded": node.get("expanded", False),
                    "children": []
                }

                # Recursively clean children
                if node.get("children"):
                    clean_group["children"] = self._clean_hierarchical_nodes(
                        node["children"])

                cleaned_nodes.append(clean_group)

                if self.reader.trace:
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(
                            f"Processed hierarchical group: '{clean_group['title']}' with {len(clean_group['children'])} children")

            elif node.get("type") == "chapter":
                # Ensure chapter has required fields
                clean_chapter = {
                    "type": "chapter",
                    "title": node.get("title", "Untitled"),
                    "src": node.get("src", "")
                }
                cleaned_nodes.append(clean_chapter)

                if self.reader.trace:
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(
                            f"Processed hierarchical chapter: '{clean_chapter['title']}'")

        return cleaned_nodes

    def _build_hierarchy_from_flat(self, raw_chapters: List[Dict]) -> List[Dict]:
        """Build hierarchical node structure from flat raw chapters (legacy logic)."""
        nodes = []
        group_stack = []  # Stack to track nested groups
        processed_chapters = set()  # Track processed chapters to avoid duplicates

        if self.reader.trace:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    "--- Finalizing Node Structure (Grouping with levels) ---")

        # Define patterns for grouping
        volume_pattern = re.compile(r"^(第.*卷|volume\s*\d+)\s*$", re.IGNORECASE)

        for chap in raw_chapters:
            title = chap["title"]
            level = chap.get("level", 0)
            chap_type = chap.get("type", "chapter")

            # Adjust stack to match current level
            while len(group_stack) > level:
                group_stack.pop()

            # Check for volume grouping (legacy support)
            if volume_pattern.match(title):
                if self.reader.trace:
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(
                            f"Creating new group from volume pattern: '{title}' (level {level})"
                        )
                current_group = {
                    "type": "group",
                    "title": title,
                    "expanded": False,
                    "children": [],
                    "src": chap.get("src"),
                }

                # Add to appropriate parent or root
                if group_stack:
                    group_stack[-1]["children"].append(current_group)
                else:
                    nodes.append(current_group)

                group_stack.append(current_group)

            # Check for group header from nested parsing
            elif chap_type == "group_header":
                if self.reader.trace:
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(
                            f"Creating new group from 'group_header': '{title}' (level {level})"
                        )
                current_group = {
                    "type": "group",
                    "title": title,
                    "expanded": False,
                    "children": [],
                }

                # Add to appropriate parent or root
                if group_stack and len(group_stack) > level:
                    # Find the correct parent level
                    parent_index = max(0, level - 1)
                    if parent_index < len(group_stack):
                        group_stack[parent_index]["children"].append(
                            current_group)
                    else:
                        nodes.append(current_group)
                else:
                    nodes.append(current_group)

                # Update stack
                while len(group_stack) > level:
                    group_stack.pop()
                group_stack.append(current_group)

            # Check for bracket grouping pattern (legacy fallback)
            elif (
                chap_type == "chapter"
                and title.startswith("【")
                and title.endswith("】")
            ):
                if self.reader.trace:
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(
                            f"Creating new group from fallback pattern '【...】': '{title}' (level {level})"
                        )
                current_group = {
                    "type": "group",
                    "title": title,
                    "expanded": False,
                    "children": [],
                }

                # Add to appropriate parent or root
                if group_stack:
                    group_stack[-1]["children"].append(current_group)
                else:
                    nodes.append(current_group)

                group_stack.append(current_group)

            # Regular chapter
            else:
                # Skip duplicate chapters
                chapter_key = (chap.get("src"), title)
                if chapter_key in processed_chapters:
                    if self.reader.trace:
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug(
                                f"Skipping duplicate chapter: '{title}'")
                    continue
                processed_chapters.add(chapter_key)

                node = {"type": "chapter", "title": title,
                        "src": chap.get("src")}
                if group_stack:
                    # Add to the current group
                    group_stack[-1]["children"].append(node)
                    if self.reader.trace:
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug(
                                f"  Adding chapter '{title}' to group '{group_stack[-1]['title']}'"
                            )
                else:
                    # Add to root level
                    nodes.append(node)
                    if self.reader.trace:
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug(
                                f"Adding chapter '{title}' as a top-level node."
                            )

        return nodes

    def _flatten_toc_nodes_for_raw_list(self, nodes: List[Dict]) -> List[Dict]:
        """Recursively flatten hierarchical nodes into a flat list for raw_chapters."""
        flat_list = []

        def recurse(node_list: List[Dict]):
            for node in node_list:
                if node.get("type") == "chapter":
                    flat_list.append(
                        {
                            "type": "chapter",
                            "title": node.get("title", "Untitled"),
                            "src": node.get("src", ""),
                            "normalized_src": normalize_src_for_matching(
                                node.get("src", "")
                            ),
                        }
                    )
                elif node.get("type") == "group":
                    if "children" in node and node["children"]:
                        recurse(node["children"])

        recurse(nodes)
        return flat_list

    def _spine_fallback_toc(self) -> Dict:
        """Emergency fallback: use basic spine parsing."""
        try:
            if not self.reader.zf or not self.reader.opf_path:
                raise RuntimeError("EPUB not properly opened")

            import xml.etree.ElementTree as ET

            opf_bytes = self.reader.zf.read(self.reader.opf_path)
            root = ET.fromstring(opf_bytes)

            # Extract manifest
            manifest = {}
            for item in root.findall(".//*[@id][@href]"):
                item_id = item.attrib.get("id")
                href = item.attrib.get("href")
                if item_id and href:
                    manifest[item_id] = href

            # Extract spine order
            spine_hrefs = []
            spine = root.find(".//spine") or root.find(".//{*}spine")
            if spine is not None:
                for itemref in spine.findall("itemref") or spine.findall("{*}itemref"):
                    idref = itemref.attrib.get("idref")
                    if idref and idref in manifest:
                        spine_hrefs.append(manifest[idref])

            # Build simple nodes
            nodes = []
            raw_chapters = []
            for idx, href in enumerate(spine_hrefs, 1):
                title = os.path.basename(href)
                title = os.path.splitext(title)[0]
                chapter_data = {
                    "type": "chapter",
                    "title": title,
                    "src": href,
                    "index": idx,
                    "normalized_src": normalize_src_for_matching(href),
                }
                nodes.append(chapter_data)
                raw_chapters.append(chapter_data)

            book_title = extract_book_title(root, self.reader.epub_path)

            # For fallback, try to parse layout properties too
            layout_properties = _parse_layout_properties_et(
                root) if not HAS_BS4 else {}

            # For fallback, create basic spine items
            spine_items = []
            for idx, href in enumerate(spine_hrefs):
                spine_items.append(type('SpineItem', (), {
                    'href': href,
                    'idref': f'item{idx}',
                    'linear': True,
                    'properties': []
                })())

            return {
                "book_title": book_title,
                "nodes": nodes,
                "spine_order": spine_hrefs,
                "toc_source": "fallback",
                "raw_chapters": raw_chapters,
                "layout_properties": layout_properties,
                "spine_items": spine_items,
            }

        except Exception as e:
            logger.error(f"Even fallback TOC parsing failed: {e}")
            return {
                "book_title": os.path.basename(self.reader.epub_path),
                "nodes": [],
                "spine_order": [],
                "toc_source": "error",
                "raw_chapters": [],
                "layout_properties": {},
                "spine_items": [],
            }
