"""App-related helpers for Android automation."""

from __future__ import annotations

import re
import subprocess

from .adb_cmd import adb_prefix


def get_installed_packages(device_id: str | None = None) -> list[str]:
    """
    Get list of installed packages on the device.

    Args:
        device_id: Optional ADB device ID.

    Returns:
        List of package names.
    """
    cmd_prefix = adb_prefix(device_id)
    result = subprocess.run(
        cmd_prefix + ["shell", "pm", "list", "packages"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    packages = []
    for line in result.stdout.strip().split("\n"):
        if line.startswith("package:"):
            packages.append(line[8:])
    return packages


def _extract_package_from_focus_line(line: str) -> str | None:
    if "/" not in line:
        return None
    part = line.split("/", 1)[0]
    tokens = part.split()
    if not tokens:
        return None
    package = tokens[-1].strip()
    if "." not in package:
        return None
    return package


def get_current_app(device_id: str | None = None, display_id: int | None = None) -> str:
    """
    Get the currently focused app package name.

    Args:
        device_id: Optional ADB device ID for multi-device setups.

    Returns:
        The package name of focused app, or "System Home" if not found.
    """
    cmd_prefix = adb_prefix(device_id)

    result = subprocess.run(
        cmd_prefix + ["shell", "dumpsys", "window"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    output = result.stdout
    if not output:
        raise ValueError("No output from dumpsys window")

    target_display_id = 0 if display_id is None else int(display_id)

    focused_by_display: dict[int, str] = {}
    current_display: int | None = None

    display_header = re.compile(r"^\s*Display:\s+mDisplayId=(\d+)")
    for line in output.splitlines():
        match = display_header.match(line)
        if match:
            current_display = int(match.group(1))
            continue

        if current_display is None:
            continue

        if "mCurrentFocus" in line or "mFocusedApp" in line:
            package = _extract_package_from_focus_line(line)
            if package:
                focused_by_display[current_display] = package

    if target_display_id in focused_by_display:
        return focused_by_display[target_display_id]

    if 0 in focused_by_display:
        return focused_by_display[0]

    if focused_by_display:
        return focused_by_display[sorted(focused_by_display.keys())[0]]

    for line in output.splitlines():
        if "mCurrentFocus" in line or "mFocusedApp" in line:
            package = _extract_package_from_focus_line(line)
            if package:
                return package

    return "System Home"
