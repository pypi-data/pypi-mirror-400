"""Image utilities for encoding and sizing."""

from __future__ import annotations

import base64
import io
import time
from pathlib import Path
from typing import Tuple

from PIL import Image


def encode_image(
    image_path: str, quality: int = 95, resize_factor: float = 1.0
) -> tuple[str, int, int]:
    """Encode image as base64 PNG and return original dimensions."""
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        orig_width, orig_height = img.size

        if resize_factor and resize_factor != 1.0:
            new_w = max(1, int(img.width * resize_factor))
            new_h = max(1, int(img.height * resize_factor))
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        img.save(buffer, format="PNG", optimize=True, quality=quality)
        b64_string = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return b64_string, orig_width, orig_height


def base64_to_image_bytes(base64_data: str) -> bytes:
    """Decode base64 PNG data to bytes."""
    return base64.b64decode(base64_data.encode("utf-8"))


def to_absolute_box(
    bounding_box: list[int], width: int, height: int
) -> tuple[int, int, int, int]:
    """Convert relative bounding box (0-1000) to absolute pixel coordinates."""
    x1 = int(bounding_box[0] / 1000 * width)
    y1 = int(bounding_box[1] / 1000 * height)
    x2 = int(bounding_box[2] / 1000 * width)
    y2 = int(bounding_box[3] / 1000 * height)
    x1 = max(0, min(width - 1, x1))
    y1 = max(0, min(height - 1, y1))
    x2 = max(0, min(width - 1, x2))
    y2 = max(0, min(height - 1, y2))
    return x1, y1, x2, y2


def annotate_image(
    image_path: str,
    bounding_box: list[int],
    width: int,
    height: int,
    output_dir: str,
    suffix: str = "locate",
) -> str:
    """Draw bounding box and center point on image and save to output_dir."""
    from pathlib import Path
    from PIL import ImageDraw

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    x1, y1, x2, y2 = to_absolute_box(bounding_box, width, height)
    draw.rectangle([x1, y1, x2, y2], outline=(0, 255, 0), width=3)
    cx = int((x1 + x2) / 2)
    cy = int((y1 + y2) / 2)
    radius = 6
    draw.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        outline=(0, 255, 0),
        width=3,
    )
    safe_suffix = (suffix or "locate").strip().replace(" ", "-")
    out_path = output_path / (Path(image_path).stem + f"_{safe_suffix}.png")
    image.save(out_path)
    return str(out_path)


def annotate_image_multi(
    image_path: str,
    bounding_boxes: list[list[int]],
    width: int,
    height: int,
    output_dir: str,
    suffix: str = "locate",
) -> str:
    """Draw multiple bounding boxes on image and save to output_dir."""
    from pathlib import Path
    from PIL import ImageDraw

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    palette = [
        (0, 255, 0),
        (255, 0, 0),
        (0, 128, 255),
        (255, 128, 0),
        (128, 0, 255),
        (0, 200, 200),
    ]

    for index, bounding_box in enumerate(bounding_boxes):
        if not isinstance(bounding_box, list) or len(bounding_box) != 4:
            continue
        color = palette[index % len(palette)]
        x1, y1, x2, y2 = to_absolute_box(bounding_box, width, height)
        draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)
        radius = 6
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            outline=color,
            width=3,
        )

    safe_suffix = (suffix or "locate").strip().replace(" ", "-")
    out_path = output_path / (Path(image_path).stem + f"_{safe_suffix}.png")
    image.save(out_path)
    return str(out_path)


def capture_screenshot_to_file(
    device_id: str | None, output_dir: str, display_id: int | None = None
) -> tuple[str, str | None]:
    """Capture screenshot from device and save to file."""
    from vision_agent.device.adb.screenshot import get_screenshot
    from vision_agent.device.adb.ui_hierarchy import resolve_device_id

    resolved_device_id = resolve_device_id(device_id)
    screenshot = get_screenshot(resolved_device_id, display_id=display_id)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    path = Path(output_dir) / f"{timestamp}.png"
    path.write_bytes(base64_to_image_bytes(screenshot.base64_data))
    return str(path), resolved_device_id
