"""Integration tests - requires device connection and LLM config."""

import pytest
import os
from pathlib import Path

from vision_agent import VisionAgent


# Test image path
TEST_IMAGE = Path(__file__).parent.parent / "assets" / "test_images" / "image.png"

# Device ID for testing (set via env or hardcode for local testing)
TEST_DEVICE = os.getenv("VISION_AGENT_TEST_DEVICE", "emulator-5554")

# Skip all tests if no device connected
# pytestmark = pytest.mark.skipif(
#     os.getenv("VISION_AGENT_TEST_DEVICE") is None,
#     reason="Set VISION_AGENT_TEST_DEVICE to run integration tests"
# )


@pytest.fixture
def agent():
    """Create agent with test device."""
    return VisionAgent(dev_mode=True, device_id=TEST_DEVICE)


class TestDisplays:
    """Test displays mode."""

    def test_list_displays(self, agent):
        """Test listing displays."""
        result = agent.list_displays()
        assert "displays" in result or "error" not in result


class TestLocate:
    """Test locate modes."""

    def test_locate_element(self, agent):
        """Test visual locate."""
        result = agent.locate("应用列表图标")
        assert result is not None

    def test_locate_with_image(self, agent):
        """Test visual locate with image path."""
        result = agent.locate("找到LDCU对应的零部件号和硬件版本值", image=str(TEST_IMAGE))
        assert result is not None

    def test_locate_xml(self, agent):
        """Test XML locate."""
        result = agent.locate_xml("调节亮度的图标")
        assert result is not None

    def test_locate_ocr(self, agent):
        """Test OCR locate."""
        result = agent.locate_ocr("识别图中的温度值")
        assert result is not None

    def test_locate_ocr_with_image(self, agent):
        """Test OCR locate with image path."""
        result = agent.locate_ocr("找到CDCU对应的零部件号和硬件版本值", image=str(TEST_IMAGE))
        assert result is not None


class TestOCR:
    """Test OCR mode."""

    def test_ocr_screen(self, agent):
        """Test OCR on current screen."""
        result = agent.ocr()
        assert result is not None

    def test_ocr_with_image(self, agent):
        """Test OCR with image path."""
        result = agent.ocr(image=str(TEST_IMAGE))
        assert result is not None


class TestAction:
    """Test action mode."""

    def test_single_action(self, agent):
        """Test single action execution."""
        result = agent.action("点击home按钮")
        assert result is not None


class TestAutomate:
    """Test automate mode."""

    def test_automate_task(self, agent):
        """Test multi-step automation."""
        result = agent.automate("进入设置应用", max_steps=10)
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
