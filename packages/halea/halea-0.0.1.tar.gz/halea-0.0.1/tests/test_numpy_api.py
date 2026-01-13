"""Tests for halea NumPy API (HaleaNumpy class and module functions)."""

from typing import Any

import numpy as np
import pytest


class TestRand:
    """Tests for HaleaNumpy.rand()."""

    def test_rand_no_args_returns_scalar(self, halea_numpy: Any) -> None:
        """rand() with no args should return np.float64 scalar."""
        result = halea_numpy.rand()
        assert isinstance(result, np.float64)

    def test_rand_single_dim_returns_1d_array(self, halea_numpy: Any) -> None:
        """rand(n) should return 1D array of shape (n,)."""
        result = halea_numpy.rand(10)
        assert isinstance(result, np.ndarray)
        assert result.shape == (10,)

    def test_rand_multi_dim_returns_nd_array(self, halea_numpy: Any) -> None:
        """rand(m, n, ...) should return array of that shape."""
        result = halea_numpy.rand(3, 4)
        assert result.shape == (3, 4)

        result = halea_numpy.rand(2, 3, 4)
        assert result.shape == (2, 3, 4)

    def test_rand_values_in_range(self, halea_numpy: Any) -> None:
        """All values should be in [0, 1)."""
        result = halea_numpy.rand(1000)
        assert np.all(result >= 0.0)
        assert np.all(result < 1.0)

    def test_rand_dtype_float64(self, halea_numpy: Any) -> None:
        """dtype should be float64."""
        result = halea_numpy.rand(10)
        assert result.dtype == np.float64

    def test_rand_not_all_same(self, halea_numpy: Any) -> None:
        """Values should not all be the same."""
        result = halea_numpy.rand(100)
        assert not np.all(result == result[0])

    def test_rand_negative_shape_raises(self, halea_numpy: Any) -> None:
        """Negative shape should raise ValueError."""
        with pytest.raises(ValueError):
            halea_numpy.rand(-1)


class TestRandn:
    """Tests for HaleaNumpy.randn()."""

    def test_randn_no_args_returns_scalar(self, halea_numpy: Any) -> None:
        """randn() with no args should return np.float64 scalar."""
        result = halea_numpy.randn()
        assert isinstance(result, np.float64)

    def test_randn_single_dim_returns_1d_array(self, halea_numpy: Any) -> None:
        """randn(n) should return 1D array of shape (n,)."""
        result = halea_numpy.randn(10)
        assert isinstance(result, np.ndarray)
        assert result.shape == (10,)

    def test_randn_multi_dim_returns_nd_array(self, halea_numpy: Any) -> None:
        """randn(m, n) should return array of that shape."""
        result = halea_numpy.randn(3, 4)
        assert result.shape == (3, 4)

    def test_randn_dtype_float64(self, halea_numpy: Any) -> None:
        """dtype should be float64."""
        result = halea_numpy.randn(10)
        assert result.dtype == np.float64

    def test_randn_values_finite(self, halea_numpy: Any) -> None:
        """All values should be finite (no NaN or Inf)."""
        result = halea_numpy.randn(1000)
        assert np.all(np.isfinite(result))

    def test_randn_not_all_same(self, halea_numpy: Any) -> None:
        """Values should not all be the same."""
        result = halea_numpy.randn(100)
        assert not np.all(result == result[0])

    def test_randn_negative_shape_raises(self, halea_numpy: Any) -> None:
        """Negative shape should raise ValueError."""
        with pytest.raises(ValueError):
            halea_numpy.randn(-1)


class TestRandint:
    """Tests for HaleaNumpy.randint()."""

    def test_randint_single_arg_range(self, halea_numpy: Any) -> None:
        """randint(n) should return value in [0, n)."""
        for _ in range(100):
            result = halea_numpy.randint(10)
            assert isinstance(result, np.int64)
            assert 0 <= result < 10

    def test_randint_two_arg_range(self, halea_numpy: Any) -> None:
        """randint(low, high) should return value in [low, high)."""
        for _ in range(100):
            result = halea_numpy.randint(5, 15)
            assert 5 <= result < 15

    def test_randint_with_size(self, halea_numpy: Any) -> None:
        """randint with size should return correct shape."""
        result = halea_numpy.randint(100, size=10)
        assert isinstance(result, np.ndarray)
        assert result.shape == (10,)

        result = halea_numpy.randint(0, 100, size=(3, 4))
        assert result.shape == (3, 4)

    def test_randint_values_in_range(self, halea_numpy: Any) -> None:
        """All values should be in [low, high)."""
        result = halea_numpy.randint(10, 50, size=1000)
        assert np.all(result >= 10)
        assert np.all(result < 50)

    def test_randint_dtype_int64(self, halea_numpy: Any) -> None:
        """dtype should be int64."""
        result = halea_numpy.randint(100, size=10)
        assert result.dtype == np.int64

    def test_randint_high_lte_low_raises(self, halea_numpy: Any) -> None:
        """high <= low should raise ValueError."""
        with pytest.raises(ValueError):
            halea_numpy.randint(10, 5)
        with pytest.raises(ValueError):
            halea_numpy.randint(10, 10)

    def test_randint_unbiased_mode(self, mock_truerng_all: Any) -> None:
        """Unbiased mode should work."""
        from halea import HaleaNumpy

        rng = HaleaNumpy(unbiased=True)
        rng.connect()
        try:
            result = rng.randint(0, 100, size=100)
            assert np.all(result >= 0)
            assert np.all(result < 100)
        finally:
            rng.disconnect()


class TestChoice:
    """Tests for HaleaNumpy.choice()."""

    def test_choice_from_int(self, halea_numpy: Any) -> None:
        """choice(n) should return value in [0, n)."""
        for _ in range(100):
            result = halea_numpy.choice(10)
            assert 0 <= result < 10

    def test_choice_from_array(self, halea_numpy: Any) -> None:
        """choice(array) should return element from array."""
        arr = np.array([10, 20, 30, 40, 50])
        for _ in range(100):
            result = halea_numpy.choice(arr)
            assert result in arr

    def test_choice_with_size(self, halea_numpy: Any) -> None:
        """choice with size should return correct shape."""
        result = halea_numpy.choice(10, size=5)
        assert result.shape == (5,)

    def test_choice_with_replacement(self, halea_numpy: Any) -> None:
        """With replacement, size can exceed population."""
        result = halea_numpy.choice(5, size=100, replace=True)
        assert len(result) == 100

    def test_choice_without_replacement_unique(self, halea_numpy: Any) -> None:
        """Without replacement, all values should be unique."""
        result = halea_numpy.choice(100, size=50, replace=False)
        assert len(result) == 50
        assert len(np.unique(result)) == 50

    def test_choice_without_replacement_size_exceeds_raises(self, halea_numpy: Any) -> None:
        """Without replacement, size > population should raise."""
        with pytest.raises(ValueError):
            halea_numpy.choice(5, size=10, replace=False)

    def test_choice_empty_array_raises(self, halea_numpy: Any) -> None:
        """Choosing from empty array should raise."""
        with pytest.raises(ValueError):
            halea_numpy.choice(np.array([]))


class TestBytes:
    """Tests for HaleaNumpy.bytes()."""

    def test_bytes_returns_bytes_type(self, halea_numpy: Any) -> None:
        """bytes() should return bytes type."""
        result = halea_numpy.bytes(10)
        assert isinstance(result, bytes)

    def test_bytes_correct_length(self, halea_numpy: Any) -> None:
        """bytes(n) should return exactly n bytes."""
        for n in [1, 10, 100, 1024]:
            result = halea_numpy.bytes(n)
            assert len(result) == n

    def test_bytes_not_all_zeros(self, halea_numpy: Any) -> None:
        """bytes() should return non-trivial data."""
        result = halea_numpy.bytes(1024)
        assert any(b != 0 for b in result)

    def test_bytes_zero_returns_empty(self, halea_numpy: Any) -> None:
        """bytes(0) should return empty bytes."""
        result = halea_numpy.bytes(0)
        assert result == b""

    def test_bytes_negative_raises(self, halea_numpy: Any) -> None:
        """bytes(negative) should raise ValueError."""
        with pytest.raises(ValueError):
            halea_numpy.bytes(-1)


class TestBits:
    """Tests for HaleaNumpy.bits()."""

    def test_bits_returns_array(self, halea_numpy: Any) -> None:
        """bits() should return np.ndarray."""
        result = halea_numpy.bits(10)
        assert isinstance(result, np.ndarray)

    def test_bits_correct_length(self, halea_numpy: Any) -> None:
        """bits(n) should return exactly n bits."""
        for n in [1, 8, 10, 100]:
            result = halea_numpy.bits(n)
            assert len(result) == n

    def test_bits_only_zeros_and_ones(self, halea_numpy: Any) -> None:
        """All values should be 0 or 1."""
        result = halea_numpy.bits(1000)
        assert np.all((result == 0) | (result == 1))

    def test_bits_dtype_uint8(self, halea_numpy: Any) -> None:
        """dtype should be uint8."""
        result = halea_numpy.bits(10)
        assert result.dtype == np.uint8

    def test_bits_has_both_values(self, halea_numpy: Any) -> None:
        """Should have both 0s and 1s (not all same)."""
        result = halea_numpy.bits(1000)
        assert np.any(result == 0)
        assert np.any(result == 1)

    def test_bits_zero_returns_empty(self, halea_numpy: Any) -> None:
        """bits(0) should return empty array."""
        result = halea_numpy.bits(0)
        assert len(result) == 0

    def test_bits_negative_raises(self, halea_numpy: Any) -> None:
        """bits(negative) should raise ValueError."""
        with pytest.raises(ValueError):
            halea_numpy.bits(-1)


class TestShuffle:
    """Tests for HaleaNumpy.shuffle()."""

    def test_shuffle_list_in_place(self, halea_numpy: Any) -> None:
        """shuffle() should modify list in place."""
        lst = [1, 2, 3, 4, 5]
        original = lst.copy()
        halea_numpy.shuffle(lst)
        # Same elements
        assert sorted(lst) == sorted(original)

    def test_shuffle_array_in_place(self, halea_numpy: Any) -> None:
        """shuffle() should modify array in place."""
        arr = np.arange(20)
        original = arr.copy()
        halea_numpy.shuffle(arr)
        # Same elements
        assert set(arr) == set(original)

    def test_shuffle_preserves_elements(self, halea_numpy: Any) -> None:
        """shuffle() should preserve all elements."""
        arr = np.array([10, 20, 30, 40, 50])
        halea_numpy.shuffle(arr)
        assert set(arr) == {10, 20, 30, 40, 50}

    def test_shuffle_returns_none(self, halea_numpy: Any) -> None:
        """shuffle() should return None."""
        arr = np.arange(10)
        result = halea_numpy.shuffle(arr)
        assert result is None

    def test_shuffle_single_element(self, halea_numpy: Any) -> None:
        """shuffle() on single element should be no-op."""
        arr = np.array([42])
        halea_numpy.shuffle(arr)
        assert arr[0] == 42

    def test_shuffle_empty(self, halea_numpy: Any) -> None:
        """shuffle() on empty should be no-op."""
        arr = np.array([])
        halea_numpy.shuffle(arr)
        assert len(arr) == 0

    def test_shuffle_changes_order(self, halea_numpy: Any) -> None:
        """shuffle() should change the order of elements (usually)."""
        # Use a large enough array that order change is very likely
        arr = np.arange(50)
        original = arr.copy()
        halea_numpy.shuffle(arr)
        # Very unlikely to be in original order after shuffle
        assert not np.array_equal(arr, original)


class TestPermutation:
    """Tests for HaleaNumpy.permutation()."""

    def test_permutation_int_returns_array(self, halea_numpy: Any) -> None:
        """permutation(n) should return array of length n."""
        result = halea_numpy.permutation(10)
        assert isinstance(result, np.ndarray)
        assert len(result) == 10

    def test_permutation_int_is_permutation(self, halea_numpy: Any) -> None:
        """permutation(n) should be a permutation of range(n)."""
        result = halea_numpy.permutation(10)
        assert set(result) == set(range(10))

    def test_permutation_array_returns_copy(self, halea_numpy: Any) -> None:
        """permutation(array) should return shuffled copy."""
        arr = np.array([10, 20, 30, 40, 50])
        original = arr.copy()
        result = halea_numpy.permutation(arr)
        # Original unchanged
        assert np.array_equal(arr, original)
        # Result has same elements
        assert set(result) == set(arr)

    def test_permutation_preserves_elements(self, halea_numpy: Any) -> None:
        """permutation() should preserve all elements."""
        arr = np.array([1, 2, 3, 4, 5])
        result = halea_numpy.permutation(arr)
        assert set(result) == set(arr)

    def test_permutation_changes_order(self, halea_numpy: Any) -> None:
        """permutation() should change the order (usually)."""
        # Use a large enough value that order change is very likely
        result = halea_numpy.permutation(50)
        original = np.arange(50)
        # Very unlikely to be in original order after permutation
        assert not np.array_equal(result, original)


class TestContextManager:
    """Tests for HaleaNumpy context manager."""

    def test_context_manager_connects(self, mock_truerng_all: Any) -> None:
        """Context manager should connect on enter."""
        from halea import HaleaNumpy

        with HaleaNumpy() as rng:
            # Should be able to generate numbers
            result = rng.rand(10)
            assert len(result) == 10

    def test_context_manager_disconnects(self, mock_truerng_all: Any) -> None:
        """Context manager should disconnect on exit."""
        from halea import HaleaNumpy

        rng = HaleaNumpy()
        with rng:
            pass
        # After exiting context, device_info should reflect disconnected state
        assert rng._backend is None

    def test_explicit_connect_disconnect(self, mock_truerng_all: Any) -> None:
        """Manual connect/disconnect should work."""
        from halea import HaleaNumpy

        rng = HaleaNumpy()
        rng.connect()
        result = rng.rand(10)
        assert len(result) == 10
        rng.disconnect()


class TestModuleFunctions:
    """Tests for module-level convenience functions."""

    def test_module_rand(self, mock_truerng_all: Any, reset_global_rng: None) -> None:
        """halea.rand() should work."""
        from halea import rand

        result = rand(10)
        assert len(result) == 10
        assert np.all(result >= 0)
        assert np.all(result < 1)

    def test_module_randn(self, mock_truerng_all: Any, reset_global_rng: None) -> None:
        """halea.randn() should work."""
        from halea.numpy import randn

        result = randn(10)
        assert len(result) == 10
        assert np.all(np.isfinite(result))

    def test_module_randint(self, mock_truerng_all: Any, reset_global_rng: None) -> None:
        """halea.randint() should work."""
        from halea import randint

        result = randint(0, 100, size=10)
        assert len(result) == 10
        assert np.all(result >= 0)
        assert np.all(result < 100)

    def test_module_choice(self, mock_truerng_all: Any, reset_global_rng: None) -> None:
        """halea.choice() should work."""
        from halea import choice

        result = choice(10, size=5)
        assert len(result) == 5

    def test_module_bytes(self, mock_truerng_all: Any, reset_global_rng: None) -> None:
        """halea.bytes() should work."""
        from halea import bytes as halea_bytes

        result = halea_bytes(16)
        assert isinstance(result, bytes)
        assert len(result) == 16

    def test_module_bits(self, mock_truerng_all: Any, reset_global_rng: None) -> None:
        """halea.bits() should work."""
        from halea import bits

        result = bits(64)
        assert len(result) == 64

    def test_module_shuffle(self, mock_truerng_all: Any, reset_global_rng: None) -> None:
        """halea.shuffle() should work."""
        from halea import shuffle

        arr = list(range(10))
        shuffle(arr)
        assert sorted(arr) == list(range(10))

    def test_module_permutation(self, mock_truerng_all: Any, reset_global_rng: None) -> None:
        """halea.permutation() should work."""
        from halea import permutation

        result = permutation(10)
        assert set(result) == set(range(10))


class TestDeviceInfo:
    """Tests for device_info property."""

    def test_device_info_before_connect(self, mock_truerng_all: Any) -> None:
        """device_info before connect should indicate not connected."""
        from halea import HaleaNumpy

        rng = HaleaNumpy()
        info = rng.device_info
        assert info["backend"] is None

    def test_device_info_after_connect(self, halea_numpy: Any) -> None:
        """device_info after connect should have backend info."""
        info = halea_numpy.device_info
        assert info["backend"] is not None


class TestRepr:
    """Tests for __repr__ method."""

    def test_repr_not_connected(self, mock_truerng_all: Any) -> None:
        """repr should indicate not connected state."""
        from halea import HaleaNumpy

        rng = HaleaNumpy()
        repr_str = repr(rng)
        assert "not connected" in repr_str

    def test_repr_connected(self, halea_numpy: Any) -> None:
        """repr should indicate connected state."""
        repr_str = repr(halea_numpy)
        assert "connected" in repr_str
