from libphash import ImageContext, Digest


def test_bmh_digest(sample_jpeg_bytes: bytes):
    """Verify Block Mean Hash digest properties."""
    with ImageContext(bytes_data=sample_jpeg_bytes) as ctx:
        digest = ctx.bmh
        assert isinstance(digest, Digest)
        assert digest.size == 32
        assert len(digest.data) == 32


def test_color_hash_digest(sample_jpeg_bytes: bytes):
    """Verify Color Moment Hash digest properties."""
    with ImageContext(bytes_data=sample_jpeg_bytes) as ctx:
        digest = ctx.color_hash
        assert digest.size == 9
        assert len(digest.data) == 9


def test_radial_hash_digest(sample_jpeg_bytes: bytes):
    """Verify Radial Variance Hash digest properties with gamma correction."""
    with ImageContext(bytes_data=sample_jpeg_bytes) as ctx:
        ctx.set_gamma(2.2)
        digest = ctx.radial_hash
        assert digest.size == 40
        assert len(digest.data) == 40
