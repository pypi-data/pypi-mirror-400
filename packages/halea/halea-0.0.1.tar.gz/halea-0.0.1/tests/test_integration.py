"""Integration tests requiring real hardware.

These tests are marked with @pytest.mark.hardware and are skipped by default.
Run with: pytest -m hardware

These tests require actual TrueRNG or ChaosKey hardware to be connected.
"""

import pytest


pytestmark = pytest.mark.hardware


class TestRealTrueRNG:
    """Integration tests for real TrueRNG hardware."""

    def test_truerng_find_devices(self) -> None:
        """Test that find_devices works with real hardware."""
        try:
            from halea.backends._truerng import TrueRNGBackend
        except ImportError:
            pytest.skip("pyserial not installed")

        devices = TrueRNGBackend.find_devices()
        if not devices:
            pytest.skip("No TrueRNG device found")

        assert isinstance(devices, list)
        assert len(devices) > 0
        assert "port" in devices[0]
        assert "type" in devices[0]

    def test_truerng_connect_and_read(self) -> None:
        """Test connecting and reading from real TrueRNG."""
        try:
            from halea.backends._truerng import TrueRNGBackend
        except ImportError:
            pytest.skip("pyserial not installed")

        devices = TrueRNGBackend.find_devices()
        if not devices:
            pytest.skip("No TrueRNG device found")

        backend = TrueRNGBackend()
        backend.connect()
        try:
            assert backend.is_connected
            data = backend.read_bytes(1024)
            assert len(data) == 1024
            assert isinstance(data, bytes)
            # Verify not all zeros (basic entropy check)
            assert any(b != 0 for b in data)
        finally:
            backend.disconnect()

    def test_truerng_context_manager(self) -> None:
        """Test TrueRNG with context manager."""
        try:
            from halea.backends._truerng import TrueRNGBackend
        except ImportError:
            pytest.skip("pyserial not installed")

        devices = TrueRNGBackend.find_devices()
        if not devices:
            pytest.skip("No TrueRNG device found")

        with TrueRNGBackend() as backend:
            data = backend.read_bytes(100)
            assert len(data) == 100


class TestRealChaosKey:
    """Integration tests for real ChaosKey hardware."""

    def test_chaoskey_find_devices(self) -> None:
        """Test that find_devices works with real hardware."""
        try:
            from halea.backends._chaoskey import ChaosKeyBackend
        except ImportError:
            pytest.skip("pyusb not installed")

        devices = ChaosKeyBackend.find_devices()
        if not devices:
            pytest.skip("No ChaosKey device found")

        assert isinstance(devices, list)
        assert len(devices) > 0
        assert "bus" in devices[0]
        assert "address" in devices[0]

    def test_chaoskey_connect_and_read(self) -> None:
        """Test connecting and reading from real ChaosKey."""
        try:
            from halea.backends._chaoskey import ChaosKeyBackend
        except ImportError:
            pytest.skip("pyusb not installed")

        devices = ChaosKeyBackend.find_devices()
        if not devices:
            pytest.skip("No ChaosKey device found")

        backend = ChaosKeyBackend()
        backend.connect()
        try:
            assert backend.is_connected
            data = backend.read_bytes(1024)
            assert len(data) == 1024
            assert isinstance(data, bytes)
            # Verify not all zeros (basic entropy check)
            assert any(b != 0 for b in data)
        finally:
            backend.disconnect()

    def test_chaoskey_context_manager(self) -> None:
        """Test ChaosKey with context manager."""
        try:
            from halea.backends._chaoskey import ChaosKeyBackend
        except ImportError:
            pytest.skip("pyusb not installed")

        devices = ChaosKeyBackend.find_devices()
        if not devices:
            pytest.skip("No ChaosKey device found")

        with ChaosKeyBackend() as backend:
            data = backend.read_bytes(100)
            assert len(data) == 100


class TestRealHaleaNumpy:
    """Integration tests for HaleaNumpy with real hardware."""

    def test_halea_numpy_auto_detect(self) -> None:
        """Test HaleaNumpy with auto-detection."""
        from halea import HaleaNumpy
        from halea.backends import find_all_devices

        devices = find_all_devices()
        if not devices["truerng"] and not devices["chaoskey"]:
            pytest.skip("No hardware RNG device found")

        with HaleaNumpy() as rng:
            # Test basic operations
            scalar = rng.rand()
            assert 0 <= scalar < 1

            arr = rng.rand(100)
            assert len(arr) == 100
            assert all(0 <= x < 1 for x in arr)

            integers = rng.randint(0, 100, size=50)
            assert len(integers) == 50
            assert all(0 <= x < 100 for x in integers)

            raw_bytes = rng.bytes(256)
            assert len(raw_bytes) == 256
            # Not all zeros
            assert any(b != 0 for b in raw_bytes)

    def test_halea_numpy_explicit_truerng(self) -> None:
        """Test HaleaNumpy with explicit TrueRNG backend."""
        from halea import HaleaNumpy

        try:
            from halea.backends._truerng import TrueRNGBackend

            devices = TrueRNGBackend.find_devices()
            if not devices:
                pytest.skip("No TrueRNG device found")
        except ImportError:
            pytest.skip("pyserial not installed")

        with HaleaNumpy(backend="truerng") as rng:
            result = rng.rand(100)
            assert len(result) == 100

    def test_halea_numpy_explicit_chaoskey(self) -> None:
        """Test HaleaNumpy with explicit ChaosKey backend."""
        from halea import HaleaNumpy

        try:
            from halea.backends._chaoskey import ChaosKeyBackend

            devices = ChaosKeyBackend.find_devices()
            if not devices:
                pytest.skip("No ChaosKey device found")
        except ImportError:
            pytest.skip("pyusb not installed")

        with HaleaNumpy(backend="chaoskey") as rng:
            result = rng.rand(100)
            assert len(result) == 100


class TestRealEntropyQuality:
    """Basic entropy quality tests (not comprehensive statistical tests)."""

    def test_bytes_not_all_same(self) -> None:
        """Bytes should have variation."""
        from halea import HaleaNumpy
        from halea.backends import find_all_devices

        devices = find_all_devices()
        if not devices["truerng"] and not devices["chaoskey"]:
            pytest.skip("No hardware RNG device found")

        with HaleaNumpy() as rng:
            data = rng.bytes(10000)
            # Should have many different byte values
            unique_bytes = len(set(data))
            # At minimum, should have at least 200 unique values (out of 256)
            assert unique_bytes > 200

    def test_bits_approximately_balanced(self) -> None:
        """Bits should be approximately balanced (not a rigorous test)."""
        from halea import HaleaNumpy
        from halea.backends import find_all_devices

        devices = find_all_devices()
        if not devices["truerng"] and not devices["chaoskey"]:
            pytest.skip("No hardware RNG device found")

        with HaleaNumpy() as rng:
            bits = rng.bits(10000)
            ones = bits.sum()
            # Should be roughly balanced (within 10% of 50%)
            ratio = ones / 10000
            assert 0.4 < ratio < 0.6
