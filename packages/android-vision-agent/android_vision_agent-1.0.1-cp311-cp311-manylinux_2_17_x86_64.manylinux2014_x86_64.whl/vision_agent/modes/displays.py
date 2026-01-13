"""Displays mode - List physical displays on Android device."""

from __future__ import annotations

from typing import Any

from vision_agent.device.adb.displays import list_displays
from vision_agent.device.adb.ui_hierarchy import resolve_device_id


def run(
    device_id: str | None = None,
    **kwargs,
) -> dict[str, Any]:
    """List all physical displays on the device."""
    resolved_device_id = resolve_device_id(device_id)
    all_displays = list_displays(resolved_device_id)

    physical_displays: list[dict[str, Any]] = []
    seen_sf_ids: set[str] = set()

    for item in all_displays:
        unique_id = str(item.get("unique_id", "") or "")
        sf_id = str(item.get("surfaceflinger_display_id", "") or "")
        if not unique_id.startswith("local:") or not sf_id:
            continue
        if sf_id in seen_sf_ids:
            continue
        seen_sf_ids.add(sf_id)
        physical_displays.append(item)

    physical_displays.sort(
        key=lambda d: (
            d.get("hwc_port") is None,
            d.get("hwc_port") if d.get("hwc_port") is not None else 0,
            d.get("display_id", 0),
        )
    )

    return {
        "mode": "displays",
        "device_id": resolved_device_id,
        "displays": physical_displays,
    }
