"""Tests for halea PyTorch API (HaleaTorch class)."""

from typing import Any

import numpy as np
import pytest

# Skip all tests if torch is not available
torch = pytest.importorskip("torch")


class TestTorchRand:
    """Tests for HaleaTorch.rand()."""

    def test_rand_returns_tensor(self, halea_torch: Any) -> None:
        """rand() should return torch.Tensor."""
        result = halea_torch.rand(10)
        assert isinstance(result, torch.Tensor)

    def test_rand_no_args_returns_scalar(self, halea_torch: Any) -> None:
        """rand() with no args should return scalar tensor."""
        result = halea_torch.rand()
        assert result.ndim == 0

    def test_rand_shape_correct(self, halea_torch: Any) -> None:
        """rand() should return correct shape."""
        result = halea_torch.rand(10)
        assert result.shape == (10,)

        result = halea_torch.rand(3, 4)
        assert result.shape == (3, 4)

    def test_rand_values_in_range(self, halea_torch: Any) -> None:
        """All values should be in [0, 1)."""
        result = halea_torch.rand(1000)
        assert torch.all(result >= 0.0)
        assert torch.all(result < 1.0)

    def test_rand_dtype_default_float64(self, halea_torch: Any) -> None:
        """Default dtype should be float64."""
        result = halea_torch.rand(10)
        assert result.dtype == torch.float64

    def test_rand_dtype_float32(self, halea_torch: Any) -> None:
        """Custom dtype float32 should work."""
        result = halea_torch.rand(10, dtype=torch.float32)
        assert result.dtype == torch.float32

    def test_rand_not_all_same(self, halea_torch: Any) -> None:
        """Values should not all be the same."""
        result = halea_torch.rand(100)
        assert not torch.all(result == result[0])


class TestTorchRandn:
    """Tests for HaleaTorch.randn()."""

    def test_randn_returns_tensor(self, halea_torch: Any) -> None:
        """randn() should return torch.Tensor."""
        result = halea_torch.randn(10)
        assert isinstance(result, torch.Tensor)

    def test_randn_no_args_returns_scalar(self, halea_torch: Any) -> None:
        """randn() with no args should return scalar tensor."""
        result = halea_torch.randn()
        assert result.ndim == 0

    def test_randn_shape_correct(self, halea_torch: Any) -> None:
        """randn() should return correct shape."""
        result = halea_torch.randn(10)
        assert result.shape == (10,)

        result = halea_torch.randn(3, 4)
        assert result.shape == (3, 4)

    def test_randn_values_finite(self, halea_torch: Any) -> None:
        """All values should be finite (no NaN or Inf)."""
        result = halea_torch.randn(1000)
        assert torch.all(torch.isfinite(result))

    def test_randn_dtype_default_float64(self, halea_torch: Any) -> None:
        """Default dtype should be float64."""
        result = halea_torch.randn(10)
        assert result.dtype == torch.float64


class TestTorchRandint:
    """Tests for HaleaTorch.randint()."""

    def test_randint_returns_tensor(self, halea_torch: Any) -> None:
        """randint() should return torch.Tensor."""
        result = halea_torch.randint(10, size=(5,))
        assert isinstance(result, torch.Tensor)

    def test_randint_values_in_range(self, halea_torch: Any) -> None:
        """All values should be in [low, high)."""
        result = halea_torch.randint(10, 50, size=(100,))
        assert torch.all(result >= 10)
        assert torch.all(result < 50)

    def test_randint_dtype_default_int64(self, halea_torch: Any) -> None:
        """Default dtype should be int64."""
        result = halea_torch.randint(100, size=(10,))
        assert result.dtype == torch.int64

    def test_randint_single_arg(self, halea_torch: Any) -> None:
        """randint(n) should work (range [0, n))."""
        result = halea_torch.randint(10, size=(100,))
        assert torch.all(result >= 0)
        assert torch.all(result < 10)


class TestTorchUniform:
    """Tests for HaleaTorch.uniform()."""

    def test_uniform_returns_tensor(self, halea_torch: Any) -> None:
        """uniform() should return torch.Tensor."""
        result = halea_torch.uniform(size=(10,))
        assert isinstance(result, torch.Tensor)

    def test_uniform_default_range(self, halea_torch: Any) -> None:
        """Default range should be [0, 1)."""
        result = halea_torch.uniform(size=(1000,))
        assert torch.all(result >= 0.0)
        assert torch.all(result < 1.0)

    def test_uniform_custom_range(self, halea_torch: Any) -> None:
        """Custom range should work."""
        result = halea_torch.uniform(low=-5.0, high=5.0, size=(1000,))
        assert torch.all(result >= -5.0)
        assert torch.all(result < 5.0)

    def test_uniform_dtype(self, halea_torch: Any) -> None:
        """dtype parameter should work."""
        result = halea_torch.uniform(size=(10,), dtype=torch.float32)
        assert result.dtype == torch.float32


class TestTorchNormal:
    """Tests for HaleaTorch.normal()."""

    def test_normal_returns_tensor(self, halea_torch: Any) -> None:
        """normal() should return torch.Tensor."""
        result = halea_torch.normal(size=(10,))
        assert isinstance(result, torch.Tensor)

    def test_normal_shape_correct(self, halea_torch: Any) -> None:
        """normal() should return correct shape."""
        result = halea_torch.normal(size=(3, 4))
        assert result.shape == (3, 4)

    def test_normal_values_finite(self, halea_torch: Any) -> None:
        """All values should be finite."""
        result = halea_torch.normal(size=(1000,))
        assert torch.all(torch.isfinite(result))

    def test_normal_mean_std(self, halea_torch: Any) -> None:
        """mean and std parameters should work."""
        result = halea_torch.normal(mean=10.0, std=2.0, size=(10,))
        # Just check it runs and returns correct type
        assert isinstance(result, torch.Tensor)


class TestTorchBytes:
    """Tests for HaleaTorch.bytes()."""

    def test_bytes_returns_bytes_type(self, halea_torch: Any) -> None:
        """bytes() should return bytes type."""
        result = halea_torch.bytes(10)
        assert isinstance(result, bytes)

    def test_bytes_correct_length(self, halea_torch: Any) -> None:
        """bytes(n) should return exactly n bytes."""
        for n in [1, 10, 100]:
            result = halea_torch.bytes(n)
            assert len(result) == n

    def test_bytes_not_all_zeros(self, halea_torch: Any) -> None:
        """bytes() should return non-trivial data."""
        result = halea_torch.bytes(1024)
        assert any(b != 0 for b in result)


class TestTorchBits:
    """Tests for HaleaTorch.bits()."""

    def test_bits_returns_tensor(self, halea_torch: Any) -> None:
        """bits() should return torch.Tensor."""
        result = halea_torch.bits(10)
        assert isinstance(result, torch.Tensor)

    def test_bits_correct_length(self, halea_torch: Any) -> None:
        """bits(n) should return exactly n bits."""
        result = halea_torch.bits(100)
        assert len(result) == 100

    def test_bits_values_binary(self, halea_torch: Any) -> None:
        """All values should be 0 or 1."""
        result = halea_torch.bits(1000)
        assert torch.all((result == 0) | (result == 1))

    def test_bits_dtype_default(self, halea_torch: Any) -> None:
        """Default dtype should be uint8."""
        result = halea_torch.bits(10)
        assert result.dtype == torch.uint8


class TestTorchShuffle:
    """Tests for HaleaTorch.shuffle()."""

    def test_shuffle_in_place(self, halea_torch: Any) -> None:
        """shuffle() should modify tensor in place."""
        t = torch.arange(20)
        original_set = set(t.tolist())
        halea_torch.shuffle(t)
        # Same elements
        assert set(t.tolist()) == original_set

    def test_shuffle_preserves_elements(self, halea_torch: Any) -> None:
        """shuffle() should preserve all elements."""
        t = torch.tensor([10, 20, 30, 40, 50])
        halea_torch.shuffle(t)
        assert set(t.tolist()) == {10, 20, 30, 40, 50}

    def test_shuffle_single_element(self, halea_torch: Any) -> None:
        """shuffle() on single element should be no-op."""
        t = torch.tensor([42])
        halea_torch.shuffle(t)
        assert t[0].item() == 42


class TestTorchPermutation:
    """Tests for HaleaTorch.permutation()."""

    def test_permutation_int_returns_tensor(self, halea_torch: Any) -> None:
        """permutation(n) should return tensor of length n."""
        result = halea_torch.permutation(10)
        assert isinstance(result, torch.Tensor)
        assert len(result) == 10

    def test_permutation_int_is_permutation(self, halea_torch: Any) -> None:
        """permutation(n) should be a permutation of range(n)."""
        result = halea_torch.permutation(10)
        assert set(result.tolist()) == set(range(10))

    def test_permutation_tensor_returns_copy(self, halea_torch: Any) -> None:
        """permutation(tensor) should return shuffled copy."""
        t = torch.tensor([10, 20, 30, 40, 50])
        original = t.clone()
        result = halea_torch.permutation(t)
        # Original unchanged
        assert torch.equal(t, original)
        # Result has same elements
        assert set(result.tolist()) == set(t.tolist())


class TestTorchContextManager:
    """Tests for HaleaTorch context manager."""

    def test_context_manager(self, mock_truerng_all: Any) -> None:
        """Context manager should work."""
        from halea import HaleaTorch

        with HaleaTorch() as rng:
            result = rng.rand(10)
            assert len(result) == 10


class TestTorchDeviceInfo:
    """Tests for device_info property."""

    def test_device_info(self, halea_torch: Any) -> None:
        """device_info should return dict."""
        info = halea_torch.device_info
        assert isinstance(info, dict)


class TestTorchRepr:
    """Tests for __repr__ method."""

    def test_repr(self, halea_torch: Any) -> None:
        """repr should return string."""
        repr_str = repr(halea_torch)
        assert isinstance(repr_str, str)
        assert "HaleaTorch" in repr_str
