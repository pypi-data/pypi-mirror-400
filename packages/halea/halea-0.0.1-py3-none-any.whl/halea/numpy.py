"""NumPy-based hardware RNG API.

Provides `HaleaNumpy` class and module-level convenience functions for
generating random numbers using hardware RNG devices.

Thread Safety
-------------
Module-level functions (rand, randint, shuffle, etc.) are NOT thread-safe.
They share a global HaleaNumpy instance with unsynchronized state.

For multi-threaded use, create separate HaleaNumpy instances per thread.
"""

import atexit
import threading
import warnings
from collections.abc import MutableSequence
from types import TracebackType
from typing import Any
from typing import Self

import numpy as np

from halea._base import HardwareRNGBackend
from halea.backends import get_backend

# Rejection sampling constants
_REJECTION_OVERGEN_FACTOR: int = 2
_REJECTION_OVERGEN_CAP: int = 1024

# Set-based choice threshold (use set-based when k < n / _CHOICE_SET_THRESHOLD_DIVISOR)
_CHOICE_SET_THRESHOLD_DIVISOR: int = 10

__all__ = [
    "HaleaNumpy",
    # Module-level functions
    "rand",
    "randn",
    "randint",
    "choice",
    "bytes",
    "bits",
    "shuffle",
    "permutation",
]


class HaleaNumpy:
    """Hardware random number generator with NumPy interface.

    Provides numpy-like API for generating random numbers using
    TrueRNG or ChaosKey hardware devices.
    """

    # Bytes per float (8 bytes = 64 bits for full float64 precision)
    BYTES_PER_FLOAT = 8
    MAX_UINT64 = 2**64 - 1

    def __init__(
        self,
        backend: str | None = None,
        *,
        port: str | None = None,
        serial: str | None = None,
        buffer_size: int = 8192,
        unbiased: bool = False,
    ) -> None:
        """Initialize hardware RNG with NumPy interface.

        Args:
            backend: "truerng", "chaoskey", or None for auto-detect.
            port: Serial port for TrueRNG (auto-detected if None).
            serial: Serial number for ChaosKey (first device if None).
            buffer_size: Internal buffer size for efficient reads.
            unbiased: If True, use rejection sampling for randint() to
                eliminate modulo bias. Slower but statistically correct.
                Default False (fast float-based method).
        """
        self._backend_type = backend
        self._port = port
        self._serial = serial
        self._buffer_size = buffer_size
        self._unbiased = unbiased
        self._backend: HardwareRNGBackend | None = None

    def connect(self) -> None:
        """Establish connection to the hardware device."""
        if self._backend is not None and self._backend.is_connected:
            return
        self._backend = get_backend(
            backend=self._backend_type,
            port=self._port,
            serial=self._serial,
            buffer_size=self._buffer_size,
        )
        self._backend.connect()

    def disconnect(self) -> None:
        """Close connection to the hardware device."""
        if self._backend is not None:
            self._backend.disconnect()
            self._backend = None

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

    def _read_bytes(self, n: int) -> bytes:
        """Read n bytes, auto-connecting if needed."""
        if self._backend is None or not self._backend.is_connected:
            self.connect()
        assert self._backend is not None
        return self._backend.read_bytes(n)

    @property
    def device_info(self) -> dict[str, str | None]:
        """Return device identification info."""
        if self._backend is None:
            return {"backend": None, "type": None}
        return self._backend.device_info

    def __repr__(self) -> str:
        """Return string representation."""
        if self._backend is None:
            status = "not connected"
        elif self._backend.is_connected:
            status = "connected"
        else:
            status = "disconnected"
        backend = self._backend_type or "auto"
        return f"HaleaNumpy(backend={backend!r}, unbiased={self._unbiased}, {status})"

    # =========================================================================
    # Core Random Generation Methods
    # =========================================================================

    def rand(self, *shape: int) -> np.float64 | np.ndarray:
        """Generate random floats uniformly distributed in [0, 1).

        Args:
            *shape: Output shape. If empty, returns a single float.

        Returns:
            Random float or array of floats in [0, 1).

        Examples:
            >>> rng.rand()  # Single float
            >>> rng.rand(5)  # Array of 5 floats
            >>> rng.rand(3, 4)  # 3x4 array
        """
        if any(s < 0 for s in shape):
            raise ValueError(f"Shape dimensions must be non-negative: {shape}")

        if not shape:
            # Single float
            raw = self._read_bytes(self.BYTES_PER_FLOAT)
            value = int.from_bytes(raw, byteorder="little")
            return np.float64(value / (self.MAX_UINT64 + 1))

        # Array of floats
        total = int(np.prod(shape))
        raw = self._read_bytes(total * self.BYTES_PER_FLOAT)

        # Convert bytes to uint64 array, then to float64
        values = np.frombuffer(raw, dtype=np.uint64)
        floats = values.astype(np.float64) / (self.MAX_UINT64 + 1)

        return floats.reshape(shape)

    def randn(self, *shape: int) -> np.float64 | np.ndarray:
        """Generate random floats from standard normal distribution N(0,1).

        Uses Box-Muller transform on hardware uniform samples.

        Args:
            *shape: Output shape. If empty, returns a single float.

        Returns:
            Random float or array from standard normal distribution.

        Examples:
            >>> rng.randn()  # Single normal float
            >>> rng.randn(5)  # Array of 5 normal floats
            >>> rng.randn(3, 4)  # 3x4 array from N(0,1)
        """
        if any(s < 0 for s in shape):
            raise ValueError(f"Shape dimensions must be non-negative: {shape}")

        squeeze_output = not shape
        if not shape:
            shape = (1,)

        total = int(np.prod(shape))
        n_pairs = (total + 1) // 2

        u1 = self.rand(n_pairs)
        u2 = self.rand(n_pairs)

        # Box-Muller transform with numerical safety
        u1_safe = np.clip(u1, np.finfo(np.float64).tiny, 1.0)
        r = np.sqrt(-2.0 * np.log(u1_safe))
        theta = 2.0 * np.pi * u2
        z0 = r * np.cos(theta)
        z1 = r * np.sin(theta)

        # Interleave and trim
        normal = np.empty(2 * n_pairs, dtype=np.float64)
        normal[0::2] = z0
        normal[1::2] = z1
        normal = normal[:total].reshape(shape)

        if squeeze_output:
            return np.float64(normal[0])
        return normal

    def randint(
        self,
        low: int,
        high: int | None = None,
        size: int | tuple[int, ...] | None = None,
    ) -> np.int64 | np.ndarray:
        """Generate random integers.

        Args:
            low: Lowest integer (inclusive), or upper bound if high is None.
            high: Upper bound (exclusive). If None, range is [0, low).
            size: Output shape.

        Returns:
            Random integer(s) in [low, high).

        Examples:
            >>> rng.randint(10)  # [0, 10)
            >>> rng.randint(5, 10)  # [5, 10)
            >>> rng.randint(0, 100, 5)  # 5 integers in [0, 100)

        Note:
            If `unbiased=True` was set at construction, uses rejection
            sampling for statistically correct uniform distribution.
            Otherwise uses fast float-based scaling which has negligible
            bias (~1e-15 relative) for ranges under 2^53, but may produce
            biased results for very large ranges. For cryptographic or
            high-precision statistical applications, use `unbiased=True`.
        """
        if high is None:
            low, high = 0, low

        if high <= low:
            raise ValueError(f"high ({high}) must be greater than low ({low})")

        if size is None:
            shape: tuple[int, ...] = ()
        elif isinstance(size, int):
            shape = (size,)
        else:
            shape = size

        range_size = high - low
        if self._unbiased and range_size > 0:
            return self._randint_unbiased(low, high, shape)

        # Default: fast float-based scaling
        if not shape:
            f = self.rand()
            return np.int64(np.floor(f * range_size + low))

        floats = self.rand(*shape)
        return np.floor(floats * range_size + low).astype(np.int64)

    def _compute_mask_params(self, range_size: int) -> tuple[int, int, int]:
        """Compute bit mask parameters for rejection sampling.

        Args:
            range_size: Size of the integer range to sample from.

        Returns:
            Tuple of (bits_needed, mask, bytes_per_value).
        """
        bits_needed = max(1, (range_size - 1).bit_length())
        mask = (1 << bits_needed) - 1
        bytes_per = (bits_needed + 7) // 8
        return bits_needed, mask, bytes_per

    def _bytes_to_masked_uint64(self, raw_bytes: bytes, bytes_per: int, mask: int) -> np.ndarray:
        """Convert raw bytes to masked uint64 candidates.

        Args:
            raw_bytes: Raw random bytes from device.
            bytes_per: Bytes per value (1, 2, 4, or 8).
            mask: Bitmask to apply.

        Returns:
            Array of masked uint64 values.
        """
        if bytes_per == 1:
            return np.frombuffer(raw_bytes, dtype=np.uint8).astype(np.uint64) & mask
        elif bytes_per == 2:
            n_vals = len(raw_bytes) // 2
            return np.frombuffer(raw_bytes[: n_vals * 2], dtype=np.uint16).astype(np.uint64) & mask
        elif bytes_per <= 4:
            n_vals = len(raw_bytes) // 4
            return np.frombuffer(raw_bytes[: n_vals * 4], dtype=np.uint32).astype(np.uint64) & mask
        else:
            n_vals = len(raw_bytes) // 8
            return np.frombuffer(raw_bytes[: n_vals * 8], dtype=np.uint64) & mask

    def _randint_unbiased(
        self,
        low: int,
        high: int,
        shape: tuple[int, ...],
    ) -> np.int64 | np.ndarray:
        """Generate unbiased random integers using rejection sampling.

        Uses bitmask rejection to eliminate modulo bias. Generates random
        values, masks to smallest power-of-2 >= range, rejects out-of-range.

        Args:
            low: Lower bound (inclusive).
            high: Upper bound (exclusive).
            shape: Output shape (empty tuple for scalar).

        Returns:
            Random integer(s) in [low, high).
        """
        range_size = high - low

        if range_size <= 0:
            raise ValueError(f"Invalid range: [{low}, {high})")

        _, mask, bytes_per = self._compute_mask_params(range_size)

        total = 1 if not shape else int(np.prod(shape))
        result = np.empty(total, dtype=np.int64)
        generated = 0

        while generated < total:
            n_needed = total - generated
            n_try = min(
                n_needed * _REJECTION_OVERGEN_FACTOR,
                n_needed + _REJECTION_OVERGEN_CAP,
            )
            raw_bytes = self._read_bytes(n_try * bytes_per)

            candidates = self._bytes_to_masked_uint64(raw_bytes, bytes_per, mask)
            valid = candidates[candidates < range_size]
            n_accept = min(len(valid), n_needed)
            result[generated : generated + n_accept] = valid[:n_accept]
            generated += n_accept

        result = result + low

        if not shape:
            return np.int64(result[0])
        return result.reshape(shape)

    def choice(
        self,
        a: int | np.ndarray,
        size: int | tuple[int, ...] | None = None,
        replace: bool = True,
    ) -> np.generic | np.ndarray:
        """Random sample from a given array or range.

        Args:
            a: If int, sample from range(a). If array, sample from it.
            size: Output shape.
            replace: Whether to sample with replacement.

        Returns:
            Random sample(s).

        Examples:
            >>> rng.choice(5)  # One from [0, 1, 2, 3, 4]
            >>> rng.choice([1, 2, 3], size=2)  # 2 from the list
            >>> rng.choice(10, size=3, replace=False)  # 3 unique from [0..9]
        """
        if isinstance(a, int):
            arr = np.arange(a)
        else:
            arr = np.asarray(a)

        if len(arr) == 0:
            raise ValueError("Cannot sample from empty array")

        if size is None:
            n = 1
            squeeze = True
        elif isinstance(size, int):
            n = size
            squeeze = False
        else:
            n = int(np.prod(size))
            squeeze = False

        if replace:
            indices = self.randint(len(arr), size=n)
            if isinstance(indices, np.int64):
                indices = np.array([indices])
        else:
            if n > len(arr):
                raise ValueError("Cannot sample more elements than available without replacement")

            # Use set-based rejection for small k (PERF-2)
            if n < len(arr) // _CHOICE_SET_THRESHOLD_DIVISOR:
                indices_set: set[int] = set()
                while len(indices_set) < n:
                    batch_size = min(n - len(indices_set), 64)
                    candidates = self.randint(len(arr), size=batch_size)
                    if isinstance(candidates, np.int64):
                        candidates = np.array([candidates])
                    for idx in candidates:
                        if idx not in indices_set:
                            indices_set.add(int(idx))
                            if len(indices_set) >= n:
                                break
                indices = np.array(list(indices_set), dtype=np.int64)
                self.shuffle(indices)  # Restore random order from hash order
            else:
                # Partial Fisher-Yates for larger samples
                idx_arr = np.arange(len(arr))
                random_floats = self.rand(n)
                for i in range(n):
                    j = i + int(random_floats[i] * (len(arr) - i))
                    idx_arr[i], idx_arr[j] = idx_arr[j], idx_arr[i]
                indices = idx_arr[:n]

        result = arr[indices]

        if squeeze:
            return result[0]
        if size is not None and not isinstance(size, int):
            return result.reshape(size)
        return result

    # =========================================================================
    # New API Methods
    # =========================================================================

    def bytes(self, n: int) -> bytes:
        """Return n random bytes.

        Args:
            n: Number of bytes to return.

        Returns:
            n random bytes.

        Example:
            >>> rng.bytes(16)  # 16 random bytes for a key
        """
        if n < 0:
            raise ValueError(f"n must be non-negative, got {n}")
        if n == 0:
            return b""
        return self._read_bytes(n)

    def bits(self, n: int) -> np.ndarray:
        """Return array of n random bits (0 or 1) as uint8.

        Args:
            n: Number of bits to return.

        Returns:
            Array of n random bits (values 0 or 1).

        Example:
            >>> rng.bits(8)  # 8 random bits
            array([1, 0, 1, 1, 0, 0, 1, 0], dtype=uint8)
        """
        if n < 0:
            raise ValueError(f"n must be non-negative, got {n}")
        if n == 0:
            return np.array([], dtype=np.uint8)
        n_bytes = (n + 7) // 8
        raw = self._read_bytes(n_bytes)
        all_bits = np.unpackbits(np.frombuffer(raw, dtype=np.uint8))
        return all_bits[:n]

    def shuffle(self, x: MutableSequence[Any] | np.ndarray) -> None:
        """Shuffle sequence in-place using Fisher-Yates with hardware randomness.

        Args:
            x: Sequence to shuffle in-place (list, numpy array, etc.).

        Example:
            >>> arr = np.arange(10)
            >>> rng.shuffle(arr)
            >>> arr  # Now shuffled
        """
        n = len(x)
        if n <= 1:
            return
        # Batch generate all random floats upfront for O(n) instead of O(n²)
        random_floats = self.rand(n - 1)
        for i in range(n - 1, 0, -1):
            # Scale float to [0, i] range
            j = int(random_floats[n - 1 - i] * (i + 1))
            x[i], x[j] = x[j], x[i]

    def permutation(self, x: int | np.ndarray) -> np.ndarray:
        """Return shuffled copy or random permutation of range.

        Args:
            x: If int, return permutation of range(x).
               If array, return shuffled copy.

        Returns:
            Shuffled array.

        Examples:
            >>> rng.permutation(5)  # Random order of [0, 1, 2, 3, 4]
            >>> rng.permutation([1, 2, 3])  # Shuffled copy
        """
        if isinstance(x, int):
            arr = np.arange(x)
        else:
            arr = np.array(x)  # Copy
        self.shuffle(arr)
        return arr


# =============================================================================
# Module-Level Singleton and Convenience Functions
# =============================================================================

_global_rng: HaleaNumpy | None = None
_main_thread_id: int | None = None
_thread_warning_shown: bool = False


def _check_thread_safety() -> None:
    """Warn on first use from non-main thread."""
    global _main_thread_id, _thread_warning_shown

    current_thread = threading.current_thread()

    if _main_thread_id is None:
        _main_thread_id = current_thread.ident
        return

    if current_thread.ident != _main_thread_id and not _thread_warning_shown:
        _thread_warning_shown = True
        warnings.warn(
            "halea module-level functions are not thread-safe. "
            "For multi-threaded use, create separate HaleaNumpy instances per thread.",
            RuntimeWarning,
            stacklevel=4,
        )


def _cleanup_global_rng() -> None:
    """Cleanup function for atexit."""
    global _global_rng
    if _global_rng is not None:
        try:
            _global_rng.disconnect()
        except Exception:
            pass
        _global_rng = None


def _get_rng() -> HaleaNumpy:
    """Get or create the global HaleaNumpy instance.

    Warning:
        Not thread-safe. For concurrent use, instantiate HaleaNumpy per thread.
    """
    global _global_rng
    _check_thread_safety()
    if _global_rng is None:
        rng = HaleaNumpy()
        rng.connect()
        _global_rng = rng
        atexit.register(_cleanup_global_rng)
    return _global_rng


def rand(*shape: int) -> np.float64 | np.ndarray:
    """Generate random floats in [0, 1) using hardware RNG.

    Module-level convenience function. Automatically manages connection.

    Args:
        *shape: Output shape. If empty, returns a single float.

    Returns:
        Random float or array of floats in [0, 1).
    """
    return _get_rng().rand(*shape)


def randn(*shape: int) -> np.float64 | np.ndarray:
    """Generate random floats from standard normal N(0,1) using hardware RNG.

    Module-level convenience function. Automatically manages connection.

    Args:
        *shape: Output shape. If empty, returns a single float.

    Returns:
        Random float or array from standard normal distribution.
    """
    return _get_rng().randn(*shape)


def randint(
    low: int,
    high: int | None = None,
    size: int | tuple[int, ...] | None = None,
) -> np.int64 | np.ndarray:
    """Generate random integers using hardware RNG.

    Args:
        low: Lowest integer (inclusive), or upper bound if high is None.
        high: Upper bound (exclusive).
        size: Output shape.

    Returns:
        Random integer(s).
    """
    return _get_rng().randint(low, high, size)


def choice(
    a: int | np.ndarray,
    size: int | tuple[int, ...] | None = None,
    replace: bool = True,
) -> np.generic | np.ndarray:
    """Random sample using hardware RNG.

    Args:
        a: If int, sample from range(a). If array, sample from it.
        size: Output shape.
        replace: Whether to sample with replacement.

    Returns:
        Random sample(s).
    """
    return _get_rng().choice(a, size, replace)


def bytes(n: int) -> bytes:  # noqa: A001 (shadows builtin intentionally)
    """Return n random bytes using hardware RNG.

    Args:
        n: Number of bytes to return.

    Returns:
        n random bytes.
    """
    return _get_rng().bytes(n)


def bits(n: int) -> np.ndarray:
    """Return array of n random bits using hardware RNG.

    Args:
        n: Number of bits to return.

    Returns:
        Array of n random bits (values 0 or 1).
    """
    return _get_rng().bits(n)


def shuffle(x: MutableSequence[Any] | np.ndarray) -> None:
    """Shuffle sequence in-place using hardware RNG.

    Args:
        x: Sequence to shuffle in-place (list, numpy array, etc.).
    """
    _get_rng().shuffle(x)


def permutation(x: int | np.ndarray) -> np.ndarray:
    """Return shuffled copy or random permutation using hardware RNG.

    Args:
        x: If int, return permutation of range(x).
           If array, return shuffled copy.

    Returns:
        Shuffled array.
    """
    return _get_rng().permutation(x)
