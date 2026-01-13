# ⚙️🎲 `HAlea`

Unified access to (some) hardware RNGs for machine learning & scientific computing

## Supported Devices

| Device                                            | Interface  | Backend    |
| ------------------------------------------------- | ---------- | ---------- |
| [TrueRNGpro](https://ubld.it/products/truerngpro) | USB Serial | `truerng`  |
| [ChaosKey](https://altusmetrum.org/ChaosKey/)     | USB Bulk   | `chaoskey` |

## Features

- **Three APIs**: NumPy (`HaleaNumpy`), PyTorch (`HaleaTorch`), JAX (`HaleaJax`)
- **Distributions**: uniform, normal (Box-Muller), integers, bits, bytes
- **Sampling**: `choice()` with/without replacement, `shuffle()`, `permutation()`
- **Auto-detection**: Finds connected devices automatically
- **Buffered I/O**: Efficient bulk reads with configurable buffer size
- **Unbiased mode**: Optional rejection sampling for perfect uniformity

## Quick Start

```python
from halea import HaleaNumpy

with HaleaNumpy() as rng:
    # Uniform [0, 1)
    x = rng.rand(1000)

    # Normal N(0, 1)
    y = rng.randn(100, 100)

    # Integers [0, 100)
    z = rng.randint(100, size=50)

    # Shuffle in-place
    rng.shuffle(my_list)
```

**PyTorch / JAX**:

```python
from halea import HaleaTorch, HaleaJax

with HaleaTorch(device="cuda") as rng:
    tensor = rng.randn(256, 256, dtype=torch.float32)

with HaleaJax() as rng:
    array = rng.normal(shape=(256, 256))
```

## Installation

```bash
pip install halea
```

**Requirements**: `numpy`, `pyserial`, `pyusb`
**Optional**: `torch`, `jax` (for respective APIs)

**Linux udev rules** (for non-root access):

```bash
# TrueRNG
echo 'SUBSYSTEM=="tty", ATTRS{idVendor}=="04d8", ATTRS{idProduct}=="f5fe", MODE="0666"' | sudo tee /etc/udev/rules.d/99-truerng.rules

# ChaosKey
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="1d50", ATTR{idProduct}=="60c6", MODE="0666"' | sudo tee /etc/udev/rules.d/99-chaoskey.rules

sudo udevadm control --reload-rules
```

## Scope & Limitations

- **For ML/scientific use** — not cryptographic applications
- **Single-threaded** — create separate instances for multi-threaded use
- **No entropy monitoring** — assumes device is functioning correctly
- **Linux-focused** — other platforms may work but are untested

## Security Notice

This library provides access to hardware random number generators for
**machine learning and scientific computing applications**. It is
**NOT designed for cryptographic use**.

For cryptographic applications:

1. The default `randint()` uses float-based scaling with negligible bias
   (~1e-15) for ranges under 2^53. Use `unbiased=True` for statistically
   perfect uniformity.

2. No entropy health monitoring is performed. If a device fails, the
   library may return low-quality randomness.

3. For cryptographic random bytes, use Python's `secrets` module or
   read from `/dev/random` directly.
