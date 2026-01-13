"""XML parsing helpers for Android UI hierarchy."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Optional


def parse_bounds(bounds_str: str) -> Optional[tuple[int, int, int, int]]:
    """Parse bounds like "[x1,y1][x2,y2]" to (x1, y1, x2, y2)."""
    matches = re.findall(r"\[(\d+),(\d+)\]", bounds_str)
    if len(matches) != 2:
        return None
    x1, y1 = int(matches[0][0]), int(matches[0][1])
    x2, y2 = int(matches[1][0]), int(matches[1][1])
    return (x1, y1, x2, y2)


def parse_hierarchy_xml_json(xml_text: str) -> dict[str, list[dict]]:
    """Parse XML hierarchy into a JSON structure grouped by display-id."""
    root = ET.fromstring(xml_text)
    nodes_by_display: dict[str, list[dict]] = {}

    def extract_node(element):
        attrs = dict(element.attrib)
        display_id = attrs.get("display-id", "0")
        
        if display_id not in nodes_by_display:
            nodes_by_display[display_id] = []
        
        nodes_by_display[display_id].append(attrs)
        for child in element:
            extract_node(child)

    for child in root:
        extract_node(child)

    return nodes_by_display


def find_nodes_by_center_point(
    nodes_json: dict[str, list[dict]], 
    center_x: int, 
    center_y: int, 
    display_id: str = "0"
) -> dict | None:
    """Find the smallest node containing the center point in the specified display."""
    if display_id not in nodes_json:
        return None
    
    nodes = nodes_json[display_id]
    matching_nodes = []

    for node in nodes:
        bounds_str = node.get("bounds", "")
        bounds_parsed = parse_bounds(bounds_str)
        if not bounds_parsed:
            continue

        x1, y1, x2, y2 = bounds_parsed
        if x1 <= center_x <= x2 and y1 <= center_y <= y2:
            matching_nodes.append(node)

    if not matching_nodes:
        return None

    matching_nodes.sort(key=lambda n: (
        (parse_bounds(n["bounds"])[2] - parse_bounds(n["bounds"])[0]) *
        (parse_bounds(n["bounds"])[3] - parse_bounds(n["bounds"])[1])
    ))

    return matching_nodes[0]

