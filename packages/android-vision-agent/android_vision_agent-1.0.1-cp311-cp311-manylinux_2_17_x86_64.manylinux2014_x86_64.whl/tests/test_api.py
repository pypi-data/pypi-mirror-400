"""API module tests."""

import pytest

from vision_agent import VisionAgent, LicenseError
from vision_agent.license.generator import LicenseGenerator


class TestVisionAgentInit:
    """Test VisionAgent initialization."""

    def test_dev_mode_no_license_required(self):
        """Test dev mode doesn't require license."""
        agent = VisionAgent(dev_mode=True)
        assert agent.license_info is not None
        assert agent.license_info.user_id == "dev"

    def test_license_key_required_in_production(self):
        """Test license is required without dev_mode."""
        with pytest.raises(LicenseError):
            VisionAgent()

    def test_init_with_license_key(self):
        """Test initialization with license key."""
        gen = LicenseGenerator()
        key = gen.create(user_id="test", days=30)

        agent = VisionAgent(license_key=key)
        assert agent.license_info.user_id == "test"

    def test_init_with_defaults(self):
        """Test default values are set."""
        agent = VisionAgent(
            dev_mode=True,
            device_id="emulator-5554",
            display_id=0,
            output_dir="test_outputs",
            lang="en",
            max_steps=20,
        )
        assert agent.device_id == "emulator-5554"
        assert agent.display_id == 0
        assert agent._output_dir == "test_outputs"
        assert agent._lang == "en"
        assert agent._max_steps == 20

    def test_device_id_setter(self):
        """Test device_id can be changed."""
        agent = VisionAgent(dev_mode=True, device_id="device1")
        assert agent.device_id == "device1"

        agent.device_id = "device2"
        assert agent.device_id == "device2"


class TestVisionAgentMethods:
    """Test VisionAgent methods exist and have correct signatures."""

    @pytest.fixture
    def agent(self):
        """Create agent in dev mode."""
        return VisionAgent(dev_mode=True)

    def test_has_list_displays(self, agent):
        """Test list_displays method exists."""
        assert hasattr(agent, "list_displays")
        assert callable(agent.list_displays)

    def test_has_locate(self, agent):
        """Test locate method exists."""
        assert hasattr(agent, "locate")
        assert callable(agent.locate)

    def test_has_locate_xml(self, agent):
        """Test locate_xml method exists."""
        assert hasattr(agent, "locate_xml")
        assert callable(agent.locate_xml)

    def test_has_locate_ocr(self, agent):
        """Test locate_ocr method exists."""
        assert hasattr(agent, "locate_ocr")
        assert callable(agent.locate_ocr)

    def test_has_ocr(self, agent):
        """Test ocr method exists."""
        assert hasattr(agent, "ocr")
        assert callable(agent.ocr)

    def test_has_diff(self, agent):
        """Test diff method exists."""
        assert hasattr(agent, "diff")
        assert callable(agent.diff)

    def test_has_action(self, agent):
        """Test action method exists."""
        assert hasattr(agent, "action")
        assert callable(agent.action)

    def test_has_automate(self, agent):
        """Test automate method exists."""
        assert hasattr(agent, "automate")
        assert callable(agent.automate)

    def test_has_route(self, agent):
        """Test route method exists."""
        assert hasattr(agent, "route")
        assert callable(agent.route)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
