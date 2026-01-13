"""ADB device discovery helpers for local and remote devices."""

import subprocess
from dataclasses import dataclass
from enum import Enum


class ConnectionType(Enum):
    """Type of ADB connection."""

    USB = "usb"
    REMOTE = "remote"


@dataclass
class DeviceInfo:
    """Information about a connected device."""

    device_id: str
    status: str
    connection_type: ConnectionType
    model: str | None = None
    android_version: str | None = None


class ADBConnection:
    """Minimal ADB helper for listing connected devices."""

    def __init__(self, adb_path: str = "adb"):
        """
        Initialize ADB connection manager.

        Args:
            adb_path: Path to ADB executable.
        """
        self.adb_path = adb_path

    def list_devices(self) -> list[DeviceInfo]:
        """
        List all connected devices.

        Returns:
            List of DeviceInfo objects.
        """
        try:
            result = subprocess.run(
                [self.adb_path, "devices", "-l"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            devices = []
            for line in result.stdout.strip().split("\n")[1:]:  # Skip header
                if not line.strip():
                    continue

                parts = line.split()
                if len(parts) >= 2:
                    device_id = parts[0]
                    status = parts[1]

                    if ":" in device_id:
                        conn_type = ConnectionType.REMOTE
                    elif "emulator" in device_id:
                        conn_type = ConnectionType.USB
                    else:
                        conn_type = ConnectionType.USB

                    model = None
                    for part in parts[2:]:
                        if part.startswith("model:"):
                            model = part.split(":", 1)[1]
                            break

                    devices.append(
                        DeviceInfo(
                            device_id=device_id,
                            status=status,
                            connection_type=conn_type,
                            model=model,
                        )
                    )

            return devices

        except Exception as e:
            print(f"Error listing devices: {e}")
            return []


def list_devices() -> list[DeviceInfo]:
    """
    Quick helper to list connected devices.

    Returns:
        List of DeviceInfo objects.
    """
    conn = ADBConnection()
    return conn.list_devices()
