"""Shared ADB helpers."""

from __future__ import annotations


def adb_prefix(device_id: str | None) -> list[str]:
    """Build the adb command prefix with an optional device selector."""
    return ["adb", "-s", device_id] if device_id else ["adb"]
