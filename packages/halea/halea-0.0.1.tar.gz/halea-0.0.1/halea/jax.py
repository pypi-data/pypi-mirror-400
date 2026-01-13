"""JAX-based hardware RNG API.

Provides `HaleaJax` class for generating random arrays using
hardware RNG devices.

This module is only available if JAX is installed.

Note: Unlike JAX's functional random API, this class is stateful
since it reads from hardware.
"""

from types import TracebackType
from typing import Self

import jax
import jax.numpy as jnp
import numpy as np
from numpy.typing import DTypeLike

from halea.numpy import HaleaNumpy

__all__ = [
    "HaleaJax",
]


class HaleaJax:
    """Hardware random number generator with JAX interface.

    Provides jax.random-like API for generating random arrays using
    TrueRNG or ChaosKey hardware devices.

    Note: Unlike JAX's functional random API, this class is stateful
    since it reads from hardware. Arrays are immutable, so no in-place
    shuffle is provided.
    """

    def __init__(
        self,
        backend: str | None = None,
        *,
        port: str | None = None,
        serial: str | None = None,
        buffer_size: int = 8192,
    ) -> None:
        """Initialize hardware RNG with JAX interface.

        Args:
            backend: "truerng", "chaoskey", or None for auto-detect.
            port: Serial port for TrueRNG (auto-detected if None).
            serial: Serial number for ChaosKey (first device if None).
            buffer_size: Internal buffer size for efficient reads.
        """
        self._numpy_rng = HaleaNumpy(
            backend=backend,
            port=port,
            serial=serial,
            buffer_size=buffer_size,
        )

    def connect(self) -> None:
        """Establish connection to the hardware device."""
        self._numpy_rng.connect()

    def disconnect(self) -> None:
        """Close connection to the hardware device."""
        self._numpy_rng.disconnect()

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

    @property
    def device_info(self) -> dict[str, str | None]:
        """Return device identification info."""
        return self._numpy_rng.device_info

    def __repr__(self) -> str:
        """Return string representation."""
        numpy_repr = repr(self._numpy_rng)
        return f"HaleaJax({numpy_repr})"

    # =========================================================================
    # Core Random Generation Methods
    # =========================================================================

    def uniform(
        self,
        shape: tuple[int, ...] = (),
        dtype: DTypeLike = jnp.float64,
        minval: float = 0.0,
        maxval: float = 1.0,
    ) -> jax.Array:
        """Generate random floats uniformly distributed in [minval, maxval).

        Args:
            shape: Output shape.
            dtype: Output dtype.
            minval: Lower bound (inclusive).
            maxval: Upper bound (exclusive).

        Returns:
            Random array in [minval, maxval).

        Examples:
            >>> rng.uniform()  # Single float in [0, 1)
            >>> rng.uniform(shape=(3, 4))  # 3x4 array
            >>> rng.uniform(minval=-1, maxval=1)  # [-1, 1)
        """
        if any(s < 0 for s in shape):
            raise ValueError(f"Shape dimensions must be non-negative: {shape}")

        squeeze_output = not shape
        if not shape:
            shape = (1,)

        arr = self._numpy_rng.rand(*shape)
        arr = arr * (maxval - minval) + minval
        result = jnp.asarray(arr, dtype=dtype)
        return result.squeeze() if squeeze_output else result

    def normal(
        self,
        shape: tuple[int, ...] = (),
        dtype: DTypeLike = jnp.float64,
    ) -> jax.Array:
        """Generate random floats from standard normal distribution.

        Uses Box-Muller transform on hardware uniform samples.

        Args:
            shape: Output shape.
            dtype: Output dtype.

        Returns:
            Random array from N(0, 1).

        Examples:
            >>> rng.normal()  # Single sample
            >>> rng.normal(shape=(10,))  # 10 samples
        """
        if any(s < 0 for s in shape):
            raise ValueError(f"Shape dimensions must be non-negative: {shape}")

        squeeze_output = not shape
        if not shape:
            shape = (1,)

        # Delegate to numpy's randn (ARCH-1)
        arr = self._numpy_rng.randn(*shape)
        if isinstance(arr, np.float64):
            arr = np.array([arr])

        result = jnp.asarray(arr, dtype=dtype)
        return result.squeeze() if squeeze_output else result

    def randint(
        self,
        minval: int,
        maxval: int,
        shape: tuple[int, ...] = (),
        dtype: DTypeLike = jnp.int64,
    ) -> jax.Array:
        """Generate random integers in [minval, maxval).

        Args:
            minval: Lower bound (inclusive).
            maxval: Upper bound (exclusive).
            shape: Output shape.
            dtype: Output dtype.

        Returns:
            Random integer array.

        Examples:
            >>> rng.randint(0, 10)  # Single int
            >>> rng.randint(0, 100, shape=(5,))  # 5 integers
        """
        if maxval <= minval:
            raise ValueError(f"maxval ({maxval}) must be greater than minval ({minval})")
        if any(s < 0 for s in shape):
            raise ValueError(f"Shape dimensions must be non-negative: {shape}")

        if not shape:
            arr = self._numpy_rng.randint(minval, maxval)
            return jnp.asarray(arr, dtype=dtype)

        arr = self._numpy_rng.randint(minval, maxval, size=shape)
        return jnp.asarray(arr, dtype=dtype)

    def choice(
        self,
        a: int | jax.Array,
        shape: tuple[int, ...] = (),
        replace: bool = True,
    ) -> jax.Array:
        """Random sample from array or range.

        Args:
            a: If int, sample from range(a). If array, sample from it.
            shape: Output shape.
            replace: Whether to sample with replacement.

        Returns:
            Random sample(s).

        Examples:
            >>> rng.choice(5)  # One from [0..4]
            >>> rng.choice(jnp.array([1, 2, 3]), (2,))  # 2 from array
        """
        if isinstance(a, int):
            arr_np = np.arange(a)
        else:
            arr_np = np.asarray(a)

        size = shape if shape else None
        result = self._numpy_rng.choice(arr_np, size=size, replace=replace)
        return jnp.asarray(result)

    # =========================================================================
    # New API Methods
    # =========================================================================

    def bytes(self, n: int) -> bytes:
        """Return n random bytes.

        Args:
            n: Number of bytes to return.

        Returns:
            n random bytes.
        """
        return self._numpy_rng.bytes(n)

    def bits(self, n: int, dtype: DTypeLike = jnp.uint8) -> jax.Array:
        """Return array of n random bits (0 or 1).

        Args:
            n: Number of bits to return.
            dtype: Output dtype.

        Returns:
            Array of n random bits.
        """
        if n < 0:
            raise ValueError(f"n must be non-negative, got {n}")
        if n == 0:
            return jnp.array([], dtype=dtype)
        arr = self._numpy_rng.bits(n)
        return jnp.asarray(arr, dtype=dtype)

    def permutation(self, x: int | jax.Array) -> jax.Array:
        """Return shuffled copy or random permutation.

        Note: JAX arrays are immutable, so no in-place shuffle is provided.

        Args:
            x: If int, return permutation of range(x).
               If array, return shuffled copy.

        Returns:
            Shuffled array.

        Examples:
            >>> rng.permutation(5)  # Random order of [0, 1, 2, 3, 4]
            >>> rng.permutation(jnp.array([1, 2, 3]))  # Shuffled
        """
        if isinstance(x, int):
            arr_np = np.arange(x)
        else:
            arr_np = np.asarray(x)

        result_np = self._numpy_rng.permutation(arr_np)
        return jnp.asarray(result_np)
