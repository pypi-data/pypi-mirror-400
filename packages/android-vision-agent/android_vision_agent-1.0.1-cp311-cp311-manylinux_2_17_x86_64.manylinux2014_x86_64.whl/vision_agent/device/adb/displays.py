"""Helpers for querying Android displays via ADB dumpsys."""

from __future__ import annotations

import re
import subprocess
from typing import Any

from .adb_cmd import adb_prefix


_DISPLAY_SECTION_RE = re.compile(r"^\s*Display\s+(\d+):\s*$")
_DISPLAY_INFO_NAME_RE = re.compile(r'DisplayInfo\{"([^"]+)"')
_PRIMARY_DEVICE_RE = re.compile(r"^\s*mPrimaryDisplayDevice=(.+?)\s*$")
_UNIQUE_ID_RE = re.compile(r'\buniqueId\s+"([^"]+)"')
_TYPE_RE = re.compile(r"\btype\s+([A-Z_]+)\b")
_REAL_SIZE_RE = re.compile(r"\breal\s+(\d+)\s+x\s+(\d+)\b")
_DEVICE_PRODUCT_NAME_RE = re.compile(
    r"\bdeviceProductInfo\s+DeviceProductInfo\{name=([^,}]+)"
)

_SURFACEFLINGER_DISPLAY_LINE_RE = re.compile(
    r'^Display\s+(\d+)\s+\(HWC display\s+(\d+)\):\s*(.*)$'
)
_SURFACEFLINGER_KV_RE = re.compile(r'(\w+)=(".*?"|\S+)')


def list_surfaceflinger_displays(device_id: str | None = None) -> list[dict[str, Any]]:
    """List SurfaceFlinger display IDs (physical outputs) with displayName/hwc/port."""
    cmd_prefix = adb_prefix(device_id)
    result = subprocess.run(
        cmd_prefix + ["shell", "dumpsys", "SurfaceFlinger", "--display-id"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
    )
    output = (result.stdout or "").strip()
    if not output:
        return []

    displays: list[dict[str, Any]] = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        match = _SURFACEFLINGER_DISPLAY_LINE_RE.match(line)
        if not match:
            continue

        sf_id = match.group(1)
        hwc_display_id = int(match.group(2))
        tail = match.group(3)

        fields: dict[str, str] = {}
        for kv_match in _SURFACEFLINGER_KV_RE.finditer(tail):
            key = kv_match.group(1)
            value = kv_match.group(2)
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            fields[key] = value

        port: int | None = None
        if "port" in fields:
            try:
                port = int(fields["port"])
            except ValueError:
                port = None

        displays.append(
            {
                "surfaceflinger_display_id": sf_id,
                "surfaceflinger_display_name": fields.get("displayName", ""),
                "hwc_display_id": hwc_display_id,
                "port": port,
                "pnp_id": fields.get("pnpId", ""),
            }
        )

    return displays


def list_displays(device_id: str | None = None) -> list[dict[str, Any]]:
    """
    List WindowManager display IDs with a human-friendly name.

    Notes:
      - Uses WindowManager/DisplayManager IDs (the same ID space as `dumpsys window`
        and `adb shell input -d`).
      - The name is parsed from `dumpsys display` (DisplayInfo / PrimaryDisplayDevice).
    """
    cmd_prefix = adb_prefix(device_id)
    result = subprocess.run(
        cmd_prefix + ["shell", "dumpsys", "display"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
    )
    output = result.stdout or ""
    if not output.strip():
        raise RuntimeError("No output from `dumpsys display`")

    sections: dict[int, list[str]] = {}
    current_id: int | None = None
    for line in output.splitlines():
        match = _DISPLAY_SECTION_RE.match(line)
        if match:
            current_id = int(match.group(1))
            sections.setdefault(current_id, [])
            continue
        if current_id is not None:
            sections[current_id].append(line)

    sf_displays = list_surfaceflinger_displays(device_id)
    sf_by_id = {d["surfaceflinger_display_id"]: d for d in sf_displays}

    displays: list[dict[str, Any]] = []
    for display_id in sorted(sections.keys()):
        section_lines = sections[display_id]
        section_text = "\n".join(section_lines)

        name: str | None = None
        info_match = _DISPLAY_INFO_NAME_RE.search(section_text)
        if info_match:
            name = info_match.group(1).strip()
        if not name:
            for line in section_lines:
                primary_match = _PRIMARY_DEVICE_RE.match(line)
                if primary_match:
                    name = primary_match.group(1).strip()
                    break

        unique_id: str | None = None
        unique_match = _UNIQUE_ID_RE.search(section_text)
        if unique_match:
            unique_id = unique_match.group(1).replace("\n", "").replace("\r", "").strip()

        display_type: str | None = None
        type_match = _TYPE_RE.search(section_text)
        if type_match:
            display_type = type_match.group(1).strip()

        real_size: list[int] | None = None
        real_match = _REAL_SIZE_RE.search(section_text)
        if real_match:
            real_size = [int(real_match.group(1)), int(real_match.group(2))]

        device_product_name: str | None = None
        product_match = _DEVICE_PRODUCT_NAME_RE.search(section_text)
        if product_match:
            device_product_name = (
                product_match.group(1).replace("\n", "").replace("\r", "").strip()
            )

        sf_display_id = ""
        if unique_id and unique_id.startswith("local:"):
            sf_display_id = unique_id.split(":", 1)[1].strip()

        sf_info = sf_by_id.get(sf_display_id, {}) if sf_display_id else {}

        displays.append(
            {
                "display_id": display_id,
                "display_name": name or "",
                "type": display_type or "",
                "unique_id": unique_id or "",
                "real_size": real_size or [],
                "device_product_name": device_product_name or "",
                "surfaceflinger_display_id": sf_display_id,
                "surfaceflinger_display_name": sf_info.get(
                    "surfaceflinger_display_name", ""
                ),
                "hwc_display_id": sf_info.get("hwc_display_id", None),
                "hwc_port": sf_info.get("port", None),
            }
        )

    return displays
