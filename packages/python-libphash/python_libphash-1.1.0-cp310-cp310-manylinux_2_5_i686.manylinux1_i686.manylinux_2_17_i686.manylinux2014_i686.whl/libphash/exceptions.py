from __future__ import annotations


class PhashError(Exception):
    """Base exception for libphash library."""


class AllocationError(PhashError):
    """Raised when memory allocation fails in the C layer."""


class DecodeError(PhashError):
    """Raised when image decoding fails (stb_image error)."""


class InvalidArgumentError(PhashError):
    """Raised when an invalid argument is passed to the C function."""


def check_error(err_code: int) -> None:
    """Map C return codes to Python exceptions."""
    if err_code == 0:
        return

    errors: dict[int, tuple[type[PhashError], str]] = {
        -1: (AllocationError, "Memory allocation failed in libphash"),
        -2: (DecodeError, "Failed to decode image (stb_image error)"),
        -3: (InvalidArgumentError, "Invalid argument provided to libphash"),
        -4: (PhashError, "Feature not implemented"),
        -5: (PhashError, "Image is empty or invalid"),
    }

    exc_class, msg = errors.get(
        err_code, (PhashError, f"Unknown error code: {err_code}")
    )
    raise exc_class(msg)
