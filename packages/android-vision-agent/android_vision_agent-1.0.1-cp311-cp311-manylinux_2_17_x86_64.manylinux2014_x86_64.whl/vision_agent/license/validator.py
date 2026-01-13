"""License validator - validates license keys."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import platform
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from vision_agent.exceptions import LicenseExpiredError, LicenseInvalidError


# Secret key for HMAC (in production, this would be compiled into .pyd)
_SECRET_KEY = b"vision_agent_secret_key_2025"


@dataclass
class LicenseInfo:
    """License information."""
    user_id: str
    created_at: datetime
    expires_at: datetime
    max_devices: int
    machine_id: str | None = None


def _get_machine_id() -> str:
    """Get unique machine identifier."""
    node = uuid.getnode()
    system = platform.system()
    return hashlib.md5(f"{node}-{system}".encode()).hexdigest()[:16]


class LicenseValidator:
    """Validates license keys."""

    def __init__(self, dev_mode: bool = False):
        self._dev_mode = dev_mode
        if dev_mode:
            self._license_info = LicenseInfo(
                user_id="dev",
                created_at=datetime.now(),
                expires_at=datetime(2099, 12, 31),
                max_devices=999,
            )
        else:
            self._license_info = None

    @property
    def is_valid(self) -> bool:
        return self._dev_mode or self._license_info is not None

    @property
    def info(self) -> LicenseInfo | None:
        return self._license_info

    def validate_key(self, license_key: str) -> LicenseInfo:
        """Validate a license key string."""
        if self._dev_mode:
            return self._license_info

        try:
            parts = license_key.split(".")
            if len(parts) != 2:
                raise LicenseInvalidError("Invalid license format")

            payload_b64, signature = parts
            payload_bytes = base64.urlsafe_b64decode(payload_b64)

            # Verify signature
            expected_sig = hmac.new(_SECRET_KEY, payload_bytes, hashlib.sha256).hexdigest()[:32]
            if not hmac.compare_digest(signature, expected_sig):
                raise LicenseInvalidError("Invalid license signature")

            data = json.loads(payload_bytes.decode())
            expires_at = datetime.fromisoformat(data["expires_at"])

            if datetime.now() > expires_at:
                raise LicenseExpiredError(f"License expired on {expires_at}")

            # Check machine binding if present
            if data.get("machine_id") and data["machine_id"] != _get_machine_id():
                raise LicenseInvalidError("License not valid for this machine")

            self._license_info = LicenseInfo(
                user_id=data["user_id"],
                created_at=datetime.fromisoformat(data["created_at"]),
                expires_at=expires_at,
                max_devices=data.get("max_devices", 1),
                machine_id=data.get("machine_id"),
            )
            return self._license_info

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise LicenseInvalidError(f"Invalid license data: {e}")

    def validate_file(self, license_file: str | Path) -> LicenseInfo:
        """Validate a license file."""
        path = Path(license_file)
        if not path.exists():
            raise LicenseInvalidError(f"License file not found: {license_file}")
        license_key = path.read_text(encoding="utf-8").strip()
        return self.validate_key(license_key)
