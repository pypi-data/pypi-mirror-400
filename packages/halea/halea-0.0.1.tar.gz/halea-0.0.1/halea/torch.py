"""PyTorch-based hardware RNG API.

Provides `HaleaTorch` class for generating random tensors using
hardware RNG devices.

This module is only available if PyTorch is installed.
"""

from types import TracebackType
from typing import Self

import numpy as np
import torch

from halea.numpy import HaleaNumpy

__all__ = [
    "HaleaTorch",
]


class HaleaTorch:
    """Hardware random number generator with PyTorch interface.

    Provides torch-like API for generating random tensors using
    TrueRNG or ChaosKey hardware devices.
    """

    def __init__(
        self,
        backend: str | None = None,
        *,
        port: str | None = None,
        serial: str | None = None,
        device: str | torch.device = "cpu",
        buffer_size: int = 8192,
    ) -> None:
        """Initialize hardware RNG with PyTorch interface.

        Args:
            backend: "truerng", "chaoskey", or None for auto-detect.
            port: Serial port for TrueRNG (auto-detected if None).
            serial: Serial number for ChaosKey (first device if None).
            device: PyTorch device for output tensors.
            buffer_size: Internal buffer size for efficient reads.
        """
        self._numpy_rng = HaleaNumpy(
            backend=backend,
            port=port,
            serial=serial,
            buffer_size=buffer_size,
        )
        self._device = torch.device(device)

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
        return f"HaleaTorch(device={self._device!r}, {numpy_repr})"

    # =========================================================================
    # Core Random Generation Methods
    # =========================================================================

    def rand(self, *size: int, dtype: torch.dtype = torch.float64) -> torch.Tensor:
        """Generate random floats uniformly distributed in [0, 1).

        Args:
            *size: Output shape.
            dtype: Output dtype (float32 or float64).

        Returns:
            Random tensor in [0, 1).

        Examples:
            >>> rng.rand()  # Single float
            >>> rng.rand(5)  # 1D tensor of 5 floats
            >>> rng.rand(3, 4)  # 3x4 tensor
        """
        if any(s < 0 for s in size):
            raise ValueError(f"Size dimensions must be non-negative: {size}")

        squeeze_output = not size
        if not size:
            size = (1,)
        arr = self._numpy_rng.rand(*size)
        tensor = torch.from_numpy(arr).to(dtype=dtype, device=self._device, non_blocking=True)
        return tensor.squeeze() if squeeze_output else tensor

    def randn(self, *size: int, dtype: torch.dtype = torch.float64) -> torch.Tensor:
        """Generate random floats from standard normal distribution.

        Uses Box-Muller transform on hardware uniform samples.

        Args:
            *size: Output shape.
            dtype: Output dtype (float32 or float64).

        Returns:
            Random tensor from N(0, 1).

        Examples:
            >>> rng.randn()  # Single sample
            >>> rng.randn(10)  # 10 samples
            >>> rng.randn(3, 4)  # 3x4 tensor
        """
        if any(s < 0 for s in size):
            raise ValueError(f"Size dimensions must be non-negative: {size}")

        squeeze_output = not size
        if not size:
            size = (1,)

        # Delegate to numpy's randn (ARCH-1)
        arr = self._numpy_rng.randn(*size)
        if isinstance(arr, np.float64):
            arr = np.array([arr])

        tensor = torch.from_numpy(arr).to(dtype=dtype, device=self._device, non_blocking=True)
        return tensor.squeeze() if squeeze_output else tensor

    def randint(
        self,
        low: int,
        high: int | None = None,
        size: tuple[int, ...] = (1,),
        dtype: torch.dtype = torch.int64,
    ) -> torch.Tensor:
        """Generate random integers.

        Args:
            low: Lowest integer (inclusive), or upper bound if high is None.
            high: Upper bound (exclusive).
            size: Output shape.
            dtype: Output dtype.

        Returns:
            Random integer tensor.

        Examples:
            >>> rng.randint(10)  # [0, 10)
            >>> rng.randint(5, 10, (3,))  # 3 integers in [5, 10)
        """
        if any(s < 0 for s in size):
            raise ValueError(f"Size dimensions must be non-negative: {size}")

        if high is None:
            low, high = 0, low

        arr = self._numpy_rng.randint(low, high, size=size)
        if isinstance(arr, np.int64):
            arr = np.array([arr])
        return torch.from_numpy(arr).to(dtype=dtype, device=self._device, non_blocking=True)

    def uniform(
        self,
        low: float = 0.0,
        high: float = 1.0,
        size: tuple[int, ...] = (1,),
        dtype: torch.dtype = torch.float64,
    ) -> torch.Tensor:
        """Generate random floats uniformly distributed in [low, high).

        Args:
            low: Lower bound (inclusive).
            high: Upper bound (exclusive).
            size: Output shape.
            dtype: Output dtype.

        Returns:
            Random tensor in [low, high).

        Examples:
            >>> rng.uniform(-1.0, 1.0, (10,))
        """
        if any(s < 0 for s in size):
            raise ValueError(f"Size dimensions must be non-negative: {size}")

        arr = self._numpy_rng.rand(*size)
        arr = arr * (high - low) + low
        return torch.from_numpy(arr).to(dtype=dtype, device=self._device, non_blocking=True)

    def normal(
        self,
        mean: float = 0.0,
        std: float = 1.0,
        size: tuple[int, ...] = (1,),
        dtype: torch.dtype = torch.float64,
    ) -> torch.Tensor:
        """Generate random floats from normal distribution.

        Args:
            mean: Mean of the distribution.
            std: Standard deviation.
            size: Output shape.
            dtype: Output dtype.

        Returns:
            Random tensor from N(mean, std^2).

        Examples:
            >>> rng.normal(0.0, 1.0, (100,))
        """
        if any(s < 0 for s in size):
            raise ValueError(f"Size dimensions must be non-negative: {size}")

        tensor = self.randn(*size, dtype=dtype)
        return tensor * std + mean

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

    def bits(self, n: int, dtype: torch.dtype = torch.uint8) -> torch.Tensor:
        """Return tensor of n random bits (0 or 1).

        Args:
            n: Number of bits to return.
            dtype: Output dtype.

        Returns:
            Tensor of n random bits.
        """
        arr = self._numpy_rng.bits(n)
        return torch.from_numpy(arr).to(dtype=dtype, device=self._device, non_blocking=True)

    def shuffle(self, x: torch.Tensor) -> None:
        """Shuffle tensor in-place along first dimension.

        Args:
            x: Tensor to shuffle in-place.

        Example:
            >>> t = torch.arange(10)
            >>> rng.shuffle(t)
        """
        n = x.size(0)
        if n <= 1:
            return
        # Batch generate all random values (PERF-1 fix)
        random_floats = self._numpy_rng.rand(n - 1)
        for i in range(n - 1, 0, -1):
            j = int(random_floats[n - 1 - i] * (i + 1))
            x[[i, j]] = x[[j, i]]

    def permutation(self, x: int | torch.Tensor) -> torch.Tensor:
        """Return shuffled copy or random permutation.

        Args:
            x: If int, return permutation of range(x).
               If tensor, return shuffled copy.

        Returns:
            Shuffled tensor.

        Examples:
            >>> rng.permutation(5)  # Random order of [0, 1, 2, 3, 4]
            >>> rng.permutation(torch.tensor([1, 2, 3]))  # Shuffled copy
        """
        if isinstance(x, int):
            t = torch.arange(x, device=self._device)
        else:
            t = x.clone()
        self.shuffle(t)
        return t
