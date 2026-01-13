"""Locate-XML mode - Find UI elements using vision + XML hierarchy."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from vision_agent.modes.llmclient import LlmClient
from vision_agent.device.adb.ui_hierarchy import dump_ui_hierarchy
from vision_agent.utils.image import capture_screenshot_to_file
from vision_agent.modes.locate import locate_element
from vision_agent.utils.xml import find_nodes_by_center_point, parse_bounds, parse_hierarchy_xml_json
from vision_agent.utils.image import annotate_image, to_absolute_box


def run(
    llm: LlmClient,
    prompt: str,
    device_id: str | None = None,
    display_id: int | None = None,
    output_dir: str = "outputs",
    **kwargs,
) -> dict[str, Any]:
    """Locate element using vision + XML hierarchy."""
    image_path, device_id = capture_screenshot_to_file(device_id, output_dir, display_id=display_id)
    image_paths = [image_path]
    xml_text = dump_ui_hierarchy(device_id)

    nodes_json = parse_hierarchy_xml_json(xml_text)

    visual = locate_element(
        llm,
        prompt=prompt,
        image_paths=image_paths,
        image_quality=95,
        resize_factor=1.0,
        output_dir=None,
    )

    image_dimensions = visual.get("image_dimensions", [])
    page = max(1, int(visual.get("page", 1)))
    page_idx = min(page - 1, max(0, len(image_dimensions) - 1))

    width, height = image_dimensions[page_idx]
    visual_box = visual.get("bounding_box", [0, 0, 0, 0])
    x1, y1, x2, y2 = to_absolute_box(visual_box, width, height)
    center_x = int((x1 + x2) / 2)
    center_y = int((y1 + y2) / 2)

    display_id_str = str(display_id) if display_id is not None else "0"
    matched_node = find_nodes_by_center_point(
        nodes_json, center_x, center_y, display_id=display_id_str
    )

    if matched_node:
        result = dict(matched_node)
    else:
        result = {}

    result["mode"] = "locate-xml"

    if output_dir:
        if matched_node:
            node_bounds = parse_bounds(matched_node.get("bounds", ""))
            if node_bounds:
                x1, y1, x2, y2 = node_bounds
                node_box = [x1 * 1000 // width, y1 * 1000 // height, x2 * 1000 // width, y2 * 1000 // height]
                try:
                    annotated_path = annotate_image(
                        image_paths[page_idx], node_box, width, height, output_dir
                    )
                    result["annotated_image_path"] = annotated_path
                except (FileNotFoundError, OSError):
                    pass

        xml_path = Path(output_dir) / (Path(image_paths[0]).stem + "_locate-xml.xml")
        xml_path.write_text(xml_text, encoding="utf-8")
        result["xml_file_path"] = str(xml_path)

    return result
