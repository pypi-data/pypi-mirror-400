"""Diff mode - Compare two images and highlight differences."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageStat


@dataclass
class DiffResult:
    diff_score: float
    diff_boxes: list[list[int]]
    diff_image_path: str


def _find_boxes(mask: Image.Image, min_area: int) -> list[list[int]]:
    width, height = mask.size
    pixels = mask.load()
    visited = bytearray(width * height)
    boxes: list[list[int]] = []

    def index(x: int, y: int) -> int:
        return y * width + x

    for y in range(height):
        row_offset = y * width
        for x in range(width):
            idx = row_offset + x
            if visited[idx] or pixels[x, y] == 0:
                continue

            stack = [(x, y)]
            visited[idx] = 1
            min_x = max_x = x
            min_y = max_y = y
            area = 0

            while stack:
                cx, cy = stack.pop()
                area += 1
                if cx < min_x:
                    min_x = cx
                if cx > max_x:
                    max_x = cx
                if cy < min_y:
                    min_y = cy
                if cy > max_y:
                    max_y = cy

                if cx > 0:
                    nx, ny = cx - 1, cy
                    nidx = index(nx, ny)
                    if not visited[nidx] and pixels[nx, ny] != 0:
                        visited[nidx] = 1
                        stack.append((nx, ny))
                if cx + 1 < width:
                    nx, ny = cx + 1, cy
                    nidx = index(nx, ny)
                    if not visited[nidx] and pixels[nx, ny] != 0:
                        visited[nidx] = 1
                        stack.append((nx, ny))
                if cy > 0:
                    nx, ny = cx, cy - 1
                    nidx = index(nx, ny)
                    if not visited[nidx] and pixels[nx, ny] != 0:
                        visited[nidx] = 1
                        stack.append((nx, ny))
                if cy + 1 < height:
                    nx, ny = cx, cy + 1
                    nidx = index(nx, ny)
                    if not visited[nidx] and pixels[nx, ny] != 0:
                        visited[nidx] = 1
                        stack.append((nx, ny))

            if area >= min_area:
                boxes.append([min_x, min_y, max_x, max_y])

    return boxes


def compute_diff(
    image_a: str,
    image_b: str,
    output_dir: str,
    threshold: int = 25,
    min_area: int = 60,
    scale: float = 0.5,
    max_boxes: int = 10,
) -> DiffResult:
    img_a = Image.open(image_a).convert("RGB")
    img_b = Image.open(image_b).convert("RGB")

    resized = False
    if img_a.size != img_b.size:
        img_b = img_b.resize(img_a.size, Image.Resampling.LANCZOS)
        resized = True

    diff = ImageChops.difference(img_a, img_b).convert("L")
    diff_score = ImageStat.Stat(diff).mean[0] / 255.0

    if scale != 1.0:
        small = diff.resize(
            (max(1, int(diff.width * scale)), max(1, int(diff.height * scale))),
            Image.Resampling.BILINEAR,
        )
    else:
        small = diff

    mask = small.point(lambda p: 255 if p > threshold else 0)
    boxes = _find_boxes(mask, min_area=min_area)

    if scale != 1.0:
        scale_x = diff.width / mask.width
        scale_y = diff.height / mask.height
        scaled_boxes = [
            [
                int(x1 * scale_x),
                int(y1 * scale_y),
                int(x2 * scale_x),
                int(y2 * scale_y),
            ]
            for x1, y1, x2, y2 in boxes
        ]
    else:
        scaled_boxes = boxes

    scaled_boxes = sorted(
        scaled_boxes, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]), reverse=True
    )[:max_boxes]

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    diff_path = output_path / (Path(image_a).stem + "_diff.png")

    overlay = img_a.copy()
    draw = ImageDraw.Draw(overlay)
    for box in scaled_boxes:
        draw.rectangle(box, outline=(255, 0, 0), width=3)

    if resized:
        draw.text((10, 10), "note: image_b resized", fill=(255, 0, 0))

    overlay.save(diff_path)

    return DiffResult(
        diff_score=diff_score,
        diff_boxes=scaled_boxes,
        diff_image_path=str(diff_path),
    )


def run(
    image_paths: list[str],
    output_dir: str = "outputs",
    **kwargs,
) -> dict[str, Any]:
    """Compare two images and return differences."""
    if len(image_paths) < 2:
        raise ValueError("diff mode requires two images")

    result = compute_diff(image_paths[0], image_paths[1], output_dir=output_dir)
    return {
        "mode": "diff",
        "diff_score": result.diff_score,
        "diff_boxes": result.diff_boxes,
        "diff_image_path": result.diff_image_path,
    }
