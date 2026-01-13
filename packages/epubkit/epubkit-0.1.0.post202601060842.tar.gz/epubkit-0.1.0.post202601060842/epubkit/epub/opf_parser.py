#!/usr/bin/env python3
"""
OPF parser for EPUB files.

This module is responsible for parsing the OPF (Open Packaging Format) file,
which contains metadata, manifest, and spine information for an EPUB book.
"""

import logging
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple, Any, Optional

# Try to import BeautifulSoup for HTML parsing, fallback if not available
try:
    from bs4 import BeautifulSoup

    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

logger = logging.getLogger(__name__)


def parse_opf(opf_bytes: bytes, basedir: str) -> Tuple[Dict, List[str], str, str, Dict[str, Any]]:
    """
    Parses the OPF file to extract the manifest, spine, ncx, navdoc, and layout properties.

    Args:
        opf_bytes: The content of the OPF file as bytes.
        basedir: The base directory of the OPF file.

    Returns:
        A tuple containing:
        - manifest: A dictionary mapping item IDs to their details.
        - spine_order: A list of hrefs in the order they appear in the spine.
        - ncx: The href of the NCX file, or None.
        - navdoc: The href of the navigation document, or None.
        - layout_properties: A dictionary of layout-related properties.
    """
    manifest: Dict[str, Dict] = {}
    spine_order: List[str] = []
    ncx: str = ""
    navdoc: str = ""
    layout_properties: Dict[str, Any] = {}

    if HAS_BS4:
        opf = BeautifulSoup(opf_bytes, "xml")
        manifest, spine_order, ncx, navdoc = _parse_opf_bs4(opf, basedir)
    else:
        root = ET.fromstring(opf_bytes)
        manifest, spine_order, ncx, navdoc = _parse_opf_et(root, basedir)

    # Parse layout properties from epub.js approach
    if HAS_BS4:
        layout_properties = _parse_layout_properties_bs4(opf)
    else:
        layout_properties = _parse_layout_properties_et(root)

    logger.debug(f"Successfully parsed spine with {len(spine_order)} items.")
    return manifest, spine_order, ncx, navdoc, layout_properties


def _parse_opf_bs4(opf, basedir: str) -> Tuple[Dict, List[str], str, str]:
    """Parse OPF using BeautifulSoup"""
    manifest: Dict[str, Dict] = {}
    spine_order: List[str] = []
    ncx: str = ""
    navdoc: str = ""

    # Extract manifest
    manifest_elem = opf.find("manifest")
    if manifest_elem:
        for item in manifest_elem.find_all("item"):
            attrs = dict(item.attrs)
            href = f"{basedir}{attrs.get('href', '')}"
            item_id = attrs.get("id")
            media_type = attrs.get("media-type", "")
            properties = attrs.get("properties", "")

            if item_id:
                manifest[item_id] = {
                    "href": href,
                    "media_type": media_type,
                    "properties": properties,
                }

            # Look for NCX and nav documents
            if media_type == "application/x-dtbncx+xml":
                ncx = href
                logger.debug(f"Found NCX file reference: {ncx}")
            elif properties == "nav":
                navdoc = href
                logger.debug(f"Found NAV document reference: {navdoc}")

    # Extract spine
    spine_elem = opf.find("spine")
    if spine_elem:
        spine_items = spine_elem.find_all("itemref")
        spine_order = [
            manifest[i["idref"]]["href"]
            for i in spine_items
            if i.get("idref") in manifest
        ]

    return manifest, spine_order, ncx, navdoc


def _parse_opf_et(root, basedir: str) -> Tuple[Dict, List[str], str, str]:
    """Parse OPF using ElementTree"""
    manifest: Dict[str, Dict] = {}
    spine_order: List[str] = []
    ncx: str = ""
    navdoc: str = ""

    # Extract manifest
    manifest_elem = root.find(
        ".//{http://www.idpf.org/2007/opf}manifest"
    ) or root.find(".//manifest")
    if manifest_elem is not None:
        for item in manifest_elem.findall(
            "{http://www.idpf.org/2007/opf}item"
        ) or manifest_elem.findall("item"):
            item_id = item.attrib.get("id")
            href = item.attrib.get("href")
            media_type = item.attrib.get("media-type", "")
            properties = item.attrib.get("properties", "")

            if item_id and href:
                full_href = f"{basedir}{href}"
                manifest[item_id] = {
                    "href": full_href,
                    "media_type": media_type,
                    "properties": properties,
                }

                if media_type == "application/x-dtbncx+xml":
                    ncx = full_href
                elif properties == "nav":
                    navdoc = full_href

    # Extract spine
    spine = root.find(".//{http://www.idpf.org/2007/opf}spine") or root.find(
        ".//spine"
    )
    if spine is not None:
        for itemref in spine.findall(
            "{http://www.idpf.org/2007/opf}itemref"
        ) or spine.findall("itemref"):
            idref = itemref.attrib.get("idref")
            if idref and idref in manifest:
                spine_order.append(manifest[idref]["href"])

    return manifest, spine_order, ncx, navdoc


def parse_spine_items(opf_bytes: bytes, basedir: str, manifest: Dict) -> List[Dict[str, Any]]:
    """Parse spine items with enhanced properties (from epub.js approach)"""
    # Use dict-based approach for better compatibility
    spine_items = []

    if HAS_BS4:
        opf = BeautifulSoup(opf_bytes, "xml")
        spine_elem = opf.find("spine")
        if spine_elem:
            for itemref in spine_elem.find_all("itemref"):
                idref = itemref.get("idref")
                if idref and idref in manifest:
                    linear = itemref.get("linear", "yes") == "yes"
                    properties_str = itemref.get("properties") or ""
                    properties = properties_str.split() if properties_str else []

                    spine_items.append({
                        "href": manifest[idref]["href"],
                        "idref": idref,
                        "linear": linear,
                        "properties": properties
                    })
    else:
        root = ET.fromstring(opf_bytes)
        spine = root.find(".//{http://www.idpf.org/2007/opf}spine") or root.find(".//spine")
        if spine is not None:
            for itemref in spine.findall(
                "{http://www.idpf.org/2007/opf}itemref"
            ) or spine.findall("itemref"):
                idref = itemref.attrib.get("idref")
                if idref and idref in manifest:
                    linear = itemref.attrib.get("linear", "yes") == "yes"
                    properties_str = itemref.attrib.get("properties") or ""
                    properties = properties_str.split() if properties_str else []

                    spine_items.append({
                        "href": manifest[idref]["href"],
                        "idref": idref,
                        "linear": linear,
                        "properties": properties
                    })

    return spine_items


def _parse_layout_properties_bs4(opf) -> Dict[str, Any]:
    """Parse layout properties using BeautifulSoup (enhanced from epub.js approach)"""
    properties = {}

    # rendition:layout
    layout = _get_property_text_bs4(opf, "rendition:layout")
    if layout:
        properties["layout"] = layout

    # rendition:flow
    flow = _get_property_text_bs4(opf, "rendition:flow")
    if flow:
        properties["flow"] = flow

    # rendition:orientation
    orientation = _get_property_text_bs4(opf, "rendition:orientation")
    if orientation:
        properties["orientation"] = orientation

    # rendition:spread
    spread = _get_property_text_bs4(opf, "rendition:spread")
    if spread:
        properties["spread"] = spread

    # rendition:viewport (for fixed-layout)
    viewport = _get_property_text_bs4(opf, "rendition:viewport")
    if viewport:
        properties["viewport"] = viewport

    # media:duration (for media overlays)
    duration = _get_property_text_bs4(opf, "media:duration")
    if duration:
        properties["duration"] = duration

    # media:narrator (for accessibility)
    narrator = _get_property_text_bs4(opf, "media:narrator")
    if narrator:
        properties["narrator"] = narrator

    # page-progression-direction
    spine_elem = opf.find("spine")
    if spine_elem and spine_elem.get("page-progression-direction"):
        properties["page_progression_direction"] = spine_elem.get("page-progression-direction")

    return properties


def _parse_layout_properties_et(root) -> Dict[str, Any]:
    """Parse layout properties using ElementTree (enhanced fallback)"""
    properties = {}

    # rendition:layout
    layout = _get_property_text_et(root, "rendition:layout")
    if layout:
        properties["layout"] = layout

    # rendition:flow
    flow = _get_property_text_et(root, "rendition:flow")
    if flow:
        properties["flow"] = flow

    # rendition:orientation
    orientation = _get_property_text_et(root, "rendition:orientation")
    if orientation:
        properties["orientation"] = orientation

    # rendition:spread
    spread = _get_property_text_et(root, "rendition:spread")
    if spread:
        properties["spread"] = spread

    # rendition:viewport (for fixed-layout)
    viewport = _get_property_text_et(root, "rendition:viewport")
    if viewport:
        properties["viewport"] = viewport

    # media:duration (for media overlays)
    duration = _get_property_text_et(root, "media:duration")
    if duration:
        properties["duration"] = duration

    # media:narrator (for accessibility)
    narrator = _get_property_text_et(root, "media:narrator")
    if narrator:
        properties["narrator"] = narrator

    # page-progression-direction
    spine = root.find(".//{http://www.idpf.org/2007/opf}spine") or root.find(".//spine")
    if spine is not None and spine.attrib.get("page-progression-direction"):
        properties["page_progression_direction"] = spine.attrib.get("page-progression-direction")

    return properties


def _get_property_text_bs4(opf, property_name: str) -> str:
    """Get property text using BeautifulSoup"""
    meta = opf.find("meta", {"property": property_name})
    if meta and meta.get("content"):
        return meta.get("content")
    return ""


def _get_property_text_et(root, property_name: str) -> str:
    """Get property text using ElementTree"""
    for meta in root.findall(".//{http://www.idpf.org/2007/opf}meta") or root.findall(".//meta"):
        if meta.attrib.get("property") == property_name and meta.attrib.get("content"):
            return meta.attrib.get("content")
    return ""
