"""License module tests."""

import pytest

from vision_agent.license.generator import LicenseGenerator
from vision_agent.license.validator import LicenseValidator, LicenseInfo
from vision_agent.exceptions import LicenseExpiredError, LicenseInvalidError


class TestLicenseGenerator:
    """Test license generation."""

    def test_create_basic_license(self):
        """Test creating a basic license."""
        gen = LicenseGenerator()
        key = gen.create(user_id="test_user", days=30)
        assert key is not None
        assert "." in key  # format: payload.signature

    def test_create_license_with_max_devices(self):
        """Test creating license with max devices."""
        gen = LicenseGenerator()
        key = gen.create(
            user_id="test_user",
            days=180,
            max_devices=5,
        )
        assert key is not None


class TestLicenseValidator:
    """Test license validation."""

    def test_dev_mode_always_valid(self):
        """Test dev mode bypasses validation."""
        validator = LicenseValidator(dev_mode=True)
        info = validator.validate_key("any_invalid_key")
        assert validator.is_valid
        assert info.user_id == "dev"

    def test_validate_generated_license(self):
        """Test validating a generated license."""
        gen = LicenseGenerator()
        key = gen.create(user_id="customer_001", days=30, max_devices=3)

        validator = LicenseValidator()
        info = validator.validate_key(key)

        assert validator.is_valid
        assert info.user_id == "customer_001"
        assert info.max_devices == 3

    def test_invalid_license_format(self):
        """Test invalid license format raises error."""
        validator = LicenseValidator()
        with pytest.raises(LicenseInvalidError):
            validator.validate_key("invalid_key_without_dot")

    def test_invalid_signature(self):
        """Test tampered license raises error."""
        gen = LicenseGenerator()
        key = gen.create(user_id="test", days=30)
        # Tamper with signature
        parts = key.split(".")
        tampered = f"{parts[0]}.{'x' * 32}"

        validator = LicenseValidator()
        with pytest.raises(LicenseInvalidError):
            validator.validate_key(tampered)

    def test_expired_license(self):
        """Test expired license raises error."""
        gen = LicenseGenerator()
        key = gen.create(user_id="test", days=-1)  # Already expired

        validator = LicenseValidator()
        with pytest.raises(LicenseExpiredError):
            validator.validate_key(key)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
