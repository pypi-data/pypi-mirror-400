"""Action mode - Execute single device action."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from vision_agent.utils.action_executor import ActionHandler
from vision_agent.device.adb.devices import list_devices
from vision_agent.device.adb.apps import get_current_app
from vision_agent.device.adb.screenshot import get_screenshot
from vision_agent.modes.llmclient import LlmClient
from vision_agent.utils.image import base64_to_image_bytes


def _ensure_device(device_id: str | None) -> None:
    devices = list_devices()
    if not devices:
        raise RuntimeError("No ADB devices detected")
    if device_id is None:
        return
    if not any(d.device_id == device_id for d in devices):
        raise RuntimeError(f"Device not found: {device_id}")


def _save_screenshot(base64_data: str, output_dir: str) -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    path = Path(output_dir) / f"screenshot_{timestamp}.png"
    path.write_bytes(base64_to_image_bytes(base64_data))
    return str(path)


def _normalize_action(action_name: str) -> str:
    key = action_name.strip().lower().replace("_", " ")
    aliases = {
        "tap": "Tap",
        "click": "Tap",
        "double tap": "Double Tap",
        "doubletap": "Double Tap",
        "long press": "Long Press",
        "longpress": "Long Press",
        "swipe": "Swipe",
        "back": "Back",
        "home": "Home",
        "type": "Type",
        "type name": "Type_Name",
        "wait": "Wait",
        "screenshot": "Screenshot",
    }
    return aliases.get(key, action_name)


def run(
    llm: LlmClient,
    prompt: str,
    device_id: str | None,
    display_id: int | None,
    output_dir: str,
    **kwargs,
) -> dict[str, Any]:
    """Execute a single device action based on prompt."""
    _ensure_device(device_id)

    screenshot = get_screenshot(device_id, display_id=display_id)
    current_app = get_current_app(device_id, display_id=display_id)

    tools = [
        {
            "type": "function",
            "function": {
                "name": "perform_action",
                "description": "Choose a single device action to execute.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": (
                                "One of Tap, Swipe, Type, Back, Home, Long Press, "
                                "Double Tap, Wait, Screenshot."
                            ),
                        },
                        "element": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "XY coordinates in 0-1000 relative space.",
                        },
                        "start": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "Swipe start XY in 0-1000 relative space.",
                        },
                        "end": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "Swipe end XY in 0-1000 relative space.",
                        },
                        "text": {"type": "string"},
                        "duration": {"type": "number", "description": "Seconds to wait."},
                    },
                    "required": ["action"],
                },
            },
        }
    ]

    system_text = (
        "Decide one device action to satisfy the request. "
        "Coordinates use 0-1000 relative space."
    )

    display_id_for_log = display_id if display_id is not None else 0
    screen_info = json.dumps(
        {"current_app": current_app, "display_id": display_id_for_log},
        ensure_ascii=False,
    )
    messages = [
        {"role": "system", "content": [{"type": "text", "text": system_text}]},
        {"role": "user", "content": [{"type": "text", "text": f"User request: {prompt}"}]},
        {"role": "user", "content": [{"type": "text", "text": f"Screen info: {screen_info}"}]},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Current screen:"},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{screenshot.base64_data}"},
                },
            ],
        },
    ]

    response = llm.chat(
        messages=messages,
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "perform_action"}},
        temperature=0.1,
    )

    tool_call = response.choices[0].message.tool_calls[0]
    result = json.loads(tool_call.function.arguments)

    action_name = _normalize_action(result.get("action", ""))

    if action_name == "Screenshot":
        path = _save_screenshot(screenshot.base64_data, output_dir)
        return {"mode": "action", "action": "Screenshot", "success": True, "path": path}

    action: dict[str, Any] = {"_metadata": "do", "action": action_name}

    if action_name in {"Tap", "Double Tap", "Long Press"}:
        action["element"] = result.get("element", [0, 0])
    elif action_name == "Swipe":
        action["start"] = result.get("start", [0, 0])
        action["end"] = result.get("end", [0, 0])
    elif action_name in {"Type", "Type_Name"}:
        action["text"] = result.get("text", "")
    elif action_name == "Wait":
        duration = float(result.get("duration", 1.0))
        action["duration"] = f"{duration} seconds"
    elif action_name in {"Back", "Home"}:
        pass
    else:
        return {
            "mode": "action",
            "action": action_name,
            "success": False,
            "message": f"Unsupported action: {action_name}",
        }

    handler = ActionHandler(device_id=device_id, display_id=display_id)
    exec_result = handler.execute(action, screenshot.width, screenshot.height)

    return {
        "mode": "action",
        "action": action_name,
        "success": exec_result.success,
        "message": exec_result.message,
    }
