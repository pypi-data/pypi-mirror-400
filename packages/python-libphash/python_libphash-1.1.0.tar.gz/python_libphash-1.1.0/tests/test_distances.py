import pytest
from libphash import Digest, hamming_distance, compare_images, HashMethod


def test_hamming_distance_uint64():
    """Verify Hamming distance logic for 64-bit integers."""
    assert hamming_distance(0b1010, 0b1011) == 1
    assert hamming_distance(0, 0xFFFFFFFFFFFFFFFF) == 64


def test_digest_hamming_distance():
    """Verify Hamming distance between Digest objects."""
    d1 = Digest(b"\x01" * 32, 32)
    d2 = Digest(b"\x00" * 32, 32)
    # 1 bit difference per byte * 32 bytes = 32
    assert d1.distance_hamming(d2) == 32


def test_digest_l2_distance():
    """Verify Euclidean distance between Digest objects."""
    d1 = Digest(bytes([10, 10]), 2)
    d2 = Digest(bytes([14, 13]), 2)
    # sqrt((14-10)^2 + (13-10)^2) = sqrt(16 + 9) = 5.0
    assert abs(d1.distance_l2(d2) - 5.0) < 1e-5


def test_compare_images_utility(image_path: str):
    """Verify high-level image comparison utility."""
    # Compare image with itself
    dist = compare_images(image_path, image_path, method=HashMethod.PHASH)
    assert dist == 0


def test_digest_size_mismatch():
    """Verify that comparing digests of different sizes raises ValueError."""
    d1 = Digest(b"\x00" * 8, 8)
    d2 = Digest(b"\x00" * 16, 16)
    with pytest.raises(ValueError, match="same size"):
        d1.distance_hamming(d2)
