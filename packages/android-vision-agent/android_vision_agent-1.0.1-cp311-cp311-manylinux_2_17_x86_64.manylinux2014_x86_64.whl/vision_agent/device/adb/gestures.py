"""Gesture helpers for Android automation."""

from __future__ import annotations

import subprocess
import time

from .adb_cmd import adb_prefix
from vision_agent.config import TIMING_CONFIG


def tap(
    x: int,
    y: int,
    device_id: str | None = None,
    display_id: int | None = None,
    delay: float | None = None,
) -> None:
    """
    Tap at the specified coordinates.

    Args:
        x: X coordinate.
        y: Y coordinate.
        device_id: Optional ADB device ID.
        delay: Delay in seconds after tap. If None, uses configured default.
    """
    if delay is None:
        delay = TIMING_CONFIG.tap_delay

    cmd_prefix = adb_prefix(device_id)

    input_cmd = cmd_prefix + ["shell", "input"]
    if display_id is not None:
        input_cmd += ["-d", str(int(display_id))]
    input_cmd += ["tap", str(x), str(y)]

    result = subprocess.run(input_cmd, capture_output=True)
    if display_id is not None and result.returncode != 0:
        subprocess.run(
            cmd_prefix + ["shell", "input", "tap", str(x), str(y)], capture_output=True
        )
    time.sleep(delay)


def double_tap(
    x: int,
    y: int,
    device_id: str | None = None,
    display_id: int | None = None,
    delay: float | None = None,
) -> None:
    """
    Double tap at the specified coordinates.

    Args:
        x: X coordinate.
        y: Y coordinate.
        device_id: Optional ADB device ID.
        delay: Delay in seconds after double tap. If None, uses configured default.
    """
    if delay is None:
        delay = TIMING_CONFIG.double_tap_delay

    cmd_prefix = adb_prefix(device_id)

    input_cmd = cmd_prefix + ["shell", "input"]
    if display_id is not None:
        input_cmd += ["-d", str(int(display_id))]
    input_cmd += ["tap", str(x), str(y)]

    result = subprocess.run(input_cmd, capture_output=True)
    if display_id is not None and result.returncode != 0:
        subprocess.run(
            cmd_prefix + ["shell", "input", "tap", str(x), str(y)], capture_output=True
        )
    time.sleep(TIMING_CONFIG.double_tap_interval)
    result = subprocess.run(input_cmd, capture_output=True)
    if display_id is not None and result.returncode != 0:
        subprocess.run(
            cmd_prefix + ["shell", "input", "tap", str(x), str(y)], capture_output=True
        )
    time.sleep(delay)


def long_press(
    x: int,
    y: int,
    duration_ms: int = 3000,
    device_id: str | None = None,
    display_id: int | None = None,
    delay: float | None = None,
) -> None:
    """
    Long press at the specified coordinates.

    Args:
        x: X coordinate.
        y: Y coordinate.
        duration_ms: Duration of press in milliseconds.
        device_id: Optional ADB device ID.
        delay: Delay in seconds after long press. If None, uses configured default.
    """
    if delay is None:
        delay = TIMING_CONFIG.long_press_delay

    cmd_prefix = adb_prefix(device_id)

    input_cmd = cmd_prefix + ["shell", "input"]
    if display_id is not None:
        input_cmd += ["-d", str(int(display_id))]
    input_cmd += ["swipe", str(x), str(y), str(x), str(y), str(duration_ms)]

    result = subprocess.run(input_cmd, capture_output=True)
    if display_id is not None and result.returncode != 0:
        subprocess.run(
            cmd_prefix
            + [
                "shell",
                "input",
                "swipe",
                str(x),
                str(y),
                str(x),
                str(y),
                str(duration_ms),
            ],
            capture_output=True,
        )
    time.sleep(delay)


def swipe(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration_ms: int | None = None,
    device_id: str | None = None,
    display_id: int | None = None,
    delay: float | None = None,
) -> None:
    """
    Swipe from start to end coordinates.

    Args:
        start_x: Starting X coordinate.
        start_y: Starting Y coordinate.
        end_x: Ending X coordinate.
        end_y: Ending Y coordinate.
        duration_ms: Duration of swipe in milliseconds (auto-calculated if None).
        device_id: Optional ADB device ID.
        delay: Delay in seconds after swipe. If None, uses configured default.
    """
    if delay is None:
        delay = TIMING_CONFIG.swipe_delay

    cmd_prefix = adb_prefix(device_id)

    if duration_ms is None:
        # Calculate duration based on distance
        dist_sq = (start_x - end_x) ** 2 + (start_y - end_y) ** 2
        duration_ms = int(dist_sq / 1000)
        duration_ms = max(1000, min(duration_ms, 2000))  # Clamp between 1000-2000ms

    input_cmd = cmd_prefix + ["shell", "input"]
    if display_id is not None:
        input_cmd += ["-d", str(int(display_id))]
    input_cmd += [
        "swipe",
        str(start_x),
        str(start_y),
        str(end_x),
        str(end_y),
        str(duration_ms),
    ]

    result = subprocess.run(input_cmd, capture_output=True)
    if display_id is not None and result.returncode != 0:
        subprocess.run(
            cmd_prefix
            + [
                "shell",
                "input",
                "swipe",
                str(start_x),
                str(start_y),
                str(end_x),
                str(end_y),
                str(duration_ms),
            ],
            capture_output=True,
        )
    time.sleep(delay)


def back(
    device_id: str | None = None, display_id: int | None = None, delay: float | None = None
) -> None:
    """
    Press the back button.

    Args:
        device_id: Optional ADB device ID.
        delay: Delay in seconds after pressing back. If None, uses configured default.
    """
    if delay is None:
        delay = TIMING_CONFIG.back_delay

    cmd_prefix = adb_prefix(device_id)

    input_cmd = cmd_prefix + ["shell", "input"]
    if display_id is not None:
        input_cmd += ["-d", str(int(display_id))]
    input_cmd += ["keyevent", "4"]

    result = subprocess.run(input_cmd, capture_output=True)
    if display_id is not None and result.returncode != 0:
        subprocess.run(
            cmd_prefix + ["shell", "input", "keyevent", "4"], capture_output=True
        )
    time.sleep(delay)


def home(
    device_id: str | None = None, display_id: int | None = None, delay: float | None = None
) -> None:
    """
    Press the home button.

    Args:
        device_id: Optional ADB device ID.
        delay: Delay in seconds after pressing home. If None, uses configured default.
    """
    if delay is None:
        delay = TIMING_CONFIG.home_delay

    cmd_prefix = adb_prefix(device_id)

    input_cmd = cmd_prefix + ["shell", "input"]
    if display_id is not None:
        input_cmd += ["-d", str(int(display_id))]
    input_cmd += ["keyevent", "KEYCODE_HOME"]

    result = subprocess.run(input_cmd, capture_output=True)
    if display_id is not None and result.returncode != 0:
        subprocess.run(
            cmd_prefix + ["shell", "input", "keyevent", "KEYCODE_HOME"],
            capture_output=True,
        )
    time.sleep(delay)
