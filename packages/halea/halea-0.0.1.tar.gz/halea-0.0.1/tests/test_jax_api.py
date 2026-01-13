"""Tests for halea JAX API (HaleaJax class)."""

from typing import Any

import numpy as np
import pytest

# Skip all tests if jax is not available
jax = pytest.importorskip("jax")
jnp = jax.numpy


class TestJaxUniform:
    """Tests for HaleaJax.uniform()."""

    def test_uniform_returns_array(self, halea_jax: Any) -> None:
        """uniform() should return jax.Array."""
        result = halea_jax.uniform(shape=(10,))
        assert isinstance(result, jax.Array)

    def test_uniform_no_shape_returns_scalar(self, halea_jax: Any) -> None:
        """uniform() with no shape should return scalar."""
        result = halea_jax.uniform()
        assert result.ndim == 0

    def test_uniform_shape_correct(self, halea_jax: Any) -> None:
        """uniform() should return correct shape."""
        result = halea_jax.uniform(shape=(10,))
        assert result.shape == (10,)

        result = halea_jax.uniform(shape=(3, 4))
        assert result.shape == (3, 4)

    def test_uniform_default_range(self, halea_jax: Any) -> None:
        """Default range should be [0, 1)."""
        result = halea_jax.uniform(shape=(1000,))
        assert jnp.all(result >= 0.0)
        assert jnp.all(result < 1.0)

    def test_uniform_custom_range(self, halea_jax: Any) -> None:
        """Custom range should work."""
        result = halea_jax.uniform(shape=(1000,), minval=-5.0, maxval=5.0)
        assert jnp.all(result >= -5.0)
        assert jnp.all(result < 5.0)

    def test_uniform_dtype_default_float64(self, halea_jax: Any) -> None:
        """Default dtype should be float64."""
        result = halea_jax.uniform(shape=(10,))
        assert result.dtype == jnp.float64

    def test_uniform_dtype_float32(self, halea_jax: Any) -> None:
        """Custom dtype float32 should work."""
        result = halea_jax.uniform(shape=(10,), dtype=jnp.float32)
        assert result.dtype == jnp.float32

    def test_uniform_not_all_same(self, halea_jax: Any) -> None:
        """Values should not all be the same."""
        result = halea_jax.uniform(shape=(100,))
        assert not jnp.all(result == result[0])


class TestJaxNormal:
    """Tests for HaleaJax.normal()."""

    def test_normal_returns_array(self, halea_jax: Any) -> None:
        """normal() should return jax.Array."""
        result = halea_jax.normal(shape=(10,))
        assert isinstance(result, jax.Array)

    def test_normal_no_shape_returns_scalar(self, halea_jax: Any) -> None:
        """normal() with no shape should return scalar."""
        result = halea_jax.normal()
        assert result.ndim == 0

    def test_normal_shape_correct(self, halea_jax: Any) -> None:
        """normal() should return correct shape."""
        result = halea_jax.normal(shape=(10,))
        assert result.shape == (10,)

        result = halea_jax.normal(shape=(3, 4))
        assert result.shape == (3, 4)

    def test_normal_values_finite(self, halea_jax: Any) -> None:
        """All values should be finite (no NaN or Inf)."""
        result = halea_jax.normal(shape=(1000,))
        assert jnp.all(jnp.isfinite(result))

    def test_normal_dtype_default_float64(self, halea_jax: Any) -> None:
        """Default dtype should be float64."""
        result = halea_jax.normal(shape=(10,))
        assert result.dtype == jnp.float64


class TestJaxRandint:
    """Tests for HaleaJax.randint()."""

    def test_randint_returns_array(self, halea_jax: Any) -> None:
        """randint() should return jax.Array."""
        result = halea_jax.randint(0, 10, shape=(5,))
        assert isinstance(result, jax.Array)

    def test_randint_no_shape_returns_scalar(self, halea_jax: Any) -> None:
        """randint() with no shape should return scalar."""
        result = halea_jax.randint(0, 10)
        assert result.ndim == 0

    def test_randint_values_in_range(self, halea_jax: Any) -> None:
        """All values should be in [minval, maxval)."""
        result = halea_jax.randint(10, 50, shape=(100,))
        assert jnp.all(result >= 10)
        assert jnp.all(result < 50)

    def test_randint_dtype_default_int64(self, halea_jax: Any) -> None:
        """Default dtype should be int64."""
        result = halea_jax.randint(0, 100, shape=(10,))
        assert result.dtype == jnp.int64

    def test_randint_maxval_lte_minval_raises(self, halea_jax: Any) -> None:
        """maxval <= minval should raise ValueError."""
        with pytest.raises(ValueError):
            halea_jax.randint(10, 5, shape=(10,))


class TestJaxChoice:
    """Tests for HaleaJax.choice()."""

    def test_choice_from_int(self, halea_jax: Any) -> None:
        """choice(n) should return value in [0, n)."""
        result = halea_jax.choice(10)
        assert 0 <= int(result) < 10

    def test_choice_from_array(self, halea_jax: Any) -> None:
        """choice(array) should return element from array."""
        arr = jnp.array([10, 20, 30, 40, 50])
        result = halea_jax.choice(arr)
        assert int(result) in [10, 20, 30, 40, 50]

    def test_choice_with_shape(self, halea_jax: Any) -> None:
        """choice with shape should return correct shape."""
        result = halea_jax.choice(10, shape=(5,))
        assert result.shape == (5,)

    def test_choice_with_replacement(self, halea_jax: Any) -> None:
        """With replacement, shape can exceed population."""
        result = halea_jax.choice(5, shape=(100,), replace=True)
        assert len(result) == 100

    def test_choice_without_replacement_unique(self, halea_jax: Any) -> None:
        """Without replacement, all values should be unique."""
        result = halea_jax.choice(100, shape=(50,), replace=False)
        assert len(result) == 50
        assert len(jnp.unique(result)) == 50


class TestJaxBytes:
    """Tests for HaleaJax.bytes()."""

    def test_bytes_returns_bytes_type(self, halea_jax: Any) -> None:
        """bytes() should return bytes type."""
        result = halea_jax.bytes(10)
        assert isinstance(result, bytes)

    def test_bytes_correct_length(self, halea_jax: Any) -> None:
        """bytes(n) should return exactly n bytes."""
        for n in [1, 10, 100]:
            result = halea_jax.bytes(n)
            assert len(result) == n

    def test_bytes_not_all_zeros(self, halea_jax: Any) -> None:
        """bytes() should return non-trivial data."""
        result = halea_jax.bytes(1024)
        assert any(b != 0 for b in result)


class TestJaxBits:
    """Tests for HaleaJax.bits()."""

    def test_bits_returns_array(self, halea_jax: Any) -> None:
        """bits() should return jax.Array."""
        result = halea_jax.bits(10)
        assert isinstance(result, jax.Array)

    def test_bits_correct_length(self, halea_jax: Any) -> None:
        """bits(n) should return exactly n bits."""
        result = halea_jax.bits(100)
        assert len(result) == 100

    def test_bits_values_binary(self, halea_jax: Any) -> None:
        """All values should be 0 or 1."""
        result = halea_jax.bits(1000)
        assert jnp.all((result == 0) | (result == 1))

    def test_bits_dtype_default_uint8(self, halea_jax: Any) -> None:
        """Default dtype should be uint8."""
        result = halea_jax.bits(10)
        assert result.dtype == jnp.uint8

    def test_bits_zero_returns_empty(self, halea_jax: Any) -> None:
        """bits(0) should return empty array."""
        result = halea_jax.bits(0)
        assert len(result) == 0

    def test_bits_negative_raises(self, halea_jax: Any) -> None:
        """bits(negative) should raise ValueError."""
        with pytest.raises(ValueError):
            halea_jax.bits(-1)


class TestJaxPermutation:
    """Tests for HaleaJax.permutation()."""

    def test_permutation_int_returns_array(self, halea_jax: Any) -> None:
        """permutation(n) should return array of length n."""
        result = halea_jax.permutation(10)
        assert isinstance(result, jax.Array)
        assert len(result) == 10

    def test_permutation_int_is_permutation(self, halea_jax: Any) -> None:
        """permutation(n) should be a permutation of range(n)."""
        result = halea_jax.permutation(10)
        assert set(result.tolist()) == set(range(10))

    def test_permutation_array_returns_shuffled(self, halea_jax: Any) -> None:
        """permutation(array) should return shuffled copy."""
        arr = jnp.array([10, 20, 30, 40, 50])
        result = halea_jax.permutation(arr)
        # Result has same elements
        assert set(result.tolist()) == set(arr.tolist())


class TestJaxContextManager:
    """Tests for HaleaJax context manager."""

    def test_context_manager(self, mock_truerng_all: Any) -> None:
        """Context manager should work."""
        from halea import HaleaJax

        with HaleaJax() as rng:
            result = rng.uniform(shape=(10,))
            assert len(result) == 10


class TestJaxDeviceInfo:
    """Tests for device_info property."""

    def test_device_info(self, halea_jax: Any) -> None:
        """device_info should return dict."""
        info = halea_jax.device_info
        assert isinstance(info, dict)


class TestJaxRepr:
    """Tests for __repr__ method."""

    def test_repr(self, halea_jax: Any) -> None:
        """repr should return string."""
        repr_str = repr(halea_jax)
        assert isinstance(repr_str, str)
        assert "HaleaJax" in repr_str
