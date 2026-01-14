# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False

"""
AES-NI accelerated AES-IGE implementation.
Falls back to tgcrypto if AES-NI not available.
"""

from cpython.bytes cimport PyBytes_FromStringAndSize
from libc.stdlib cimport malloc, free
from libc.string cimport memcpy

cdef extern from "aes_ni_impl.h":
    void aes256_ige_decrypt_ni(
        const unsigned char *input,
        unsigned char *output,
        size_t length,
        const unsigned char *key,
        const unsigned char *iv
    )
    void aes256_ige_encrypt_ni(
        const unsigned char *input,
        unsigned char *output,
        size_t length,
        const unsigned char *key,
        const unsigned char *iv
    )

# Fallback to tgcrypto
try:
    import tgcrypto as _tgcrypto
    _has_fallback = True
except ImportError:
    _has_fallback = False

cpdef bytes ige256_decrypt(bytes data, bytes key, bytes iv):
    """AES-256-IGE decrypt with AES-NI acceleration."""
    cdef size_t length = len(data)
    cdef unsigned char *output = <unsigned char*>malloc(length)
    
    if output == NULL:
        raise MemoryError("Cannot allocate output buffer")
    
    try:
        aes256_ige_decrypt_ni(
            <const unsigned char*>data,
            output,
            length,
            <const unsigned char*>key,
            <const unsigned char*>iv
        )
        return PyBytes_FromStringAndSize(<char*>output, length)
    finally:
        free(output)

cpdef bytes ige256_encrypt(bytes data, bytes key, bytes iv):
    """AES-256-IGE encrypt with AES-NI acceleration."""
    cdef size_t length = len(data)
    cdef unsigned char *output = <unsigned char*>malloc(length)
    
    if output == NULL:
        raise MemoryError("Cannot allocate output buffer")
    
    try:
        aes256_ige_encrypt_ni(
            <const unsigned char*>data,
            output,
            length,
            <const unsigned char*>key,
            <const unsigned char*>iv
        )
        return PyBytes_FromStringAndSize(<char*>output, length)
    finally:
        free(output)
