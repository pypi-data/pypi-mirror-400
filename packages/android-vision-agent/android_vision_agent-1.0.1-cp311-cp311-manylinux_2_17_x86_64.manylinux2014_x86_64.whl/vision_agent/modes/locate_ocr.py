"""Locate-OCR mode - Extract text with bounding boxes."""

from __future__ import annotations

import re
from typing import Any

from vision_agent.modes.llmclient import LlmClient
from vision_agent.utils.image import capture_screenshot_to_file
from vision_agent.modes.locate import _build_image_messages, _extract_tool_args
from vision_agent.utils.image import annotate_image_multi


def _normalize_label(text: str) -> str:
    return re.sub(r"\s+", "", str(text)).strip().lower()


def _extract_anchor_label(prompt: str) -> str | None:
    patterns = [
        r"(?:找到|查找|寻找|获取|定位)?\s*([A-Za-z0-9_-]+)\s*对应",
        r"\bfor\s+([A-Za-z0-9_-]+)\b",
        r"\bof\s+([A-Za-z0-9_-]+)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, prompt, flags=re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def _filter_items_for_anchor(
    items: list[dict[str, Any]],
    anchor_label: str,
) -> list[dict[str, Any]]:
    label = _normalize_label(anchor_label)
    anchor_candidates = [
        item
        for item in items
        if _normalize_label(item.get("text", "")) == label
    ]
    if not anchor_candidates:
        return []
    anchor = max(
        anchor_candidates,
        key=lambda item: float(item.get("confidence", 0.0) or 0.0),
    )
    box = anchor.get("bounding_box", [])
    if (
        not isinstance(box, list)
        or len(box) != 4
        or not all(isinstance(value, (int, float)) for value in box)
    ):
        return []
    anchor_y1, anchor_y2 = float(box[1]), float(box[3])
    anchor_center_y = (anchor_y1 + anchor_y2) / 2.0
    anchor_height = abs(anchor_y2 - anchor_y1)
    threshold = max(anchor_height * 1.5, 12.0)
    anchor_page = int(anchor.get("page", 1) or 1)

    filtered: list[dict[str, Any]] = []
    for item in items:
        if int(item.get("page", 1) or 1) != anchor_page:
            continue
        item_box = item.get("bounding_box", [])
        if (
            not isinstance(item_box, list)
            or len(item_box) != 4
            or not all(isinstance(value, (int, float)) for value in item_box)
        ):
            continue
        item_center_y = (float(item_box[1]) + float(item_box[3])) / 2.0
        if abs(item_center_y - anchor_center_y) <= threshold:
            filtered.append(item)

    return filtered


def locate_ocr_text(
    llm: LlmClient,
    prompt: str,
    image_paths: list[str],
    image_quality: int = 95,
    resize_factor: float = 1.0,
    output_dir: str | None = None,
    *,
    lang: str = "cn",
) -> dict[str, Any]:
    tools = [
        {
            "type": "function",
            "function": {
                "name": "return_text_bboxes",
                "description": (
                    "Return all extracted values (copied from the screenshot) and their bounding boxes. "
                    "If there are multiple matches, return them all; if none, return an empty list."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "items": {
                            "type": "array",
                            "description": (
                                "List of extracted values and their bounding boxes in reading order "
                                "(top-to-bottom, left-to-right). Return [] if no match."
                            ),
                            "items": {
                                "type": "object",
                                "properties": {
                                    "text": {
                                        "type": "string",
                                        "description": (
                                            "Copy the value from the screenshot verbatim. "
                                            "Do not add any extra words."
                                        ),
                                    },
                                    "bounding_box": {
                                        "type": "array",
                                        "items": {"type": "number"},
                                        "description": "XYXY in 0-1000 relative coordinates.",
                                    },
                                    "confidence": {"type": "number"},
                                    "page": {"type": "integer"},
                                },
                                "required": ["text", "bounding_box", "confidence", "page"],
                            },
                        },
                    },
                    "required": ["items"],
                },
            },
        }
    ]

    system_text = (
        "You are an OCR locator. Find the requested text on the screenshot.\n"
        "Rules:\n"
        "- Return a JSON tool call with an `items` array.\n"
        "- Each item is one matching value copied from the screenshot, with its `bounding_box`.\n"
        "- If multiple matches exist, include them all in reading order (top-to-bottom, left-to-right).\n"
        "- If nothing matches, return `items`: [] (empty list).\n"
        "- If the request references a specific key/row label (e.g., \"NGX\"), include that label as an item with its "
        "bounding_box so row alignment can be verified.\n"
        "- Do not add any extra words like \"not found\" or \"empty\".\n"
    )
    if lang != "en":
        system_text = (
            "你是 OCR 文本定位器：在截图中找到用户要的文字和值。\n"
            "规则：\n"
            "- 返回一个包含 `items` 数组的 JSON tool call。\n"
            "- 每个 item 必须包含：`text`（截图中真实可见原文，逐字抄写）、`bounding_box`（0-1000 相对坐标，XYXY）、`confidence`、`page`。\n"
            "- 如果存在多个匹配，按从上到下、从左到右的阅读顺序全部返回。\n"
            "- 如果没有任何匹配，返回 `items`: []（空数组）。\n"
            "- 如果请求包含特定的关键标识/行名（例如'NGX对应...'），请把该标识及其 bounding_box 也作为一条 item 返回，便于做行对齐校验。\n"
            "- 不要输出任何额外解释（例如'为空/不存在/未找到/无/N/A'等）。\n"
        )

    request_label = "User request" if lang == "en" else "用户请求"
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": [{"type": "text", "text": system_text}]},
        {"role": "user", "content": [{"type": "text", "text": f"{request_label}: {prompt}"}]},
    ]

    image_messages, image_dimensions = _build_image_messages(
        image_paths, image_quality, resize_factor
    )
    messages.extend(image_messages)

    response = llm.chat(
        messages=messages,
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "return_text_bboxes"}},
        temperature=0.0,
    )

    args = _extract_tool_args(response, "return_text_bboxes")

    pages: list[dict[str, Any]] = []
    for idx, (width, height) in enumerate(image_dimensions):
        page = idx + 1
        page_path = image_paths[idx] if idx < len(image_paths) else ""
        pages.append(
            {
                "page": page,
                "image_path": page_path,
                "image_dimensions": [width, height],
            }
        )

    raw_items = args.get("items", [])
    items: list[dict[str, Any]] = []
    if isinstance(raw_items, list):
        for raw_item in raw_items:
            if not isinstance(raw_item, dict):
                continue
            text = str(raw_item.get("text", "") or "")
            if not text.strip():
                continue
            bounding_box = raw_item.get("bounding_box", [0, 0, 0, 0])
            if (
                not isinstance(bounding_box, list)
                or len(bounding_box) != 4
                or not all(isinstance(value, (int, float)) for value in bounding_box)
            ):
                continue
            if all(float(value) == 0.0 for value in bounding_box):
                continue
            page = max(1, int(raw_item.get("page", 1)))
            page = min(page, max(1, len(image_paths)))
            confidence = float(raw_item.get("confidence", 0.0) or 0.0)
            items.append(
                {
                    "text": text,
                    "bounding_box": bounding_box,
                    "confidence": confidence,
                    "page": page,
                }
            )

    items.sort(
        key=lambda item: (
            int(item.get("page", 1)),
            float(item.get("bounding_box", [0, 0, 0, 0])[1]),
            float(item.get("bounding_box", [0, 0, 0, 0])[0]),
        )
    )

    anchor_label = _extract_anchor_label(prompt)
    if anchor_label:
        filtered_items = _filter_items_for_anchor(items, anchor_label)
        if filtered_items:
            items = filtered_items
            anchor_norm = _normalize_label(anchor_label)
            items = [
                item
                for item in items
                if _normalize_label(item.get("text", "")) != anchor_norm
            ]
        else:
            items = []

    combined_text = "\n".join(item["text"] for item in items)
    result: dict[str, Any] = {
        "mode": "locate-ocr",
        "text": combined_text,
        "pages": pages,
        "items": items,
    }

    if output_dir:
        try:
            boxes_by_page_idx: dict[int, list[list[int]]] = {}
            for item in items:
                item_page = max(1, int(item.get("page", 1)))
                item_page_idx = min(item_page - 1, max(0, len(image_paths) - 1))
                item_box = item.get("bounding_box", [])
                if isinstance(item_box, list) and len(item_box) == 4:
                    boxes_by_page_idx.setdefault(item_page_idx, []).append(item_box)

            annotated_images: list[dict[str, Any]] = []
            for item_page_idx in sorted(boxes_by_page_idx):
                page_width, page_height = image_dimensions[item_page_idx]
                annotated_path = annotate_image_multi(
                    image_paths[item_page_idx],
                    boxes_by_page_idx[item_page_idx],
                    page_width,
                    page_height,
                    output_dir,
                    suffix=f"locate-ocr-p{item_page_idx + 1}",
                )
                annotated_images.append(
                    {
                        "page": item_page_idx + 1,
                        "annotated_image_path": annotated_path,
                    }
                )

            if annotated_images:
                result["annotated_images"] = annotated_images
        except (FileNotFoundError, OSError):
            pass

    return result


def run(
    llm: LlmClient,
    prompt: str,
    image_paths: list[str],
    device_id: str | None = None,
    display_id: int | None = None,
    output_dir: str = "outputs",
    lang: str = "cn",
    **kwargs,
) -> dict[str, Any]:
    """Extract text with bounding boxes using OCR."""
    if not image_paths:
        image_path, device_id = capture_screenshot_to_file(
            device_id, output_dir, display_id=display_id
        )
        image_paths = [image_path]

    return locate_ocr_text(
        llm, prompt=prompt, image_paths=image_paths, lang=lang, output_dir=output_dir
    )
