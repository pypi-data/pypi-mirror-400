"""Tests for halea backend implementations."""

from typing import Any
from unittest.mock import patch

import pytest

from halea.exceptions import DeviceNotFoundError


class TestTrueRNGBackend:
    """Tests for TrueRNGBackend."""

    def test_find_devices_returns_list(self, mock_serial: Any, mock_list_ports_truerng: Any) -> None:
        """find_devices() should return a list."""
        from halea.backends._truerng import TrueRNGBackend

        devices = TrueRNGBackend.find_devices()
        assert isinstance(devices, list)

    def test_find_devices_contains_device_info(self, mock_serial: Any, mock_list_ports_truerng: Any) -> None:
        """find_devices() should return device info dicts."""
        from halea.backends._truerng import TrueRNGBackend

        devices = TrueRNGBackend.find_devices()
        assert len(devices) > 0
        device = devices[0]
        assert "port" in device
        assert "type" in device

    def test_find_devices_empty_when_no_device(self, mock_serial: Any, mock_list_ports_empty: Any) -> None:
        """find_devices() should return empty list when no devices."""
        from halea.backends._truerng import TrueRNGBackend

        devices = TrueRNGBackend.find_devices()
        assert devices == []

    def test_connect_sets_is_connected(self, mock_truerng_all: Any) -> None:
        """connect() should set is_connected to True."""
        from halea.backends._truerng import TrueRNGBackend

        backend = TrueRNGBackend()
        assert not backend.is_connected
        backend.connect()
        assert backend.is_connected
        backend.disconnect()

    def test_disconnect_clears_is_connected(self, mock_truerng_all: Any) -> None:
        """disconnect() should set is_connected to False."""
        from halea.backends._truerng import TrueRNGBackend

        backend = TrueRNGBackend()
        backend.connect()
        assert backend.is_connected
        backend.disconnect()
        assert not backend.is_connected

    def test_disconnect_safe_to_call_multiple_times(self, mock_truerng_all: Any) -> None:
        """disconnect() should be safe to call multiple times."""
        from halea.backends._truerng import TrueRNGBackend

        backend = TrueRNGBackend()
        backend.connect()
        backend.disconnect()
        backend.disconnect()  # Should not raise
        backend.disconnect()  # Should not raise

    def test_read_bytes_returns_correct_length(self, mock_truerng_all: Any) -> None:
        """read_bytes(n) should return exactly n bytes."""
        from halea.backends._truerng import TrueRNGBackend

        backend = TrueRNGBackend()
        backend.connect()
        try:
            for n in [1, 10, 100, 1024, 8192]:
                data = backend.read_bytes(n)
                assert len(data) == n
                assert isinstance(data, bytes)
        finally:
            backend.disconnect()

    def test_read_bytes_not_all_zeros(self, mock_truerng_all: Any) -> None:
        """read_bytes() should return non-trivial data."""
        from halea.backends._truerng import TrueRNGBackend

        backend = TrueRNGBackend()
        backend.connect()
        try:
            data = backend.read_bytes(1024)
            # Should have some non-zero bytes
            assert any(b != 0 for b in data)
        finally:
            backend.disconnect()

    def test_context_manager_connects_and_disconnects(self, mock_truerng_all: Any) -> None:
        """Context manager should connect on enter and disconnect on exit."""
        from halea.backends._truerng import TrueRNGBackend

        backend = TrueRNGBackend()
        assert not backend.is_connected
        with backend:
            assert backend.is_connected
        assert not backend.is_connected

    def test_device_info_populated_after_connect(self, mock_truerng_all: Any) -> None:
        """device_info should be populated after connect."""
        from halea.backends._truerng import TrueRNGBackend

        backend = TrueRNGBackend()
        backend.connect()
        try:
            info = backend.device_info
            assert isinstance(info, dict)
            assert "backend" in info
            assert info["backend"] == "truerng"
        finally:
            backend.disconnect()

    def test_connect_raises_when_no_device(self, mock_serial: Any, mock_list_ports_empty: Any) -> None:
        """connect() should raise DeviceNotFoundError when no device."""
        from halea.backends._truerng import TrueRNGBackend

        backend = TrueRNGBackend()
        with pytest.raises(DeviceNotFoundError):
            backend.connect()


class TestChaosKeyBackend:
    """Tests for ChaosKeyBackend."""

    def test_find_devices_returns_list(self, mock_usb_find: Any, mock_usb_util: Any) -> None:
        """find_devices() should return a list."""
        from halea.backends._chaoskey import ChaosKeyBackend

        devices = ChaosKeyBackend.find_devices()
        assert isinstance(devices, list)

    def test_find_devices_contains_device_info(self, mock_usb_find: Any, mock_usb_util: Any) -> None:
        """find_devices() should return device info dicts."""
        from halea.backends._chaoskey import ChaosKeyBackend

        devices = ChaosKeyBackend.find_devices()
        assert len(devices) > 0
        device = devices[0]
        assert "bus" in device
        assert "address" in device

    def test_find_devices_empty_when_no_device(self, mock_usb_find_empty: Any) -> None:
        """find_devices() should return empty list when no devices."""
        from halea.backends._chaoskey import ChaosKeyBackend

        devices = ChaosKeyBackend.find_devices()
        assert devices == []

    def test_connect_sets_is_connected(self, mock_chaoskey_all: Any) -> None:
        """connect() should set is_connected to True."""
        from halea.backends._chaoskey import ChaosKeyBackend

        backend = ChaosKeyBackend()
        assert not backend.is_connected
        backend.connect()
        assert backend.is_connected
        backend.disconnect()

    def test_disconnect_clears_is_connected(self, mock_chaoskey_all: Any) -> None:
        """disconnect() should set is_connected to False."""
        from halea.backends._chaoskey import ChaosKeyBackend

        backend = ChaosKeyBackend()
        backend.connect()
        assert backend.is_connected
        backend.disconnect()
        assert not backend.is_connected

    def test_disconnect_safe_to_call_multiple_times(self, mock_chaoskey_all: Any) -> None:
        """disconnect() should be safe to call multiple times."""
        from halea.backends._chaoskey import ChaosKeyBackend

        backend = ChaosKeyBackend()
        backend.connect()
        backend.disconnect()
        backend.disconnect()  # Should not raise
        backend.disconnect()  # Should not raise

    def test_read_bytes_returns_correct_length(self, mock_chaoskey_all: Any) -> None:
        """read_bytes(n) should return exactly n bytes."""
        from halea.backends._chaoskey import ChaosKeyBackend

        backend = ChaosKeyBackend()
        backend.connect()
        try:
            for n in [1, 10, 100, 1024, 8192]:
                data = backend.read_bytes(n)
                assert len(data) == n
                assert isinstance(data, bytes)
        finally:
            backend.disconnect()

    def test_read_bytes_not_all_zeros(self, mock_chaoskey_all: Any) -> None:
        """read_bytes() should return non-trivial data."""
        from halea.backends._chaoskey import ChaosKeyBackend

        backend = ChaosKeyBackend()
        backend.connect()
        try:
            data = backend.read_bytes(1024)
            # Should have some non-zero bytes
            assert any(b != 0 for b in data)
        finally:
            backend.disconnect()

    def test_context_manager_connects_and_disconnects(self, mock_chaoskey_all: Any) -> None:
        """Context manager should connect on enter and disconnect on exit."""
        from halea.backends._chaoskey import ChaosKeyBackend

        backend = ChaosKeyBackend()
        assert not backend.is_connected
        with backend:
            assert backend.is_connected
        assert not backend.is_connected

    def test_device_info_populated_after_connect(self, mock_chaoskey_all: Any) -> None:
        """device_info should be populated after connect."""
        from halea.backends._chaoskey import ChaosKeyBackend

        backend = ChaosKeyBackend()
        backend.connect()
        try:
            info = backend.device_info
            assert isinstance(info, dict)
            assert "backend" in info
            assert info["backend"] == "chaoskey"
        finally:
            backend.disconnect()

    def test_connect_raises_when_no_device(self, mock_usb_find_empty: Any) -> None:
        """connect() should raise DeviceNotFoundError when no device."""
        from halea.backends._chaoskey import ChaosKeyBackend

        backend = ChaosKeyBackend()
        with pytest.raises(DeviceNotFoundError):
            backend.connect()


class TestBackendFactory:
    """Tests for backend factory functions."""

    def test_get_backend_explicit_truerng(self, mock_truerng_all: Any) -> None:
        """get_backend('truerng') should return TrueRNGBackend."""
        from halea.backends import get_backend
        from halea.backends._truerng import TrueRNGBackend

        backend = get_backend("truerng")
        assert isinstance(backend, TrueRNGBackend)

    def test_get_backend_explicit_chaoskey(self, mock_chaoskey_all: Any) -> None:
        """get_backend('chaoskey') should return ChaosKeyBackend."""
        from halea.backends import get_backend
        from halea.backends._chaoskey import ChaosKeyBackend

        backend = get_backend("chaoskey")
        assert isinstance(backend, ChaosKeyBackend)

    def test_get_backend_auto_detection_truerng(self, mock_truerng_all: Any) -> None:
        """get_backend(None) should auto-detect TrueRNG."""
        from halea.backends import get_backend
        from halea.backends._truerng import TrueRNGBackend

        # Ensure ChaosKey is not found
        with patch("halea.backends._get_chaoskey_backend") as mock_ck:
            from halea.exceptions import BackendNotAvailableError

            mock_ck.side_effect = BackendNotAvailableError("No ChaosKey")
            backend = get_backend(None)
            assert isinstance(backend, TrueRNGBackend)

    def test_get_backend_raises_on_invalid_name(self) -> None:
        """get_backend() should raise ValueError for invalid backend name."""
        from halea.backends import get_backend

        with pytest.raises(ValueError, match="Unknown backend"):
            get_backend("invalid_backend")

    def test_get_backend_raises_when_no_device(self, mock_list_ports_empty: Any, mock_usb_find_empty: Any) -> None:
        """get_backend(None) should raise DeviceNotFoundError when no device."""
        from halea.backends import get_backend

        with pytest.raises(DeviceNotFoundError):
            get_backend(None)

    def test_find_all_devices_returns_dict(
        self, mock_serial: Any, mock_list_ports_truerng: Any, mock_usb_find: Any, mock_usb_util: Any
    ) -> None:
        """find_all_devices() should return dict with correct keys."""
        from halea.backends import find_all_devices

        result = find_all_devices()
        assert isinstance(result, dict)
        assert "truerng" in result
        assert "chaoskey" in result
        assert isinstance(result["truerng"], list)
        assert isinstance(result["chaoskey"], list)

    def test_find_all_devices_finds_truerng(self, mock_serial: Any, mock_list_ports_truerng: Any) -> None:
        """find_all_devices() should find TrueRNG devices."""
        from halea.backends import find_all_devices

        # Mock ChaosKey to not be available
        with patch("halea.backends._get_chaoskey_backend") as mock_ck:
            from halea.exceptions import BackendNotAvailableError

            mock_ck.side_effect = BackendNotAvailableError("No ChaosKey")
            result = find_all_devices()
            assert len(result["truerng"]) > 0

    def test_find_all_devices_finds_chaoskey(self, mock_usb_find: Any, mock_usb_util: Any) -> None:
        """find_all_devices() should find ChaosKey devices."""
        from halea.backends import find_all_devices

        # Mock TrueRNG to not be available
        with patch("halea.backends._get_truerng_backend") as mock_tr:
            from halea.exceptions import BackendNotAvailableError

            mock_tr.side_effect = BackendNotAvailableError("No TrueRNG")
            result = find_all_devices()
            assert len(result["chaoskey"]) > 0
