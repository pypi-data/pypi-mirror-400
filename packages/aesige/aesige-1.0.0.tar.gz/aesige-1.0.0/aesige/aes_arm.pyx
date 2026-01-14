# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False

"""ARM Crypto Extensions AES-IGE implementation."""

from cpython.bytes cimport PyBytes_FromStringAndSize
from libc.stdlib cimport malloc, free

cdef extern from "aes_arm_impl.h":
    void aes256_ige_decrypt_arm(
        const unsigned char *input,
        unsigned char *output,
        size_t length,
        const unsigned char *key,
        const unsigned char *iv
    )
    void aes256_ige_encrypt_arm(
        const unsigned char *input,
        unsigned char *output,
        size_t length,
        const unsigned char *key,
        const unsigned char *iv
    )

cpdef bytes ige256_decrypt(bytes data, bytes key, bytes iv):
    """AES-256-IGE decrypt with ARM CE acceleration."""
    cdef size_t length = len(data)
    cdef unsigned char *output = <unsigned char*>malloc(length)
    
    if output == NULL:
        raise MemoryError("Cannot allocate output buffer")
    
    try:
        aes256_ige_decrypt_arm(
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
    """AES-256-IGE encrypt with ARM CE acceleration."""
    cdef size_t length = len(data)
    cdef unsigned char *output = <unsigned char*>malloc(length)
    
    if output == NULL:
        raise MemoryError("Cannot allocate output buffer")
    
    try:
        aes256_ige_encrypt_arm(
            <const unsigned char*>data,
            output,
            length,
            <const unsigned char*>key,
            <const unsigned char*>iv
        )
        return PyBytes_FromStringAndSize(<char*>output, length)
    finally:
        free(output)
