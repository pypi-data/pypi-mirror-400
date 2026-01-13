"""Backend factory and device detection for halea.

This module provides:
- `get_backend()`: Factory function to create backend instances
- `find_all_devices()`: Scan for all available hardware RNG devices
- Backend classes: `TrueRNGBackend`, `ChaosKeyBackend`
"""

from halea._base import HardwareRNGBackend
from halea.exceptions import BackendNotAvailableError
from halea.exceptions import DeviceNotFoundError

__all__ = [
    "HardwareRNGBackend",
    "TrueRNGBackend",
    "ChaosKeyBackend",
    "get_backend",
    "find_all_devices",
]


# Lazy imports to handle missing dependencies gracefully
def _get_truerng_backend() -> type:
    """Get TrueRNGBackend class, raising if pyserial unavailable."""
    try:
        from halea.backends._truerng import TrueRNGBackend

        return TrueRNGBackend
    except ImportError as e:
        raise BackendNotAvailableError("TrueRNG backend requires pyserial. Install with: pip install pyserial") from e


def _get_chaoskey_backend() -> type:
    """Get ChaosKeyBackend class, raising if pyusb unavailable."""
    try:
        from halea.backends._chaoskey import ChaosKeyBackend

        return ChaosKeyBackend
    except ImportError as e:
        raise BackendNotAvailableError("ChaosKey backend requires pyusb. Install with: pip install pyusb") from e


# Try to import for module-level exports (may be None if deps missing)
try:
    from halea.backends._truerng import TrueRNGBackend
except ImportError:
    TrueRNGBackend = None  # type: ignore[misc, assignment]

try:
    from halea.backends._chaoskey import ChaosKeyBackend
except ImportError:
    ChaosKeyBackend = None  # type: ignore[misc, assignment]


def find_all_devices() -> dict[str, list[dict[str, str | int | None]]]:
    """Scan for all available hardware RNG devices.

    Returns:
        Dictionary with keys 'truerng' and 'chaoskey', each containing
        a list of device info dictionaries.

    Example:
        >>> find_all_devices()
        {
            'truerng': [{'port': '/dev/ttyACM0', 'type': 'TrueRNGproV2', ...}],
            'chaoskey': [{'bus': 1, 'address': 5, 'serial': 'ABC123'}],
        }
    """
    result: dict[str, list[dict[str, str | int | None]]] = {
        "truerng": [],
        "chaoskey": [],
    }

    # Scan for TrueRNG devices
    try:
        backend_cls = _get_truerng_backend()
        result["truerng"] = backend_cls.find_devices()
    except BackendNotAvailableError:
        pass

    # Scan for ChaosKey devices
    try:
        backend_cls = _get_chaoskey_backend()
        result["chaoskey"] = backend_cls.find_devices()
    except BackendNotAvailableError:
        pass

    return result


def get_backend(
    backend: str | None = None,
    *,
    # TrueRNG-specific
    port: str | None = None,
    # ChaosKey-specific
    serial: str | None = None,
    # Common
    buffer_size: int = 8192,
) -> HardwareRNGBackend:
    """Get a hardware RNG backend.

    Args:
        backend: Backend type - "truerng", "chaoskey", or None for auto-detect.
        port: Serial port for TrueRNG (auto-detected if None).
        serial: Serial number for ChaosKey (first device if None).
        buffer_size: Internal buffer size for efficient reads.

    Returns:
        A HardwareRNGBackend instance (not yet connected).

    Raises:
        DeviceNotFoundError: If no device found during auto-detection.
        BackendNotAvailableError: If requested backend's dependencies missing.
        ValueError: If backend name is invalid.

    Example:
        >>> # Auto-detect any available device
        >>> with get_backend() as rng:
        ...     data = rng.read_bytes(1024)

        >>> # Explicitly use TrueRNG
        >>> with get_backend(backend="truerng") as rng:
        ...     data = rng.read_bytes(1024)

        >>> # Use specific ChaosKey by serial number
        >>> with get_backend(backend="chaoskey", serial="ABC123") as rng:
        ...     data = rng.read_bytes(1024)
    """
    if backend == "truerng":
        backend_cls = _get_truerng_backend()
        return backend_cls(port=port, buffer_size=buffer_size)

    elif backend == "chaoskey":
        backend_cls = _get_chaoskey_backend()
        return backend_cls(serial=serial, buffer_size=buffer_size)

    elif backend is None:
        # Auto-detect: try TrueRNG first, then ChaosKey
        errors: list[str] = []

        # Try TrueRNG
        try:
            truerng_cls = _get_truerng_backend()
            devices = truerng_cls.find_devices()
            if devices:
                return truerng_cls(port=port, buffer_size=buffer_size)
        except BackendNotAvailableError as e:
            errors.append(str(e))

        # Try ChaosKey
        try:
            chaoskey_cls = _get_chaoskey_backend()
            devices = chaoskey_cls.find_devices()
            if devices:
                return chaoskey_cls(serial=serial, buffer_size=buffer_size)
        except BackendNotAvailableError as e:
            errors.append(str(e))

        # No device found
        if errors:
            raise DeviceNotFoundError(
                "No hardware RNG device found. Backend errors:\n" + "\n".join(f"  - {e}" for e in errors)
            )
        raise DeviceNotFoundError(
            "No hardware RNG device found. Supported devices: TrueRNG V1/V2/V3, TrueRNGpro V1/V2, ChaosKey."
        )

    else:
        raise ValueError(f"Unknown backend: '{backend}'. Valid options: 'truerng', 'chaoskey', None")
