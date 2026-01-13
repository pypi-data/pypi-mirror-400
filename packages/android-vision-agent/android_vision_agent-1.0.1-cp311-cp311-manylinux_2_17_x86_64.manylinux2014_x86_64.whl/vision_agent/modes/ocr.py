"""OCR mode - Extract text from images."""

from __future__ import annotations

import json
import re
from typing import Any

from vision_agent.modes.llmclient import LlmClient
from vision_agent.utils.image import capture_screenshot_to_file
from vision_agent.modes.locate import _build_image_messages, _extract_tool_args


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


def ocr_text(
    llm: LlmClient,
    prompt: str,
    image_paths: list[str],
    image_quality: int = 95,
    resize_factor: float = 1.0,
    *,
    lang: str = "cn",
) -> dict[str, Any]:
    # Check if this is an anchor-based query
    anchor_label = _extract_anchor_label(prompt)
    if anchor_label:
        # Use locate_ocr for anchor-based queries
        from vision_agent.modes.locate_ocr import locate_ocr_text
        locate_result = locate_ocr_text(
            llm,
            prompt=prompt,
            image_paths=image_paths,
            image_quality=image_quality,
            resize_factor=resize_factor,
            output_dir=None,
            lang=lang,
        )
        raw_items = locate_result.get("items", [])
        items: list[dict[str, Any]] = []
        if isinstance(raw_items, list):
            for raw_item in raw_items:
                if not isinstance(raw_item, dict):
                    continue
                text = str(raw_item.get("text", "") or "")
                if not text.strip():
                    continue
                confidence = float(raw_item.get("confidence", 0.0) or 0.0)
                page = max(1, int(raw_item.get("page", 1)))
                items.append(
                    {
                        "text": text,
                        "confidence": confidence,
                        "page": page,
                    }
                )

        combined_text = "\n".join(item["text"] for item in items)
        return {
            "mode": "ocr",
            "text": combined_text,
            "pages": locate_result.get("pages", []),
            "items": items,
        }

    tools = [
        {
            "type": "function",
            "function": {
                "name": "return_texts",
                "description": (
                    "Return all extracted values that satisfy the user request, copied from the screenshot. "
                    "If there are multiple matches, return them all; if none, return an empty list."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "items": {
                            "type": "array",
                            "description": (
                                "List of extracted values in reading order (top-to-bottom, left-to-right). "
                                "Return [] if no match."
                            ),
                            "items": {
                                "type": "object",
                                "properties": {
                                    "text": {
                                        "type": "string",
                                        "description": (
                                            "Copy the value from the screenshot verbatim. "
                                            "Do not add explanations like 'not found'/'为空'."
                                        ),
                                    },
                                    "confidence": {"type": "number"},
                                    "page": {"type": "integer"},
                                },
                                "required": ["text", "confidence", "page"],
                            },
                        },
                    },
                    "required": ["items"],
                },
            },
        }
    ]

    system_text = (
        "You are an OCR extractor. Copy text verbatim from the screenshot.\n"
        "Rules:\n"
        "- Return a JSON tool call with an `items` array.\n"
        "- Each item is one matching value copied from the screenshot.\n"
        "- If multiple matches exist, include them all in reading order (top-to-bottom, left-to-right).\n"
        "- If nothing matches, return `items`: [] (empty list).\n"
        "- If the request references a specific key/row label (e.g., \"NGX\"), include that label as an item so row "
        "alignment can be verified.\n"
        "- Do not infer, paraphrase, translate, or restate the question.\n"
        "- Never output phrases like \"not found\", \"empty\", \"N/A\", \"不存在\", \"未找到\", or \"为空\".\n"
    )
    if lang != "en":
        system_text = (
            "你是 OCR 文字抽取器：只能从截图中抄写文字，不做推理。\n"
            "规则：\n"
            "- 返回一个包含 `items` 数组的 JSON tool call。\n"
            "- 每个 item 表示一条匹配的结果：`text` 必须是截图中真实可见的原文，逐字抄写；不要改写/翻译/补充说明/复述问题。\n"
            "- 如果存在多个匹配，按从上到下、从左到右的阅读顺序全部返回。\n"
            "- 如果没有任何匹配，返回 `items`: []（空数组）。\n"
            "- 如果请求包含特定的关键标识/行名（例如'NGX对应...'），请把该标识也作为一条 item 返回，便于做行对齐校验。\n"
            "- 不要输出类似'为空/不存在/未找到/无/N/A'等解释句。\n"
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
        tool_choice={"type": "function", "function": {"name": "return_texts"}},
        temperature=0.0,
    )

    args = _extract_tool_args(response, "return_texts")

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
            page = max(1, int(raw_item.get("page", 1)))
            page = min(page, max(1, len(image_paths)))
            confidence = float(raw_item.get("confidence", 0.0) or 0.0)
            items.append(
                {
                    "text": text,
                    "confidence": confidence,
                    "page": page,
                }
            )

    anchor_label = _extract_anchor_label(prompt)
    if anchor_label:
        anchor_norm = _normalize_label(anchor_label)
        anchor_present = any(
            _normalize_label(item.get("text", "")) == anchor_norm for item in items
        )
        if not anchor_present:
            items = []
        else:
            items = [
                item
                for item in items
                if _normalize_label(item.get("text", "")) != anchor_norm
            ]

    combined_text = "\n".join(item["text"] for item in items)

    return {
        "mode": "ocr",
        "text": combined_text,
        "pages": pages,
        "items": items,
    }


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
    """Extract text from images using OCR."""
    if not image_paths:
        image_path, device_id = capture_screenshot_to_file(
            device_id, output_dir, display_id=display_id
        )
        image_paths = [image_path]

    return ocr_text(llm, prompt=prompt, image_paths=image_paths, lang=lang)
