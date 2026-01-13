"""ChaosKey hardware backend using pyusb."""

from types import TracebackType
from typing import Self

import usb.core
import usb.util

from halea._base import HardwareRNGBackend
from halea.exceptions import DeviceConnectionError
from halea.exceptions import DeviceNotFoundError
from halea.exceptions import DeviceReadError

# ChaosKey USB identifiers
CHAOSKEY_VID: int = 0x1D50
CHAOSKEY_PID: int = 0x60C6

# USB endpoint for cooked (whitened) random bytes
ENDPOINT_COOKED: int = 0x85

# USB communication parameters
USB_TIMEOUT_MS: int = 10_000  # 10 second timeout
BULK_TRANSFER_SIZE: int = 1024  # Optimal bulk transfer chunk size


class ChaosKeyBackend(HardwareRNGBackend):
    """Hardware RNG backend for ChaosKey devices.

    Uses USB bulk transfers to read whitened random bytes from
    the cooked endpoint (0x85).
    """

    def __init__(
        self,
        serial: str | None = None,
        buffer_size: int = 8192,
    ) -> None:
        """Initialize ChaosKey backend.

        Args:
            serial: Device serial number. First device if None.
            buffer_size: Internal buffer size for efficient reads.
        """
        self._serial_filter = serial
        self._buffer_size = buffer_size
        self._device: usb.core.Device | None = None
        self._buffer = b""
        self._connected = False
        self._kernel_was_active = False
        self._interface = 0
        self._device_serial: str | None = None

    @classmethod
    def find_devices(cls) -> list[dict[str, str | int | None]]:
        """Scan for connected ChaosKey devices.

        Returns:
            List of dicts with 'bus', 'address', 'serial' for each device.
        """
        devices: list[dict[str, str | int | None]] = []

        for dev in usb.core.find(find_all=True, idVendor=CHAOSKEY_VID, idProduct=CHAOSKEY_PID):
            try:
                serial = usb.util.get_string(dev, dev.iSerialNumber)
            except (usb.core.USBError, ValueError):
                serial = None

            devices.append({
                "bus": dev.bus,
                "address": dev.address,
                "serial": serial,
            })

        return devices

    def connect(self) -> None:
        """Establish connection to the ChaosKey device."""
        if self._connected:
            return

        # Find device, optionally filtering by serial
        if self._serial_filter:
            devices = list(usb.core.find(find_all=True, idVendor=CHAOSKEY_VID, idProduct=CHAOSKEY_PID))
            for dev in devices:
                try:
                    dev_serial = usb.util.get_string(dev, dev.iSerialNumber)
                    if dev_serial == self._serial_filter:
                        self._device = dev
                        self._device_serial = dev_serial
                        break
                except (usb.core.USBError, ValueError):
                    continue
        else:
            self._device = usb.core.find(idVendor=CHAOSKEY_VID, idProduct=CHAOSKEY_PID)
            if self._device is not None:
                try:
                    self._device_serial = usb.util.get_string(self._device, self._device.iSerialNumber)
                except (usb.core.USBError, ValueError):
                    self._device_serial = None

        if self._device is None:
            if self._serial_filter:
                raise DeviceNotFoundError(f"No ChaosKey device with serial '{self._serial_filter}' found.")
            raise DeviceNotFoundError("No ChaosKey device found. Check USB connection and udev rules for permissions.")

        # Detach kernel driver if active (Linux-specific)
        try:
            if self._device.is_kernel_driver_active(self._interface):
                self._device.detach_kernel_driver(self._interface)
                self._kernel_was_active = True
        except (usb.core.USBError, NotImplementedError):
            pass  # Not supported on all platforms

        # Claim interface
        try:
            usb.util.claim_interface(self._device, self._interface)
            self._connected = True
        except usb.core.USBError as e:
            if e.errno == 13:  # Permission denied
                raise DeviceConnectionError(
                    f"Permission denied accessing ChaosKey. "
                    f"Install udev rules: "
                    f"sudo cp 99-chaoskey.rules /etc/udev/rules.d/"
                ) from e
            raise DeviceConnectionError(f"Failed to claim ChaosKey interface: {e}") from e

    def disconnect(self) -> None:
        """Close connection to the ChaosKey device."""
        if self._device is not None:
            try:
                usb.util.release_interface(self._device, self._interface)
            except usb.core.USBError:
                pass
            if self._kernel_was_active:
                try:
                    self._device.attach_kernel_driver(self._interface)
                except usb.core.USBError:
                    pass
            try:
                usb.util.dispose_resources(self._device)
            except usb.core.USBError:
                pass
            self._device = None
        self._connected = False
        self._kernel_was_active = False
        self._buffer = b""

    def read_bytes(self, n: int) -> bytes:
        """Read exactly n random bytes from the device.

        Args:
            n: Number of bytes to read.

        Returns:
            Exactly n random bytes.

        Raises:
            DeviceReadError: If reading fails or times out.
        """
        if not self._connected:
            self.connect()

        if self._device is None:
            raise DeviceReadError("Device not connected")

        # Refill buffer if needed
        try:
            while len(self._buffer) < n:
                # Always read full bulk transfer size for consistent USB performance
                chunk_size = BULK_TRANSFER_SIZE
                data = self._device.read(ENDPOINT_COOKED, chunk_size, timeout=USB_TIMEOUT_MS)
                if not data:
                    raise DeviceReadError("No data received from ChaosKey")
                self._buffer += bytes(data)
        except usb.core.USBTimeoutError as e:
            self._buffer = b""  # Clear stale data on error
            raise DeviceReadError(f"Timeout reading from ChaosKey: {e}") from e
        except usb.core.USBError as e:
            self._buffer = b""  # Clear stale data on error
            raise DeviceReadError(f"USB error reading from ChaosKey: {e}") from e
        except DeviceReadError:
            self._buffer = b""  # Clear stale data on error
            raise

        # Extract requested bytes
        result = self._buffer[:n]
        self._buffer = self._buffer[n:]
        return result

    @property
    def is_connected(self) -> bool:
        """Check if device is currently connected."""
        return self._connected

    @property
    def device_info(self) -> dict[str, str | None]:
        """Return device identification info."""
        return {
            "backend": "chaoskey",
            "type": "ChaosKey",
            "serial": self._device_serial,
        }

    def __repr__(self) -> str:
        """Return string representation."""
        status = "connected" if self._connected else "disconnected"
        serial = self._device_serial or self._serial_filter or "auto"
        return f"ChaosKeyBackend(serial={serial!r}, {status})"

    def __enter__(self) -> Self:
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Context manager exit."""
        self.disconnect()
