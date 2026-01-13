"""Abstract base class for hardware RNG backends."""

from abc import ABC
from abc import abstractmethod
from types import TracebackType
from typing import Self


class HardwareRNGBackend(ABC):
    """Abstract base class for hardware RNG device backends.

    All hardware-specific backends (TrueRNG, ChaosKey) must inherit from
    this class and implement its abstract methods.

    Backends should manage their own internal buffering for efficiency.
    """

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the hardware device.

        Raises:
            DeviceNotFoundError: If no device is found.
            DeviceConnectionError: If connection fails.
        """
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to the hardware device.

        Should be safe to call multiple times.
        """
        ...

    @abstractmethod
    def read_bytes(self, n: int) -> bytes:
        """Read exactly n random bytes from the device.

        Args:
            n: Number of bytes to read.

        Returns:
            Exactly n random bytes.

        Raises:
            DeviceReadError: If reading fails or times out.
        """
        ...

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if device is currently connected."""
        ...

    @property
    @abstractmethod
    def device_info(self) -> dict[str, str | None]:
        """Return device identification info.

        Returns:
            Dictionary with keys like 'type', 'port'/'serial', 'firmware'.
        """
        ...

    @classmethod
    @abstractmethod
    def find_devices(cls) -> list[dict[str, str | int | None]]:
        """Scan for available devices of this type.

        Returns:
            List of device info dictionaries.
        """
        ...

    def __enter__(self) -> Self:
        """Context manager entry - connect to device."""
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Context manager exit - disconnect from device."""
        self.disconnect()
