"""Vision Agent App package.

This package provides:
- Android device control via ADB
- Vision-based element location (with optional XML UI hierarchy)
- Single-step and multi-step automation driven by an LLM

Usage:
    from vision_agent import VisionAgent

    # Development mode
    agent = VisionAgent(dev_mode=True, device_id="emulator-5554")

    # Production mode
    agent = VisionAgent(license_key="xxx", device_id="emulator-5554")

    # Execute actions
    agent.action("点击搜索按钮")
    agent.automate("打开设置并截图")
"""

from __future__ import annotations

from vision_agent.api import VisionAgent
from vision_agent.exceptions import (
    VisionAgentError,
    LicenseError,
    LicenseExpiredError,
    LicenseInvalidError,
    DeviceError,
    ModeError,
)

__version__ = "0.1.0"

__all__ = [
    "VisionAgent",
    "VisionAgentError",
    "LicenseError",
    "LicenseExpiredError",
    "LicenseInvalidError",
    "DeviceError",
    "ModeError",
]
