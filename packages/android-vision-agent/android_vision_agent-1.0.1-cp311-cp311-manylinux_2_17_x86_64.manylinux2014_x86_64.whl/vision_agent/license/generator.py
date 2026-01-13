"""License generator - for admin use only (DO NOT distribute)."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta

# Same secret key as validator
_SECRET_KEY = b"vision_agent_secret_key_2025"


class LicenseGenerator:
    """Generate license keys. For admin use only."""

    def __init__(self, secret_key: bytes | None = None):
        self._secret_key = secret_key or _SECRET_KEY

    def create(
        self,
        user_id: str,
        days: int = 30,
        max_devices: int = 1,
        machine_id: str | None = None,
    ) -> str:
        """Create a new license key.

        Args:
            user_id: Customer identifier
            days: Validity period in days
            max_devices: Maximum number of devices
            machine_id: Bind to specific machine (optional)

        Returns:
            License key string
        """
        now = datetime.now()
        data = {
            "user_id": user_id,
            "created_at": now.isoformat(),
            "expires_at": (now + timedelta(days=days)).isoformat(),
            "max_devices": max_devices,
        }
        if machine_id:
            data["machine_id"] = machine_id

        payload = json.dumps(data, separators=(",", ":")).encode()
        payload_b64 = base64.urlsafe_b64encode(payload).decode()
        signature = hmac.new(self._secret_key, payload, hashlib.sha256).hexdigest()[:32]

        return f"{payload_b64}.{signature}"


if __name__ == "__main__":
    # Example usage
    gen = LicenseGenerator()
    key = gen.create(
        user_id="customer_001",
        days=180,
        max_devices=3,
    )
    print(f"License Key:\n{key}")
