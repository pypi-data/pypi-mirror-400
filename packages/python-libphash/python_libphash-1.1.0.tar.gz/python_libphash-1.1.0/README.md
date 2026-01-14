# python-libphash

High-performance Python bindings for [libphash](https://github.com/gudoshnikovn/libphash) v1.3.0, a C library for perceptual image hashing.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Overview

`libphash` provides multiple algorithms to generate "perceptual hashes" of images. Unlike cryptographic hashes (like MD5 or SHA256), perceptual hashes change only slightly if the image is resized, compressed, or has minor color adjustments. This makes them ideal for finding duplicate or similar images.

### Supported Algorithms

*   **64-bit Hashes (uint64):**
    *   `ahash`: Average Hash
    *   `dhash`: Difference Hash
    *   `phash`: Perceptual Hash (DCT based)
    *   `whash`: Wavelet Hash
    *   `mhash`: Median Hash
*   **Digest Hashes (Multi-byte):**
    *   `bmh`: Block Mean Hash
    *   `color_hash`: Color Moment Hash
    *   `radial_hash`: Radial Variance Hash

## Installation

### Prerequisites
*   A C compiler (GCC/Clang or MSVC)
*   Python 3.8 or higher

### Install from source
```bash
git clone --recursive https://github.com/yourusername/python-libphash.git
cd python-libphash
pip install .
```

## Quick Start

### Basic Usage
```python
from libphash import ImageContext, HashMethod, hamming_distance

# Use the context manager for automatic memory management
with ImageContext("photo.jpg") as ctx:
    # Get standard 64-bit hashes
    phash_val = ctx.phash
    dhash_val = ctx.dhash
    
    print(f"pHash: {phash_val:016x}")
    print(f"dHash: {dhash_val:016x}")

# Compare two images
from libphash import compare_images
distance = compare_images("image1.jpg", "image2.jpg", method=HashMethod.PHASH)
print(f"Hamming Distance: {distance}")
```

### Working with Digests (Advanced Hashes)
Algorithms like Radial Hash or Color Hash return a `Digest` object instead of a single integer.

```python
with ImageContext("photo.jpg") as ctx:
    digest = ctx.radial_hash
    print(f"Digest size: {digest.size} bytes")
    print(f"Raw data: {digest.data.hex()}")

# Comparing digests
with ImageContext("photo_v2.jpg") as ctx2:
    digest2 = ctx2.radial_hash
    
    # Hamming distance for bit-wise comparison
    h_dist = digest.distance_hamming(digest2)
    
    # L2 (Euclidean) distance for similarity
    l2_dist = digest.distance_l2(digest2)
```

## API Reference

### `ImageContext`
The main class for loading images and computing hashes.
*   `__init__(path=None, bytes_data=None)`: Load an image from a file path or memory.
*   `set_gamma(gamma: float)`: Set gamma correction (useful for Radial Hash).
*   **Properties**: `ahash`, `dhash`, `phash`, `whash`, `mhash` (returns `int`).
*   **Properties**: `bmh`, `color_hash`, `radial_hash` (returns `Digest`).

### `Digest`
*   `data`: The raw `bytes` of the hash.
*   `size`: Length of the hash in bytes.
*   `distance_hamming(other)`: Calculates bit-wise distance.
*   `distance_l2(other)`: Calculates Euclidean distance.

### Utilities
*   `hamming_distance(h1: int, h2: int)`: Returns the number of differing bits between two 64-bit integers.
*   `get_hash(path, method)`: Quick way to get a hash without manual context management.
*   `compare_images(path1, path2, method)`: Returns the Hamming distance between two image files.

## Performance
Since the core logic is implemented in C and uses `stb_image` for decoding, `libphash` is significantly faster than pure-Python alternatives. It also uses CFFI's "out-of-line" mode for minimal overhead.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

