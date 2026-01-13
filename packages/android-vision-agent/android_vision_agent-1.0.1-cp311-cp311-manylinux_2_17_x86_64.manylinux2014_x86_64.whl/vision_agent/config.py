"""Consolidated configuration for the vision agent app."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ModelConfig:
    """LLM model configuration."""

    base_url: str
    api_key: str
    model: str
    temperature: float = 0.1
    max_tokens: int = 2048


@dataclass
class AgentConfig:
    """Agent runtime configuration."""

    lang: str = "cn"
    max_steps: int = 50
    output_dir: str = "outputs"


@dataclass
class TimingConfig:
    """Timing delays for actions and device operations."""

    # Action handler delays
    keyboard_switch_delay: float = 1.0
    text_clear_delay: float = 1.0
    text_input_delay: float = 1.0
    keyboard_restore_delay: float = 1.0

    # Device operation delays
    tap_delay: float = 1.0
    double_tap_delay: float = 1.0
    double_tap_interval: float = 0.1
    long_press_delay: float = 1.0
    swipe_delay: float = 1.0
    back_delay: float = 1.0
    home_delay: float = 1.0

    def __post_init__(self):
        """Load values from environment variables if present."""
        self.keyboard_switch_delay = float(
            os.getenv("VISION_AGENT_KEYBOARD_SWITCH_DELAY", self.keyboard_switch_delay)
        )
        self.text_clear_delay = float(
            os.getenv("VISION_AGENT_TEXT_CLEAR_DELAY", self.text_clear_delay)
        )
        self.text_input_delay = float(
            os.getenv("VISION_AGENT_TEXT_INPUT_DELAY", self.text_input_delay)
        )
        self.keyboard_restore_delay = float(
            os.getenv("VISION_AGENT_KEYBOARD_RESTORE_DELAY", self.keyboard_restore_delay)
        )
        self.tap_delay = float(
            os.getenv("VISION_AGENT_TAP_DELAY", self.tap_delay)
        )
        self.double_tap_delay = float(
            os.getenv("VISION_AGENT_DOUBLE_TAP_DELAY", self.double_tap_delay)
        )
        self.double_tap_interval = float(
            os.getenv("VISION_AGENT_DOUBLE_TAP_INTERVAL", self.double_tap_interval)
        )
        self.long_press_delay = float(
            os.getenv("VISION_AGENT_LONG_PRESS_DELAY", self.long_press_delay)
        )
        self.swipe_delay = float(
            os.getenv("VISION_AGENT_SWIPE_DELAY", self.swipe_delay)
        )
        self.back_delay = float(
            os.getenv("VISION_AGENT_BACK_DELAY", self.back_delay)
        )
        self.home_delay = float(
            os.getenv("VISION_AGENT_HOME_DELAY", self.home_delay)
        )


# Global timing configuration instance
TIMING_CONFIG = TimingConfig()


def load_dotenv(path: str | Path = ".env") -> None:
    """Load environment variables from a .env file if present."""
    env_path = Path(path)
    if not env_path.is_file():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        raw_value = value.strip()
        if (raw_value.startswith('"') and raw_value.endswith('"')) or (
            raw_value.startswith("'") and raw_value.endswith("'")
        ):
            value = raw_value[1:-1]
        else:
            value = raw_value.split("#", 1)[0].strip()
        if key and key not in os.environ:
            os.environ[key] = value


def load_settings() -> tuple[ModelConfig, AgentConfig]:
    """Load model and agent settings from environment."""
    model = ModelConfig(
        base_url=os.getenv("VISION_AGENT_BASE_URL", "http://localhost:8000/v1"),
        api_key=os.getenv("VISION_AGENT_API_KEY", "EMPTY"),
        model=os.getenv("VISION_AGENT_MODEL", "qwen3-vl-plus"),
        temperature=float(os.getenv("VISION_AGENT_TEMPERATURE", "0.1")),
        max_tokens=int(os.getenv("VISION_AGENT_MAX_TOKENS", "2048")),
    )

    agent = AgentConfig(
        lang=os.getenv("VISION_AGENT_LANG", "cn"),
        max_steps=int(os.getenv("VISION_AGENT_MAX_STEPS", "50")),
        output_dir=os.getenv("VISION_AGENT_OUTPUT_DIR", "outputs"),
    )

    return model, agent


__all__ = [
    "ModelConfig",
    "AgentConfig",
    "TimingConfig",
    "TIMING_CONFIG",
    "load_dotenv",
    "load_settings",
]
