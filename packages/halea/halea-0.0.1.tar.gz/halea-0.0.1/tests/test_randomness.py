"""Tests for output randomness quality.

These tests provide additional assurance that the RNG produces properly varied
output. They are NOT statistically rigorous tests (like NIST SP 800-22), but
simple sanity checks that catch obvious failures.
"""

from typing import Any

import numpy as np
import pytest


class TestByteRandomness:
    """Tests for byte output diversity."""

    def test_bytes_has_diverse_values(self, halea_numpy: Any) -> None:
        """Bytes should use most of the byte value range."""
        data = halea_numpy.bytes(1000)
        unique = len(set(data))
        # With 1000 bytes from uniform distribution, expect many unique values
        assert unique > 150

    def test_bytes_not_sequential(self, halea_numpy: Any) -> None:
        """Bytes should not be sequential (0, 1, 2, ...)."""
        data = halea_numpy.bytes(256)
        sequential = bytes(range(256))
        assert data != sequential


class TestBitRandomness:
    """Tests for bit output balance."""

    def test_bits_approximately_balanced(self, halea_numpy: Any) -> None:
        """Bits should be roughly balanced (35-65% ones)."""
        bits = halea_numpy.bits(2000)
        ratio = bits.sum() / len(bits)
        assert 0.35 < ratio < 0.65

    def test_bits_not_alternating(self, halea_numpy: Any) -> None:
        """Bits should not be alternating (0, 1, 0, 1, ...)."""
        bits = halea_numpy.bits(100)
        alternating = np.array([i % 2 for i in range(100)], dtype=np.uint8)
        assert not np.array_equal(bits, alternating)


class TestFloatRandomness:
    """Tests for float output distribution."""

    def test_rand_covers_range(self, halea_numpy: Any) -> None:
        """rand() should cover the [0, 1) range reasonably."""
        samples = halea_numpy.rand(1000)
        # Should have values in different quartiles
        assert np.any(samples < 0.25)
        assert np.any((samples >= 0.25) & (samples < 0.5))
        assert np.any((samples >= 0.5) & (samples < 0.75))
        assert np.any(samples >= 0.75)

    def test_rand_successive_calls_differ(self, halea_numpy: Any) -> None:
        """Successive rand() calls should produce different results."""
        samples = [halea_numpy.rand(50) for _ in range(5)]
        # No consecutive arrays should be identical
        for i in range(len(samples) - 1):
            assert not np.array_equal(samples[i], samples[i + 1])

    def test_randn_has_both_signs(self, halea_numpy: Any) -> None:
        """randn() should produce both positive and negative values."""
        samples = halea_numpy.randn(500)
        assert np.any(samples < 0)
        assert np.any(samples > 0)

    def test_randn_successive_calls_differ(self, halea_numpy: Any) -> None:
        """Successive randn() calls should produce different results."""
        samples = [halea_numpy.randn(50) for _ in range(5)]
        for i in range(len(samples) - 1):
            assert not np.array_equal(samples[i], samples[i + 1])


class TestIntegerRandomness:
    """Tests for integer output distribution."""

    def test_randint_covers_range(self, halea_numpy: Any) -> None:
        """randint() should cover most of the specified range."""
        samples = halea_numpy.randint(0, 10, size=500)
        unique_values = set(samples)
        # With 500 samples from [0, 10), should see most values
        assert len(unique_values) >= 8

    def test_randint_successive_calls_differ(self, halea_numpy: Any) -> None:
        """Successive randint() calls should produce different results."""
        samples = [halea_numpy.randint(0, 1000, size=50) for _ in range(5)]
        for i in range(len(samples) - 1):
            assert not np.array_equal(samples[i], samples[i + 1])


class TestBackendRandomness:
    """Tests for randomness across different backends."""

    @pytest.fixture
    def halea_numpy_truerng_local(self, mock_truerng_all: Any) -> Any:
        """HaleaNumpy with TrueRNG backend."""
        from halea import HaleaNumpy

        rng = HaleaNumpy(backend="truerng")
        rng.connect()
        yield rng
        rng.disconnect()

    @pytest.fixture
    def halea_numpy_chaoskey_local(self, mock_chaoskey_all: Any) -> Any:
        """HaleaNumpy with ChaosKey backend."""
        from halea import HaleaNumpy

        rng = HaleaNumpy(backend="chaoskey")
        rng.connect()
        yield rng
        rng.disconnect()

    def test_truerng_bytes_diverse(self, halea_numpy_truerng_local: Any) -> None:
        """TrueRNG backend should produce diverse bytes."""
        data = halea_numpy_truerng_local.bytes(1000)
        unique = len(set(data))
        assert unique > 150

    def test_chaoskey_bytes_diverse(self, halea_numpy_chaoskey_local: Any) -> None:
        """ChaosKey backend should produce diverse bytes."""
        data = halea_numpy_chaoskey_local.bytes(1000)
        unique = len(set(data))
        assert unique > 150

    def test_truerng_bits_balanced(self, halea_numpy_truerng_local: Any) -> None:
        """TrueRNG backend should produce balanced bits."""
        bits = halea_numpy_truerng_local.bits(2000)
        ratio = bits.sum() / len(bits)
        assert 0.35 < ratio < 0.65

    def test_chaoskey_bits_balanced(self, halea_numpy_chaoskey_local: Any) -> None:
        """ChaosKey backend should produce balanced bits."""
        bits = halea_numpy_chaoskey_local.bits(2000)
        ratio = bits.sum() / len(bits)
        assert 0.35 < ratio < 0.65
