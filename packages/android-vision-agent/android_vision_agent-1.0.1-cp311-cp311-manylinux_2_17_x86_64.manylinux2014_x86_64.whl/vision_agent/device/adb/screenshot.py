"""Screenshot utilities for capturing Android device screen."""

import base64
import os
import re
import subprocess
import tempfile
import uuid
from dataclasses import dataclass
from io import BytesIO

from PIL import Image

from .adb_cmd import adb_prefix

_WINDOW_DISPLAY_SIZE_CACHE: dict[str | None, dict[int, tuple[int, int]]] = {}
_SURFACEFLINGER_DISPLAY_CACHE: dict[str | None, dict[tuple[int, int], int]] = {}
_SCREENCAP_DISPLAY_ID_CACHE: dict[tuple[str | None, int], int] = {}
_DISPLAY_LOCAL_SF_ID_CACHE: dict[str | None, dict[int, int]] = {}


def _get_display_local_surfaceflinger_ids(device_id: str | None) -> dict[int, int]:
    """
    Parse `dumpsys display` and map WindowManager displayId -> SurfaceFlinger displayId
    using the DisplayInfo uniqueId like `local:<sf_display_id>`.
    """
    cached = _DISPLAY_LOCAL_SF_ID_CACHE.get(device_id)
    if cached is not None:
        return cached

    cmd_prefix = adb_prefix(device_id)
    result = subprocess.run(
        cmd_prefix + ["shell", "dumpsys", "display"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
    )
    output = result.stdout or ""

    display_section_re = re.compile(r"^\s*Display\s+(\d+):\s*$")
    unique_local_re = re.compile(r'\buniqueId\s+"local:(\d+)"')

    mapping: dict[int, int] = {}
    current_display: int | None = None
    for line in output.splitlines():
        section_match = display_section_re.match(line)
        if section_match:
            current_display = int(section_match.group(1))
            continue
        if current_display is None:
            continue
        unique_match = unique_local_re.search(line)
        if unique_match:
            mapping[current_display] = int(unique_match.group(1))

    _DISPLAY_LOCAL_SF_ID_CACHE[device_id] = mapping
    return mapping


def _get_window_display_sizes(device_id: str | None) -> dict[int, tuple[int, int]]:
    cached = _WINDOW_DISPLAY_SIZE_CACHE.get(device_id)
    if cached is not None:
        return cached

    cmd_prefix = adb_prefix(device_id)
    result = subprocess.run(
        cmd_prefix + ["shell", "dumpsys", "window"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    output = result.stdout

    display_header = re.compile(r"^\s*Display:\s+mDisplayId=(\d+)")
    init_re = re.compile(r"\binit=(\d+)x(\d+)\b")

    sizes: dict[int, tuple[int, int]] = {}
    current_display: int | None = None
    for line in output.splitlines():
        match = display_header.match(line)
        if match:
            current_display = int(match.group(1))
            continue
        if current_display is None:
            continue
        init_match = init_re.search(line)
        if init_match:
            sizes[current_display] = (int(init_match.group(1)), int(init_match.group(2)))

    _WINDOW_DISPLAY_SIZE_CACHE[device_id] = sizes
    return sizes


def _get_surfaceflinger_displays(device_id: str | None) -> dict[tuple[int, int], int]:
    cached = _SURFACEFLINGER_DISPLAY_CACHE.get(device_id)
    if cached is not None:
        return cached

    cmd_prefix = adb_prefix(device_id)
    result = subprocess.run(
        cmd_prefix + ["shell", "dumpsys", "SurfaceFlinger"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    output = result.stdout

    display_re = re.compile(r"^\s*Display\s+(\d+)\b")
    resolution_re = re.compile(r"\bresolution=(\d+)x(\d+)\b")

    by_resolution: dict[tuple[int, int], int] = {}
    current_sf_display: int | None = None
    for line in output.splitlines():
        display_match = display_re.match(line)
        if display_match:
            current_sf_display = int(display_match.group(1))
            continue
        res_match = resolution_re.search(line)
        if res_match and current_sf_display is not None:
            resolution = (int(res_match.group(1)), int(res_match.group(2)))
            by_resolution.setdefault(resolution, current_sf_display)

    _SURFACEFLINGER_DISPLAY_CACHE[device_id] = by_resolution
    return by_resolution


def _resolve_screencap_display_id(device_id: str | None, display_id: int) -> int:
    """
    `adb shell screencap -d` expects a SurfaceFlinger display ID, while most callers
    (and `adb shell input -d`) use WindowManager display IDs.

    This helper maps WindowManager display IDs to SurfaceFlinger display IDs.
    It prefers `dumpsys display` uniqueId mapping (`local:<sf_id>`), and falls back
    to a resolution-based heuristic when needed (e.g. for virtual displays).
    """
    cache_key = (device_id, display_id)
    cached = _SCREENCAP_DISPLAY_ID_CACHE.get(cache_key)
    if cached is not None:
        return cached

    local_sf_ids = _get_display_local_surfaceflinger_ids(device_id)
    if display_id in local_sf_ids:
        sf_display_id = local_sf_ids[display_id]
        _SCREENCAP_DISPLAY_ID_CACHE[cache_key] = sf_display_id
        return sf_display_id

    window_sizes = _get_window_display_sizes(device_id)
    window_resolution = window_sizes.get(display_id)
    if not window_resolution:
        return display_id

    sf_displays = _get_surfaceflinger_displays(device_id)
    sf_display_id = sf_displays.get(window_resolution)
    if sf_display_id is None:
        # Fallback: match by width and closest height (some virtual displays are cropped).
        width, height = window_resolution
        candidates = [
            (resolution, sf_id)
            for resolution, sf_id in sf_displays.items()
            if resolution[0] == width
        ]
        if candidates:
            candidates.sort(key=lambda item: abs(item[0][1] - height))
            sf_display_id = candidates[0][1]

    if sf_display_id is None:
        return display_id

    _SCREENCAP_DISPLAY_ID_CACHE[cache_key] = sf_display_id
    return sf_display_id


@dataclass
class Screenshot:
    """Represents a captured screenshot."""

    base64_data: str
    width: int
    height: int
    is_sensitive: bool = False


def get_screenshot(
    device_id: str | None = None, timeout: int = 10, display_id: int | None = None
) -> Screenshot:
    """
    Capture a screenshot from the connected Android device.

    Args:
        device_id: Optional ADB device ID for multi-device setups.
        timeout: Timeout in seconds for screenshot operations.

    Returns:
        Screenshot object containing base64 data and dimensions.

    Note:
        If the screenshot fails (e.g., on sensitive screens like payment pages),
        a black fallback image is returned with is_sensitive=True.
    """
    return get_screenshot_for_display(
        device_id=device_id, display_id=display_id, timeout=timeout
    )


def get_screenshot_for_display(
    device_id: str | None = None, display_id: int | None = None, timeout: int = 10
) -> Screenshot:
    """
    Capture a screenshot from a specific Android display.

    Args:
        device_id: Optional ADB device ID for multi-device setups.
        display_id: WindowManager display ID (e.g., 0 for main display). If None, uses default.
        timeout: Timeout in seconds for screenshot operations.
    """
    temp_path = os.path.join(tempfile.gettempdir(), f"screenshot_{uuid.uuid4()}.png")
    cmd_prefix = adb_prefix(device_id)

    try:
        screencap_cmd = cmd_prefix + ["shell", "screencap", "-p"]
        if display_id is not None:
            screencap_display_id = _resolve_screencap_display_id(device_id, int(display_id))
            screencap_cmd += ["-d", str(screencap_display_id)]
        screencap_cmd += ["/sdcard/tmp.png"]

        result = subprocess.run(
            screencap_cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if display_id is not None and result.returncode != 0:
            result = subprocess.run(
                cmd_prefix + ["shell", "screencap", "-p", "/sdcard/tmp.png"],
                capture_output=True,
                text=True,
                timeout=timeout,
            )

        # Check for screenshot failure (sensitive screen)
        output = result.stdout + result.stderr
        if "Status: -1" in output or "Failed" in output:
            return _create_fallback_screenshot(is_sensitive=True)

        # Pull screenshot to local temp path
        subprocess.run(
            cmd_prefix + ["pull", "/sdcard/tmp.png", temp_path],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if not os.path.exists(temp_path):
            return _create_fallback_screenshot(is_sensitive=False)

        # Read and encode image
        img = Image.open(temp_path)
        width, height = img.size

        buffered = BytesIO()
        img.save(buffered, format="PNG")
        base64_data = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # Cleanup
        os.remove(temp_path)

        return Screenshot(
            base64_data=base64_data, width=width, height=height, is_sensitive=False
        )

    except Exception as e:
        print(f"Screenshot error: {e}")
        return _create_fallback_screenshot(is_sensitive=False)


def _create_fallback_screenshot(is_sensitive: bool) -> Screenshot:
    """Create a black fallback image when screenshot fails."""
    default_width, default_height = 1080, 2400

    black_img = Image.new("RGB", (default_width, default_height), color="black")
    buffered = BytesIO()
    black_img.save(buffered, format="PNG")
    base64_data = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return Screenshot(
        base64_data=base64_data,
        width=default_width,
        height=default_height,
        is_sensitive=is_sensitive,
    )
