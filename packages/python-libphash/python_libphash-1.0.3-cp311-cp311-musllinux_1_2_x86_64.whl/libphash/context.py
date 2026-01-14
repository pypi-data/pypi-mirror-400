from __future__ import annotations
from pathlib import Path
from typing import Any, final, Callable
from ._native import ffi, lib
from .exceptions import check_error
from .types import Digest


@final
class ImageContext:
    _ptr: Any
    _ctx_ptr_ptr: Any

    def __init__(
        self, path: str | Path | None = None, bytes_data: bytes | None = None
    ) -> None:
        self._ctx_ptr_ptr = ffi.new("ph_context_t **")
        check_error(lib.ph_create(self._ctx_ptr_ptr))
        self._ptr = self._ctx_ptr_ptr[0]

        try:
            if path is not None:
                self.load_from_file(path)
            elif bytes_data is not None:
                self.load_from_memory(bytes_data)
        except Exception:
            self.close()
            raise

    def close(self) -> None:
        if hasattr(self, "_ptr") and self._ptr is not None:
            lib.ph_free(self._ptr)
            self._ptr = None

    def __enter__(self) -> ImageContext:
        return self

    def __exit__(self, exc_type: type[BaseException] | None, *args: Any) -> None:
        self.close()

    def load_from_file(self, path: str | Path) -> None:
        path_obj = Path(path).resolve()
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {path_obj}")
        check_error(lib.ph_load_from_file(self._ptr, str(path_obj).encode()))

    def load_from_memory(self, data: bytes) -> None:
        check_error(lib.ph_load_from_memory(self._ptr, data, len(data)))

    def set_gamma(self, gamma: float) -> None:
        lib.ph_context_set_gamma(self._ptr, float(gamma))

    # Внутренние хелперы теперь типизированы через Callable
    def _uint64_prop(self, func: Callable[[Any, Any], int]) -> int:
        out = ffi.new("uint64_t *")
        check_error(func(self._ptr, out))
        return int(out[0])

    def _digest_prop(self, func: Callable[[Any, Any], int]) -> Digest:
        out = ffi.new("ph_digest_t *")
        check_error(func(self._ptr, out))
        return Digest.from_c_struct(out[0])

    @property
    def ahash(self) -> int:
        return self._uint64_prop(lib.ph_compute_ahash)

    @property
    def dhash(self) -> int:
        return self._uint64_prop(lib.ph_compute_dhash)

    @property
    def phash(self) -> int:
        return self._uint64_prop(lib.ph_compute_phash)

    @property
    def whash(self) -> int:
        return self._uint64_prop(lib.ph_compute_whash)

    @property
    def mhash(self) -> int:
        return self._uint64_prop(lib.ph_compute_mhash)

    @property
    def bmh(self) -> Digest:
        return self._digest_prop(lib.ph_compute_bmh)

    @property
    def color_hash(self) -> Digest:
        return self._digest_prop(lib.ph_compute_color_hash)

    @property
    def radial_hash(self) -> Digest:
        return self._digest_prop(lib.ph_compute_radial_hash)
