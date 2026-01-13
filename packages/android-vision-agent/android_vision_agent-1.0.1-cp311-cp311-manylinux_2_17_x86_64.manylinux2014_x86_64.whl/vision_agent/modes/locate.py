"""Locate mode - Find UI elements using vision."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from vision_agent.modes.llmclient import LlmClient
from vision_agent.utils.image import annotate_image, encode_image


def _build_image_messages(
    image_paths: list[str], image_quality: int, resize_factor: float
) -> tuple[list[dict[str, Any]], list[tuple[int, int]]]:
    messages: list[dict[str, Any]] = []
    dimensions: list[tuple[int, int]] = []

    for path in image_paths:
        b64, width, height = encode_image(
            path, quality=image_quality, resize_factor=resize_factor
        )
        dimensions.append((width, height))
        messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Screenshot (page={len(messages) + 1}):"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                ],
            }
        )

    return messages, dimensions


def _extract_tool_args(response, tool_name: str) -> dict[str, Any]:
    if not response.choices:
        raise ValueError("Empty LLM response")
    message = response.choices[0].message
    tool_calls = message.tool_calls or []
    for call in tool_calls:
        if call.function.name == tool_name:
            return json.loads(call.function.arguments)
    raise ValueError(f"Tool call '{tool_name}' not found")


def locate_element(
    llm: LlmClient,
    prompt: str,
    image_paths: list[str],
    image_quality: int = 95,
    resize_factor: float = 1.0,
    output_dir: str | None = None,
) -> dict[str, Any]:
    tools = [
        {
            "type": "function",
            "function": {
                "name": "return_target",
                "description": "Return the target element location for the user request.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "label": {"type": "string"},
                        "bounding_box": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "XYXY in 0-1000 relative coordinates.",
                        },
                        "confidence": {"type": "number"},
                        "page": {"type": "integer"},
                    },
                    "required": ["label", "bounding_box", "confidence", "page"],
                },
            },
        }
    ]

    system_text = (
        "Find the UI element for the user request. "
        "Return bounding_box as [x1,y1,x2,y2] in 0-1000 relative coordinates."
    )

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": [{"type": "text", "text": system_text}]},
        {"role": "user", "content": [{"type": "text", "text": f"User request: {prompt}"}]},
    ]

    image_messages, image_dimensions = _build_image_messages(
        image_paths, image_quality, resize_factor
    )
    messages.extend(image_messages)

    response = llm.chat(
        messages=messages,
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "return_target"}},
        temperature=0.1,
    )

    result = _extract_tool_args(response, "return_target")
    result["image_dimensions"] = image_dimensions
    result["mode"] = "locate"

    if output_dir:
        bounding_box = result.get("bounding_box", [])
        if isinstance(bounding_box, list) and len(bounding_box) == 4:
            page = max(1, int(result.get("page", 1)))
            page_idx = min(page - 1, max(0, len(image_paths) - 1))
            if page_idx < len(image_dimensions):
                width, height = image_dimensions[page_idx]
                try:
                    annotated_path = annotate_image(
                        image_paths[page_idx], bounding_box, width, height, output_dir
                    )
                    result["annotated_image_path"] = annotated_path
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
    **kwargs,
) -> dict[str, Any]:
    """Locate UI element in images."""
    from vision_agent.utils.image import capture_screenshot_to_file

    if not image_paths:
        image_path, device_id = capture_screenshot_to_file(
            device_id, output_dir, display_id=display_id
        )
        image_paths = [image_path]

    return locate_element(llm, prompt=prompt, image_paths=image_paths, output_dir=output_dir)
