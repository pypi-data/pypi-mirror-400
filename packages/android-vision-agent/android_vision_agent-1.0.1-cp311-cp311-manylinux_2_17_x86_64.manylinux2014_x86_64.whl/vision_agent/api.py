"""Vision Agent SDK - Public API."""

from __future__ import annotations

from typing import Any

from vision_agent.config import ModelConfig, load_dotenv, load_settings
from vision_agent.exceptions import LicenseError, ModeError
from vision_agent.license import LicenseValidator
from vision_agent.modes.llmclient import LlmClient
from vision_agent import router, modes


class VisionAgent:
    """Vision Agent SDK - Main entry point for all operations.

    Example:
        # Development mode (no license required)
        agent = VisionAgent(dev_mode=True, device_id="emulator-5554")

        # Production mode with license
        agent = VisionAgent(license_key="xxx", device_id="emulator-5554")

        # Use methods
        agent.action("点击搜索按钮")
        agent.automate("打开设置并截图", max_steps=20)
    """

    def __init__(
        self,
        license_key: str | None = None,
        license_file: str | None = None,
        device_id: str | None = None,
        display_id: int | None = None,
        output_dir: str = "outputs",
        lang: str = "cn",
        max_steps: int = 10,
        dev_mode: bool = False,
        env_file: str = ".env",
    ):
        """Initialize Vision Agent.

        Args:
            license_key: License key string
            license_file: Path to license file
            device_id: Default ADB device ID
            display_id: Default Android display ID
            output_dir: Default output directory
            lang: Default language (cn/en)
            max_steps: Default max steps for automate mode
            dev_mode: Enable development mode (skip license check)
            env_file: Path to .env file for LLM config
        """
        # License validation
        self._validator = LicenseValidator(dev_mode=dev_mode)
        if not dev_mode:
            if license_key:
                self._validator.validate_key(license_key)
            elif license_file:
                self._validator.validate_file(license_file)
            else:
                raise LicenseError("License key or file required (or use dev_mode=True)")

        # Load LLM config from env
        load_dotenv(env_file)
        model_config, _ = load_settings()

        # Initialize LLM client
        self._llm = LlmClient(model_config)

        # Default settings
        self._device_id = device_id
        self._display_id = display_id
        self._output_dir = output_dir
        self._lang = lang
        self._max_steps = max_steps

    def _merge_kwargs(self, **kwargs) -> dict[str, Any]:
        """Merge method kwargs with instance defaults."""
        return {
            "device_id": kwargs.get("device_id", self._device_id),
            "display_id": kwargs.get("display_id", self._display_id),
            "output_dir": kwargs.get("output_dir", self._output_dir),
            "lang": kwargs.get("lang", self._lang),
            "max_steps": kwargs.get("max_steps", self._max_steps),
        }

    def _call_mode(self, mode: str, prompt: str, image_paths: list[str] | None = None, **kwargs) -> dict[str, Any]:
        """Internal method to call router."""
        merged = self._merge_kwargs(**kwargs)
        return router.route(
            llm=self._llm,
            mode=mode,
            prompt=prompt,
            image_paths=image_paths,
            **merged,
        )

    # ===== Device Management =====

    def list_displays(self, **kwargs) -> dict[str, Any]:
        """List available displays on the device.

        Args:
            **kwargs: Additional options
                - device_id: Optional device ID (overrides instance default)

        Returns:
            Dict with display information:
            {
                "mode": "displays",
                "device_id": "设备ID",
                "displays": [
                    {"display_id": 0, "hwc_port": 0, "unique_id": "local:..."}
                ]
            }
        """
        return self._call_mode("displays", "", **kwargs)

    # ===== Location Methods =====

    def locate(self, prompt: str, *, image: str | None = None, **kwargs) -> dict[str, Any]:
        """Locate element using vision.

        Args:
            prompt: Element description (required)
            image: Optional image path (uses device screenshot if not provided)
            **kwargs: Additional options
                - device_id: Optional device ID (overrides instance default)
                - display_id: Optional display ID (overrides instance default)
                - output_dir: Optional output directory (overrides instance default)

        Returns:
            Dict with location coordinates:
            {
                "mode": "locate",
                "label": "元素标签",
                "bounding_box": [x1, y1, x2, y2],
                "confidence": 0.95,
                "page": 1,
                "annotated_image_path": "path/to/annotated.png"
            }
        """
        images = [image] if image else None
        return self._call_mode("locate", prompt, images, **kwargs)

    def locate_xml(self, prompt: str, **kwargs) -> dict[str, Any]:
        """Locate element using XML UI hierarchy.

        Args:
            prompt: Element description (required)
            **kwargs: Additional options
                - device_id: Optional device ID (overrides instance default, requires device)
                - display_id: Optional display ID (overrides instance default)
                - output_dir: Optional output directory (overrides instance default)

        Returns:
            Dict with location coordinates and XML info:
            {
                "mode": "locate-xml",
                "class": "android.widget.Button",
                "text": "确定",
                "resource-id": "com.app:id/btn_ok",
                "bounds": "[100,200][300,250]",
                "xml_file_path": "path/to/ui.xml"
            }
        """
        return self._call_mode("locate-xml", prompt, **kwargs)

    def locate_ocr(self, prompt: str, *, image: str | None = None, **kwargs) -> dict[str, Any]:
        """Locate element using OCR.

        Args:
            prompt: Text to find (required)
            image: Optional image path (uses device screenshot if not provided)
            **kwargs: Additional options
                - device_id: Optional device ID (overrides instance default)
                - display_id: Optional display ID (overrides instance default)
                - output_dir: Optional output directory (overrides instance default)
                - lang: Optional language (cn/en, overrides instance default)

        Returns:
            Dict with location coordinates and annotated images:
            {
                "mode": "locate-ocr",
                "text": "合并文字",
                "items": [
                    {"text": "文字", "bounding_box": [x1,y1,x2,y2], "confidence": 0.95, "page": 1}
                ],
                "annotated_images": [{"page": 1, "annotated_image_path": "..."}]
            }
        """
        images = [image] if image else None
        return self._call_mode("locate-ocr", prompt, images, **kwargs)

    # ===== Recognition Methods =====

    def ocr(self, prompt: str, *, image: str | None = None, **kwargs) -> dict[str, Any]:
        """Perform OCR on screen or image.

        Args:
            prompt: Query description (required, e.g., "屏幕上显示的时间是多少")
            image: Optional image path (uses device screenshot if not provided)
            **kwargs: Additional options
                - device_id: Optional device ID (overrides instance default)
                - display_id: Optional display ID (overrides instance default)
                - output_dir: Optional output directory (overrides instance default)
                - lang: Optional language (cn/en, overrides instance default)

        Returns:
            Dict with OCR results:
            {
                "mode": "ocr",
                "text": "识别的文字",
                "items": [
                    {"text": "文字1", "confidence": 0.95, "page": 1}
                ]
            }
        """
        images = [image] if image else None
        return self._call_mode("ocr", prompt, images, **kwargs)

    def diff(self, images: list[str], **kwargs) -> dict[str, Any]:
        """Compare two images.

        Args:
            images: List of two image paths to compare (required)
            **kwargs: Additional options
                - output_dir: Optional output directory (overrides instance default)

        Returns:
            Dict with diff results:
            {
                "mode": "diff",
                "diff_score": 0.05,
                "diff_boxes": [[x1,y1,x2,y2], ...],
                "diff_image_path": "path/to/diff.png"
            }
        """
        return self._call_mode("diff", "", images, **kwargs)

    # ===== Action Methods =====

    def action(self, prompt: str, *, image: str | None = None, **kwargs) -> dict[str, Any]:
        """Execute a single action.

        Args:
            prompt: Action description (required, e.g., "点击搜索按钮")
            image: Optional image path (not commonly used, action uses device screenshot)
            **kwargs: Additional options
                - device_id: Optional device ID (overrides instance default, requires device)
                - display_id: Optional display ID (overrides instance default)
                - output_dir: Optional output directory (overrides instance default)

        Returns:
            Dict with action result:
            {
                "mode": "action",
                "action": "Tap",
                "success": true,
                "message": "操作完成"
            }
        """
        images = [image] if image else None
        return self._call_mode("action", prompt, images, **kwargs)

    def automate(self, prompt: str, *, max_steps: int | None = None, **kwargs) -> dict[str, Any]:
        """Execute multi-step automation.

        Args:
            prompt: Task description (required, e.g., "打开设置并截图")
            max_steps: Optional maximum steps (overrides instance default)
            **kwargs: Additional options
                - device_id: Optional device ID (overrides instance default, requires device)
                - display_id: Optional display ID (overrides instance default)
                - output_dir: Optional output directory (overrides instance default)
                - lang: Optional language (cn/en, overrides instance default)

        Returns:
            Dict with automation result:
            {
                "mode": "automate",
                "status": "finished",
                "message": "任务完成",
                "steps": 5
            }
        """
        if max_steps is not None:
            kwargs["max_steps"] = max_steps
        return self._call_mode("automate", prompt, **kwargs)

    # ===== Advanced =====

    def route(self, mode: str, prompt: str, image_paths: list[str] | None = None, **kwargs) -> dict[str, Any]:
        """Direct access to router for advanced usage.

        Args:
            mode: Mode name (displays, diff, locate-xml, locate, ocr, locate-ocr, action, automate)
            prompt: Prompt string
            image_paths: Optional list of image paths

        Returns:
            Dict with mode result
        """
        return self._call_mode(mode, prompt, image_paths, **kwargs)

    # ===== Properties =====

    @property
    def license_info(self):
        """Get current license information."""
        return self._validator.info

    @property
    def device_id(self) -> str | None:
        return self._device_id

    @device_id.setter
    def device_id(self, value: str | None):
        self._device_id = value

    @property
    def display_id(self) -> int | None:
        return self._display_id

    @display_id.setter
    def display_id(self, value: int | None):
        self._display_id = value
