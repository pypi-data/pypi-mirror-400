"""uiautomator2 helpers for UI hierarchy dumps."""

from __future__ import annotations

from .devices import list_devices


def _select_device(device_id: str | None) -> str | None:
    devices = list_devices()
    if not devices:
        raise RuntimeError("No ADB devices detected")
    if device_id:
        if not any(d.device_id == device_id for d in devices):
            raise RuntimeError(f"Device not found: {device_id}")
        return device_id
    if len(devices) > 1:
        raise RuntimeError("Multiple devices detected; please provide --device-id")
    return devices[0].device_id


def resolve_device_id(device_id: str | None) -> str | None:
    return _select_device(device_id)


def dump_ui_hierarchy(device_id: str | None = None) -> str:
    try:
        import uiautomator2 as u2
    except Exception as exc:
        raise RuntimeError(
            "uiautomator2 is required for locate-xml mode. Install with `pip install uiautomator2`."
        ) from exc

    selected = _select_device(device_id)
    try:
        device = u2.connect(selected) if selected else u2.connect()
    except Exception as exc:
        raise RuntimeError("Failed to connect to device via uiautomator2") from exc

    try:
        return device.dump_hierarchy()
    except Exception as exc:
        raise RuntimeError("Failed to dump UI hierarchy via uiautomator2") from exc
