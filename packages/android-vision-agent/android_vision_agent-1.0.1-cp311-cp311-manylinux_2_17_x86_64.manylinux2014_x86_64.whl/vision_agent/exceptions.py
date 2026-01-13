"""Vision Agent exceptions."""


class VisionAgentError(Exception):
    """Base exception for Vision Agent."""
    pass


class LicenseError(VisionAgentError):
    """License validation failed."""
    pass


class LicenseExpiredError(LicenseError):
    """License has expired."""
    pass


class LicenseInvalidError(LicenseError):
    """License is invalid or corrupted."""
    pass


class DeviceError(VisionAgentError):
    """Device connection or operation failed."""
    pass


class ModeError(VisionAgentError):
    """Unknown or invalid mode."""
    pass
