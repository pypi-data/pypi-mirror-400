"""TrueRNG hardware backend using pyserial."""

import os
import stat
import sys
import time
from types import TracebackType
from typing import Self

import serial
from serial.tools import list_ports

from halea._base import HardwareRNGBackend
from halea.exceptions import DeviceConnectionError
from halea.exceptions import DeviceNotFoundError
from halea.exceptions import DeviceReadError

# Import termios only on Linux
if sys.platform == "linux":
    import termios

# USB Vendor/Product IDs for device identification
TRUERNG_VID_PID = "04D8:F5FE"  # TrueRNG V1/V2/V3
TRUERNGPRO_VID_PID = "16D0:0AA0"  # TrueRNGpro V1
TRUERNGPROV2_VID_PID = "04D8:EBB5"  # TrueRNGpro V2

# Mode baudrate for normal (whitened) output
MODE_NORMAL_BAUDRATE = 300

# Timeout for serial reads (seconds)
READ_TIMEOUT = 10


def _mode_change(port: str) -> bool:
    """Switch TrueRNGpro/V2 to MODE_NORMAL using baudrate knock sequence.

    Note: TrueRNG V1/V2/V3 devices do not support mode changes and will
    ignore this sequence (they only have normal mode).

    Args:
        port: Serial port path.

    Returns:
        True if mode change sequence completed.

    Raises:
        serial.SerialException: If serial port operations fail.
    """
    # "Knock" sequence: 110 -> 300 -> 110 -> target
    for baudrate in [110, 300, 110, MODE_NORMAL_BAUDRATE]:
        ser = serial.Serial(port=port, baudrate=baudrate, timeout=1)
        time.sleep(0.5 if baudrate == 110 else 0)
        ser.close()
    return True


def _reset_serial_port(port: str) -> None:
    """Reset serial port settings on Linux using termios.

    pyserial may leave the port in a non-standard state; this resets it.
    Only has effect on Linux systems.

    Args:
        port: Serial port path to reset.
    """
    if sys.platform != "linux":
        return
    try:
        with open(port) as f:
            attrs = termios.tcgetattr(f)
            attrs[6][termios.VMIN] = 1
            termios.tcsetattr(f, termios.TCSANOW, attrs)
    except (OSError, termios.error):
        pass


def _validate_port(port: str) -> None:
    """Validate port is a character device.

    Args:
        port: Serial port path to validate.

    Raises:
        ValueError: If port is not in /dev/ or not a character device.
        DeviceNotFoundError: If port cannot be accessed.
    """
    if sys.platform != "linux":
        return  # Skip validation on non-Linux
    if not port.startswith("/dev/"):
        raise ValueError(f"Port must be in /dev/: {port}")
    try:
        mode = os.stat(port).st_mode
        if not stat.S_ISCHR(mode):
            raise ValueError(f"Port is not a character device: {port}")
    except OSError as e:
        raise DeviceNotFoundError(f"Cannot access port {port}: {e}") from e


class TrueRNGBackend(HardwareRNGBackend):
    """Hardware RNG backend for TrueRNG devices.

    Supports TrueRNG V1/V2/V3 and TrueRNGpro V1/V2 devices connected
    via USB serial (CDC ACM).
    """

    def __init__(
        self,
        port: str | None = None,
        buffer_size: int = 8192,
    ) -> None:
        """Initialize TrueRNG backend.

        Args:
            port: Serial port path (e.g., "/dev/ttyACM0").
                  Auto-detected if None.
            buffer_size: Internal buffer size for efficient reads.
        """
        self._port = port
        self._buffer_size = buffer_size
        self._ser: serial.Serial | None = None
        self._buffer = b""
        self._connected = False
        self._device_type: str | None = None

    @classmethod
    def find_devices(cls) -> list[dict[str, str | int | None]]:
        """Scan for connected TrueRNG devices.

        Returns:
            List of dicts with 'port', 'type', 'serial_number' for each device.
        """
        devices: list[dict[str, str | int | None]] = []
        ports_available = list_ports.comports()

        for port_info in ports_available:
            hwid = port_info.hwid
            device_type: str | None = None

            if TRUERNG_VID_PID in hwid:
                device_type = "TrueRNG"
            elif TRUERNGPRO_VID_PID in hwid:
                device_type = "TrueRNGpro"
            elif TRUERNGPROV2_VID_PID in hwid:
                device_type = "TrueRNGproV2"

            if device_type:
                devices.append({
                    "port": port_info.device,
                    "type": device_type,
                    "serial_number": port_info.serial_number,
                })

        return devices

    def connect(self) -> None:
        """Establish connection to the TrueRNG device."""
        if self._connected:
            return

        # Find device if port not specified
        if self._port is None:
            devices = self.find_devices()
            if not devices:
                raise DeviceNotFoundError("No TrueRNG device found. Supported: TrueRNG V1/V2/V3, TrueRNGpro V1/V2.")
            self._port = str(devices[0]["port"])
            self._device_type = str(devices[0]["type"])
        else:
            # Validate port is a TrueRNG device
            devices = self.find_devices()
            for dev in devices:
                if dev["port"] == self._port:
                    self._device_type = str(dev["type"])
                    break
            else:
                self._device_type = "TrueRNG"  # Assume if explicitly specified

        # Validate port is a real character device (SEC-1)
        _validate_port(self._port)

        # Switch to normal mode (no-op for TrueRNG V1/V2/V3)
        try:
            _mode_change(self._port)
        except serial.SerialException as e:
            raise DeviceConnectionError(f"Failed to switch mode on {self._port}: {e}") from e

        # Open serial connection
        try:
            self._ser = serial.Serial(port=self._port, timeout=READ_TIMEOUT)
            if not self._ser.is_open:
                self._ser.open()
            self._ser.setDTR(True)
            self._ser.reset_input_buffer()
            self._connected = True
        except serial.SerialException as e:
            raise DeviceConnectionError(
                f"Failed to open {self._port}: {e}. Check permissions (you may need udev rules)."
            ) from e

    def disconnect(self) -> None:
        """Close connection to the TrueRNG device."""
        if self._ser is not None:
            try:
                self._ser.close()
            except serial.SerialException:
                pass
            self._ser = None
        if self._port is not None and self._connected:
            _reset_serial_port(self._port)
        self._connected = False
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

        if self._ser is None:
            raise DeviceReadError("Device not connected")

        # Refill buffer if needed
        try:
            while len(self._buffer) < n:
                chunk = self._ser.read(self._buffer_size)
                if not chunk:
                    raise DeviceReadError(f"Timeout reading from TrueRNG on {self._port}")
                self._buffer += chunk
        except serial.SerialException as e:
            self._buffer = b""  # Clear stale data on error
            raise DeviceReadError(f"Read error on {self._port}: {e}") from e
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
            "backend": "truerng",
            "type": self._device_type,
            "port": self._port,
        }

    def __repr__(self) -> str:
        """Return string representation."""
        status = "connected" if self._connected else "disconnected"
        port = self._port or "auto"
        return f"TrueRNGBackend(port={port!r}, {status})"

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
