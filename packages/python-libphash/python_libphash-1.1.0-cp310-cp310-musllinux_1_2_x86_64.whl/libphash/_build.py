import os
import glob
from cffi import FFI

ffibuilder = FFI()

# 1. Define the C definitions exposed to Python
# We strip macros like PH_API for CFFI parsing
ffibuilder.cdef("""
    // Constants
    #define PH_DIGEST_MAX_BYTES 64

    // Error Codes
    typedef enum {
        PH_SUCCESS = 0,
        PH_ERR_ALLOCATION_FAILED = -1,
        PH_ERR_DECODE_FAILED = -2,
        PH_ERR_INVALID_ARGUMENT = -3,
        PH_ERR_NOT_IMPLEMENTED = -4,
        PH_ERR_EMPTY_IMAGE = -5,
        ...
    } ph_error_t;

    // Types
    typedef struct ph_context ph_context_t;

    typedef struct {
        uint8_t data[PH_DIGEST_MAX_BYTES];
        uint8_t size;
        uint8_t reserved[7];
    } ph_digest_t;

    // Lifecycle
    const char *ph_version(void);
    ph_error_t ph_create(ph_context_t **out_ctx);
    void ph_free(ph_context_t *ctx);
    void ph_context_set_gamma(ph_context_t *ctx, float gamma);

    // Loading
    ph_error_t ph_load_from_file(ph_context_t *ctx, const char *filepath);
    ph_error_t ph_load_from_memory(ph_context_t *ctx, const uint8_t *buffer, size_t length);

    // uint64 Hashes
    ph_error_t ph_compute_ahash(ph_context_t *ctx, uint64_t *out_hash);
    ph_error_t ph_compute_dhash(ph_context_t *ctx, uint64_t *out_hash);
    ph_error_t ph_compute_phash(ph_context_t *ctx, uint64_t *out_hash);
    ph_error_t ph_compute_whash(ph_context_t *ctx, uint64_t *out_hash);
    ph_error_t ph_compute_mhash(ph_context_t *ctx, uint64_t *out_hash);

    // Digest Hashes
    ph_error_t ph_compute_bmh(ph_context_t *ctx, ph_digest_t *out_digest);
    ph_error_t ph_compute_color_hash(ph_context_t *ctx, ph_digest_t *out_digest);
    ph_error_t ph_compute_radial_hash(ph_context_t *ctx, ph_digest_t *out_digest);

    // Comparison
    int ph_hamming_distance(uint64_t hash1, uint64_t hash2);
    int ph_hamming_distance_digest(const ph_digest_t *a, const ph_digest_t *b);
    double ph_l2_distance(const ph_digest_t *a, const ph_digest_t *b);
""")

# 2. Configure the Source Compilation
# We need to find all .c files in the native directory
curr_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(curr_dir, "../../"))
native_dir = os.path.abspath(os.path.join(project_root, "native", "libphash"))

sources = []
sources.extend(glob.glob(os.path.join(native_dir, "src", "*.c")))
sources.extend(glob.glob(os.path.join(native_dir, "src", "hashes", "*.c")))

include_dirs = ["native/libphash/include"]
source_files = [
    "native/libphash/src/core.c",
    "native/libphash/src/image.c",
    "native/libphash/src/hashes/ahash.c",
    "native/libphash/src/hashes/bmh.c",
    "native/libphash/src/hashes/color_hash.c",
    "native/libphash/src/hashes/common.c",
    "native/libphash/src/hashes/dhash.c",
    "native/libphash/src/hashes/mhash.c",
    "native/libphash/src/hashes/phash.c",
    "native/libphash/src/hashes/radial.c",
    "native/libphash/src/hashes/whash.c",
]

ffibuilder.set_source(
    "libphash._native",
    '#include "libphash.h"',
    sources=source_files,
    include_dirs=include_dirs,
    libraries=["m"] if os.name == "posix" else [],
    extra_compile_args=["-O3", "-Wall", "-fPIC"]
    if os.name == "posix"
    else ["/O2", "/W3"],
)
if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
