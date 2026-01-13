"""HAlea: Unified hardware RNG for ML & scientific computing.

This package provides a unified interface to hardware random number generators
(TrueRNG and ChaosKey) with NumPy, PyTorch, and JAX APIs.

Quick Start
-----------
Auto-detect device and use module-level functions:

    >>> from halea import rand, shuffle
    >>> x = rand(10)  # 10 random floats in [0, 1)
    >>> arr = [1, 2, 3, 4, 5]
    >>> shuffle(arr)

Use explicit backend with context manager:

    >>> from halea import HaleaNumpy
    >>> with HaleaNumpy(backend="truerng") as rng:
    ...     data = rng.bytes(1024)
    ...     perm = rng.permutation(10)

PyTorch API:

    >>> from halea import HaleaTorch
    >>> with HaleaTorch(device="cuda") as rng:
    ...     x = rng.randn(32, 32)

JAX API:

    >>> from halea import HaleaJax
    >>> with HaleaJax() as rng:
    ...     x = rng.uniform(shape=(10, 10))

Device Discovery
----------------
List all available hardware RNG devices:

    >>> from halea import find_all_devices
    >>> find_all_devices()
    {'truerng': [...], 'chaoskey': [...]}

Supported Devices
-----------------
- TrueRNG V1/V2/V3 (USB VID:PID 04D8:F5FE)
- TrueRNGpro V1 (USB VID:PID 16D0:0AA0)
- TrueRNGpro V2 (USB VID:PID 04D8:EBB5)
- ChaosKey (USB VID:PID 1D50:60C6)
"""

from halea._version import __version__
from halea.backends import find_all_devices
from halea.backends import get_backend
from halea.exceptions import BackendNotAvailableError
from halea.exceptions import DeviceConnectionError
from halea.exceptions import DeviceNotFoundError
from halea.exceptions import DeviceReadError
from halea.exceptions import HaleaError
from halea.numpy import bits
from halea.numpy import bytes
from halea.numpy import choice
from halea.numpy import HaleaNumpy
from halea.numpy import permutation
from halea.numpy import rand
from halea.numpy import randint
from halea.numpy import shuffle

__all__ = [
    # Version
    "__version__",
    # Exceptions
    "HaleaError",
    "DeviceNotFoundError",
    "DeviceConnectionError",
    "DeviceReadError",
    "BackendNotAvailableError",
    # Backend utilities
    "get_backend",
    "find_all_devices",
    # NumPy API
    "HaleaNumpy",
    "rand",
    "randint",
    "choice",
    "bytes",
    "bits",
    "shuffle",
    "permutation",
    # PyTorch API (None if unavailable)
    "HaleaTorch",
    # JAX API (None if unavailable)
    "HaleaJax",
]

# Conditional imports for optional framework support
try:
    from halea.torch import HaleaTorch
except ImportError:
    HaleaTorch = None  # type: ignore[misc, assignment]

try:
    from halea.jax import HaleaJax
except ImportError:
    HaleaJax = None  # type: ignore[misc, assignment]
