import pytest
from libphash import ImageContext, DecodeError


def test_context_lifecycle():
    """Verify context creation and manual/automatic cleanup."""
    with ImageContext() as ctx:
        assert ctx is not None

    ctx_manual = ImageContext()
    ctx_manual.close()


def test_load_from_file(image_path: str):
    """Verify loading from a valid file path."""
    with ImageContext(path=image_path) as ctx:
        # Accessing a property ensures the image was loaded correctly
        assert isinstance(ctx.phash, int)


def test_load_from_file_not_found():
    """Verify FileNotFoundError is raised for missing files."""
    with pytest.raises(FileNotFoundError):
        ImageContext(path="non_existent.jpg")


def test_load_from_memory(sample_jpeg_bytes: bytes):
    """Verify loading from raw bytes."""
    with ImageContext(bytes_data=sample_jpeg_bytes) as ctx:
        assert ctx.phash > 0


def test_load_invalid_data():
    """Verify DecodeError is raised for malformed image data."""
    with ImageContext() as ctx:
        with pytest.raises(DecodeError):
            ctx.load_from_memory(b"invalid_data_not_an_image")
