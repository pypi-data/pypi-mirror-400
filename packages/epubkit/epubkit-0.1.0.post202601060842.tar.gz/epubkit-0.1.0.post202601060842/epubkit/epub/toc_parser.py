import logging
import os
import re
from typing import Any, Dict, List

from ..interfaces import ContentReader
from .path_resolver import normalize_src_for_matching

logger = logging.getLogger(__name__)

try:
    from bs4 import BeautifulSoup

    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


def parse_nav_item_recursive(
    item: "BeautifulSoup",
    basedir: str,
    level: int = 0,
    max_depth: int = 10
) -> Dict[str, Any]:
    """
    Recursively parse a single navigation item and its children.

    Args:
        item: BeautifulSoup <li> element
        basedir: Base directory for resolving relative paths
        level: Current nesting level
        max_depth: Maximum allowed nesting depth

    Returns:
        Dict containing parsed navigation item with children
    """
    if level > max_depth:
        logger.warning(
            f"Maximum nesting depth ({max_depth}) exceeded, stopping recursion")
        return None

    span_tag = item.find("span")
    a_tag = item.find("a")
    sublist = item.find("ol")

    # Priority 1: Items with sublists (nested structure) are groups
    if sublist:
        # Extract title from <a> tag if present, otherwise from <span>
        if a_tag:
            title = " ".join(a_tag.text.strip().split())
            href = a_tag.get("href")
            if href:
                full_path = os.path.normpath(
                    os.path.join(basedir, href)).split("#")[0]
                src = full_path
            else:
                src = None
        elif span_tag:
            title = " ".join(span_tag.text.strip().split())
            src = None
        else:
            title = f"Group {level}"
            src = None

        # Recursively parse children
        children = []
        child_items = sublist.find_all("li", recursive=False)
        for child_item in child_items:
            child_node = parse_nav_item_recursive(
                child_item, basedir, level + 1, max_depth)
            if child_node:
                children.append(child_node)

        return {
            "type": "group",
            "title": title,
            "src": src,
            "children": children,
            "level": level,
            "expanded": False  # Default to collapsed
        }

    # Priority 2: Items with <a> links are chapters
    elif a_tag and a_tag.get("href"):
        href = a_tag.get("href")
        full_path = os.path.normpath(os.path.join(basedir, href)).split("#")[0]
        title = " ".join(a_tag.text.strip().split())

        return {
            "type": "chapter",
            "title": title,
            "src": full_path,
            "normalized_src": normalize_src_for_matching(full_path),
            "level": level
        }

    # Priority 3: Items with only <span> are group headers (legacy support)
    elif span_tag:
        title = " ".join(span_tag.text.strip().split())
        return {
            "type": "group_header",
            "title": title,
            "level": level
        }

    # Fallback: skip unrecognized items
    else:
        logger.debug(f"Skipping unrecognized nav item at level {level}")
        return None


def flatten_nav_structure(nodes: List[Dict], result: List[Dict] = None) -> List[Dict]:
    """
    Flatten hierarchical navigation structure to flat list for backward compatibility.

    Args:
        nodes: Hierarchical navigation nodes
        result: Accumulator for flattened results

    Returns:
        Flat list of navigation items compatible with existing code
    """
    if result is None:
        result = []

    # Track processed chapters to avoid duplicates in flattened structure
    processed_chapters = set()

    for node in nodes:
        if node["type"] == "group":
            # Add group header for backward compatibility
            result.append({
                "type": "group_header",
                "title": node["title"],
                "level": node.get("level", 0)
            })
            # Recursively flatten children
            if "children" in node:
                flatten_nav_structure(node["children"], result)
        elif node["type"] == "chapter":
            # Skip duplicate chapters
            chapter_key = (node.get("src"), node["title"])
            if chapter_key in processed_chapters:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(
                        f"Skipping duplicate chapter in flatten: {node['title']}")
                continue
            processed_chapters.add(chapter_key)

            result.append({
                "type": "chapter",
                "title": node["title"],
                "src": node["src"],
                "normalized_src": node.get("normalized_src"),
                "level": node.get("level", 0)
            })
        elif node["type"] == "group_header":
            result.append({
                "type": "group_header",
                "title": node["title"],
                "level": node.get("level", 0)
            })

    return result


def detect_toc_structure(nav_toc) -> str:
    """
    檢測 TOC 結構類型。

    分析 nav.xhtml 的結構模式，返回對應的處理策略：
    - "nested": 標準的巢狀 <ol> 結構
    - "flat_grouped": 扁平化群組結構（<span> + 連續 <a>）
    - "mixed": 混合結構
    - "unknown": 無法識別的結構

    Args:
        nav_toc: BeautifulSoup nav element

    Returns:
        str: 結構類型
    """
    list_items = nav_toc.find_all("li")

    # 檢查是否有巢狀 <ol>
    has_nested_ols = any(item.find("ol") for item in list_items)

    # 檢查是否有 <span> 標題
    has_span_headers = any(item.find("span") for item in list_items)

    # 檢查是否有連續的 <a> 項目（沒有 <ol> 包圍）
    flat_links = []
    for item in list_items:
        if item.find("a") and not item.find("ol"):
            flat_links.append(item)

    # 分析結構模式
    if has_nested_ols and not has_span_headers:
        return "nested"  # 標準巢狀結構
    elif has_span_headers and len(flat_links) > len(list_items) * 0.3:
        return "flat_grouped"  # 扁平化群組結構
    elif has_nested_ols and has_span_headers:
        return "mixed"  # 混合結構
    else:
        return "unknown"  # 其他結構


def parse_flat_grouped_nav(nav_toc, nav_basedir: str) -> List[Dict]:
    """
    解析扁平化群組結構的應變邏輯。

    這種結構的特點：
    - 群組標題使用 <span>
    - 子項目直接跟隨在群組標題之後（沒有巢狀 <ol>）
    - 需要根據位置關係重建階層

    Args:
        nav_toc: BeautifulSoup nav element
        nav_basedir: 基礎目錄路徑

    Returns:
        List[Dict]: 重建的階層結構
    """
    list_items = nav_toc.find_all("li")
    hierarchical_nodes = []
    current_group = None
    processed_items = set()  # 避免重複處理

    for i, item in enumerate(list_items):
        if i in processed_items:
            continue

        # 檢查是否為群組標題
        span_tag = item.find("span")
        if span_tag:
            # 創建新群組
            group_title = " ".join(span_tag.text.strip().split())
            current_group = {
                "type": "group",
                "title": group_title,
                "children": [],
                "expanded": False
            }
            hierarchical_nodes.append(current_group)

            # 查找後續屬於此群組的項目
            group_items = []
            for j in range(i + 1, len(list_items)):
                next_item = list_items[j]
                next_span = next_item.find("span")
                next_link = next_item.find("a")

                # 如果遇到下一個 <span> 或到達結尾，停止
                if next_span:
                    break

                # 如果是 <a> 鏈接，加入到當前群組
                if next_link:
                    chapter_node = {
                        "type": "chapter",
                        "title": " ".join(next_link.text.strip().split()),
                        "src": os.path.normpath(os.path.join(
                            nav_basedir,
                            next_link.get("href", "").split("#")[0]
                        )),
                        "normalized_src": normalize_src_for_matching(
                            next_link.get("href", "")
                        )
                    }
                    if current_group:
                        current_group["children"].append(chapter_node)
                    processed_items.add(j)

        # 如果是獨立的鏈接項目（沒有前面的 <span>）
        elif item.find("a"):
            link_node = parse_nav_item_recursive(item, nav_basedir)
            if link_node:
                hierarchical_nodes.append(link_node)

    return hierarchical_nodes


def parse_nav_document_robust(
    reader: ContentReader, nav_href: str
) -> List[Dict[str, Any]]:
    """
    Parse EPUB3 navigation document with support for nested structures.

    增強版本：支援多種 TOC 結構，包括扁平化群組結構的應變處理。

    Args:
        reader: Content reader interface for accessing EPUB content
        nav_href: Path to the navigation document within the EPUB
    """
    if not HAS_BS4:
        logger.warning(
            "BeautifulSoup4 not found, cannot parse nav.xhtml. Skipping.")
        return []

    try:
        nav_content = reader.read_chapter(nav_href)
        nav_basedir = os.path.dirname(nav_href)
        nav_soup = BeautifulSoup(nav_content, "xml")

        # Look for the TOC navigation
        nav_toc = nav_soup.find("nav", attrs={"epub:type": "toc"})
        if not nav_toc:
            return []

        list_items = nav_toc.find_all("li")
        total_items = len(list_items)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                f"Found {total_items} <li> items in nav.xhtml - analyzing structure..."
            )

        # 檢測 TOC 結構類型
        structure_type = detect_toc_structure(nav_toc)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Detected TOC structure: {structure_type}")

        # 根據結構類型選擇解析策略
        if structure_type == "flat_grouped":
            # 扁平化群組結構：直接返回階層結構，跳過扁平化
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    "Using flat grouped parsing strategy - returning hierarchical structure directly")
            hierarchical_nodes = parse_flat_grouped_nav(nav_toc, nav_basedir)

            # 統計資訊
            chapter_count = 0
            group_count = 0

            def count_items(nodes):
                nonlocal chapter_count, group_count
                for node in nodes:
                    if node["type"] == "group":
                        group_count += 1
                        if "children" in node:
                            count_items(node["children"])
                    elif node["type"] == "chapter":
                        chapter_count += 1

            count_items(hierarchical_nodes)

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    f"TOC parsing complete: {chapter_count} chapters, "
                    f"{group_count} groups from {total_items} total items "
                    f"(structure: {structure_type})"
                )

            # 對於扁平化結構，直接返回階層結構，不進行扁平化
            return hierarchical_nodes
        else:
            # 標準巢狀結構或其他：使用原有邏輯
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    f"Using standard parsing strategy for {structure_type}")
            hierarchical_nodes = []
            processed_chapters = set()

            for item in list_items:
                node = parse_nav_item_recursive(item, nav_basedir)
                if node:
                    # Handle groups: add their children to processed set to prevent duplicates
                    if node["type"] == "group" and "children" in node:
                        for child in node["children"]:
                            if child["type"] == "chapter":
                                child_key = (child.get("src"),
                                             child.get("title"))
                                processed_chapters.add(child_key)
                                if logger.isEnabledFor(logging.DEBUG):
                                    logger.debug(
                                        f"Added group child to processed: {child.get('title')}")

                    # Skip duplicate standalone chapters
                    elif node["type"] == "chapter":
                        chapter_key = (node.get("src"), node.get("title"))
                        if chapter_key in processed_chapters:
                            if logger.isEnabledFor(logging.DEBUG):
                                logger.debug(
                                    f"Skipping duplicate chapter: {node.get('title')}")
                            continue
                        processed_chapters.add(chapter_key)

                    hierarchical_nodes.append(node)

            # 統計資訊
            chapter_count = 0
            group_count = 0

            def count_items(nodes):
                nonlocal chapter_count, group_count
                for node in nodes:
                    if node["type"] == "group":
                        group_count += 1
                        if "children" in node:
                            count_items(node["children"])
                    elif node["type"] == "chapter":
                        chapter_count += 1

            count_items(hierarchical_nodes)

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    f"TOC parsing complete: {chapter_count} chapters, "
                    f"{group_count} groups from {total_items} total items "
                    f"(structure: {structure_type})"
                )

            # Return flattened structure for backward compatibility
            return flatten_nav_structure(hierarchical_nodes)

    except Exception as e:
        if reader.trace:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Failed to parse nav document {nav_href}: {e}")
        return []


def parse_ncx_document_robust(
    reader: ContentReader, ncx_href: str, basedir: str
) -> List[Dict[str, Any]]:
    """
    Parse EPUB2 NCX document with proper hierarchical structure.
    Return nested node structure with children attributes directly.

    Args:
        reader: Content reader interface for accessing EPUB content
        ncx_href: Path to the NCX document within the EPUB
        basedir: Base directory for resolving relative paths
    """
    try:
        ncx_content = reader.read_chapter(ncx_href)

        if HAS_BS4:
            ncx_soup = BeautifulSoup(ncx_content, "xml")
            # Only find root-level navPoint elements (direct children of navMap)
            nav_map = ncx_soup.find("navMap")
            if not nav_map:
                return []

            root_nav_points = nav_map.find_all("navPoint", recursive=False)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    f"Found {len(root_nav_points)} root <navPoint> items in toc.ncx"
                )

            # Define a regex pattern to match volume titles like "第X卷" or "Volume X"
            volume_pattern = re.compile(r"^(第.*卷|volume\s*\d+)", re.IGNORECASE)

            # Summary counters for less verbose logging
            total_chapters = 0
            total_groups = 0

            # Recursive function to process each navPoint and its children, returning nested structure
            def parse_nav_point_recursive(nav_point, depth=0):
                """Recursively parse navPoint, returning nested node structure"""
                nonlocal total_chapters, total_groups

                content_tag = nav_point.find("content", recursive=False)
                nav_label = nav_point.find("navLabel", recursive=False)

                if not content_tag or not nav_label:
                    return None

                # Keep full href including fragment for anchor support
                full_src = content_tag.get("src", "")
                full_path = os.path.normpath(os.path.join(basedir, full_src))
                # Don't split on "#" - keep the full href for anchor support
                title = " ".join(nav_label.text.strip().split())

                # Check if there are child nodes
                child_nav_points = nav_point.find_all(
                    "navPoint", recursive=False)

                if child_nav_points:
                    # This is a group node (has children)
                    total_groups += 1
                    children = []
                    for child in child_nav_points:
                        child_node = parse_nav_point_recursive(
                            child, depth + 1)
                        if child_node:
                            children.append(child_node)

                    return {
                        "type": "group",
                        "title": title,
                        "src": full_path,
                        "expanded": False,
                        "children": children,
                    }
                else:
                    # This is a leaf node (chapter)
                    total_chapters += 1
                    return {
                        "type": "chapter",
                        "title": title,
                        "src": full_path,
                    }

            # Start recursive parsing from root level, return nested results
            nodes = []
            for nav_point in root_nav_points:
                node = parse_nav_point_recursive(nav_point, depth=0)
                if node:
                    nodes.append(node)

            # Post-processing: assign non-volume chapters to the nearest volume group
            processed_nodes = []
            current_group = None

            for node in nodes:
                if node["type"] == "group":
                    # This is a volume group
                    current_group = node
                    processed_nodes.append(node)
                else:
                    # This is a chapter
                    if current_group:
                        # Add chapter to current group
                        current_group["children"].append(node)
                    else:
                        # If no current group, add to top level
                        processed_nodes.append(node)

            # Summary logging for NCX parsing
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    f"NCX parsing complete: {total_chapters} chapters, "
                    f"{total_groups} groups from {len(root_nav_points)} root navPoints"
                )

            return processed_nodes
        else:
            logger.warning(
                "BeautifulSoup4 not available. NCX parsing will be limited.")
            return []

    except Exception as e:
        if reader.trace:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Failed to parse NCX document {ncx_href}: {e}")
        return []


def parse_landmarks(reader: ContentReader, nav_href: str) -> List[Dict[str, Any]]:
    """
    Parse EPUB3 landmarks from navigation document (enhanced from foliate-js approach)

    Args:
        reader: Content reader interface for accessing EPUB content
        nav_href: Path to the navigation document within the EPUB

    Returns:
        List of landmark entries with type and href information
    """
    if not HAS_BS4:
        logger.warning(
            "BeautifulSoup4 not found, cannot parse landmarks. Skipping.")
        return []

    try:
        nav_content = reader.read_chapter(nav_href)
        nav_basedir = os.path.dirname(nav_href)
        nav_soup = BeautifulSoup(nav_content, "xml")

        # Look for landmarks navigation
        landmarks_nav = nav_soup.find("nav", attrs={"epub:type": "landmarks"})
        if not landmarks_nav:
            return []

        landmarks = []
        list_items = landmarks_nav.find_all("li")

        for item in list_items:
            a_tag = item.find("a")
            if a_tag:
                href = a_tag.get("href")
                if href:
                    # Resolve href relative to the nav document
                    full_path = os.path.normpath(
                        os.path.join(nav_basedir, str(href)))
                    title = " ".join(a_tag.text.strip().split())

                    # Extract epub:type from the link
                    epub_type_attr = a_tag.get("epub:type") or ""
                    epub_type = str(epub_type_attr).split()

                    landmarks.append({
                        "type": epub_type,
                        "title": title,
                        "href": full_path,
                    })

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Parsed {len(landmarks)} landmarks from nav.xhtml")

        return landmarks

    except Exception as e:
        if reader.trace:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Failed to parse landmarks from {nav_href}: {e}")
        return []


def parse_page_list(reader: ContentReader, nav_href: str) -> List[Dict[str, Any]]:
    """
    Parse EPUB3 page-list from navigation document (enhanced from foliate-js approach)

    Args:
        reader: Content reader interface for accessing EPUB content
        nav_href: Path to the navigation document within the EPUB

    Returns:
        List of page entries with title and href information
    """
    if not HAS_BS4:
        logger.warning(
            "BeautifulSoup4 not found, cannot parse page-list. Skipping.")
        return []

    try:
        nav_content = reader.read_chapter(nav_href)
        nav_basedir = os.path.dirname(nav_href)
        nav_soup = BeautifulSoup(nav_content, "xml")

        # Look for page-list navigation
        page_list_nav = nav_soup.find("nav", attrs={"epub:type": "page-list"})
        if not page_list_nav:
            return []

        pages = []
        list_items = page_list_nav.find_all("li")

        for item in list_items:
            a_tag = item.find("a")
            if a_tag:
                href = a_tag.get("href")
                if href:
                    # Resolve href relative to the nav document
                    full_path = os.path.normpath(
                        os.path.join(nav_basedir, str(href)))
                    title = " ".join(a_tag.text.strip().split())

                    pages.append({
                        "title": title,
                        "href": full_path,
                    })

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                f"Parsed {len(pages)} pages from page-list in nav.xhtml")

        return pages

    except Exception as e:
        if reader.trace:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Failed to parse page-list from {nav_href}: {e}")
        return []
