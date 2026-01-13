"""Custom exceptions for halea package."""


class HaleaError(Exception):
    """Base exception for halea package."""


class DeviceNotFoundError(HaleaError):
    """No hardware RNG device found.

    Raised when attempting to connect but no supported device is detected.
    """


class DeviceConnectionError(HaleaError):
    """Failed to connect to hardware RNG device.

    Raised when a device is found but connection cannot be established
    (e.g., permission denied, device busy).
    """


class DeviceReadError(HaleaError):
    """Failed to read from hardware RNG device.

    Raised when reading bytes from the device fails (e.g., timeout,
    device disconnected mid-operation).
    """


class BackendNotAvailableError(HaleaError):
    """Requested backend's dependencies are not installed.

    Raised when a specific backend is requested but its required
    dependencies (pyserial for TrueRNG, pyusb for ChaosKey) are missing.
    """
