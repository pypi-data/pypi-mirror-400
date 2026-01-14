#ifndef AES_NI_IMPL_H
#define AES_NI_IMPL_H

#include <stdint.h>
#include <stddef.h>

void aes256_ige_decrypt_ni(
    const uint8_t *in,
    uint8_t *out,
    size_t len,
    const uint8_t *key,
    const uint8_t *iv
);

void aes256_ige_encrypt_ni(
    const uint8_t *in,
    uint8_t *out,
    size_t len,
    const uint8_t *key,
    const uint8_t *iv
);

#endif
