"""ADB utilities and device helpers."""

from .devices import (
    ADBConnection,
    ConnectionType,
    DeviceInfo,
    list_devices,
)
from .displays import list_displays, list_surfaceflinger_displays
from .apps import get_current_app, get_installed_packages
from .gestures import (
    back,
    double_tap,
    home,
    long_press,
    swipe,
    tap,
)
from .text_input import (
    clear_text,
    detect_and_set_adb_keyboard,
    restore_keyboard,
    type_text,
)
from .screenshot import Screenshot, get_screenshot
from .ui_hierarchy import dump_ui_hierarchy, resolve_device_id

__all__ = [
    "ConnectionType",
    "DeviceInfo",
    "ADBConnection",
    "list_devices",
    "list_displays",
    "list_surfaceflinger_displays",
    "get_current_app",
    "get_installed_packages",
    "tap",
    "double_tap",
    "long_press",
    "swipe",
    "back",
    "home",
    "clear_text",
    "type_text",
    "detect_and_set_adb_keyboard",
    "restore_keyboard",
    "Screenshot",
    "get_screenshot",
    "dump_ui_hierarchy",
    "resolve_device_id",
]
