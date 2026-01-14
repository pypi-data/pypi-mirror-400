/*
 * AES-IGE implementation with ARM Cryptography Extensions
 * For ARM64 processors (Apple M1/M2, AWS Graviton, etc.)
 */

#if defined(__aarch64__) || defined(_M_ARM64)

#include <stdint.h>
#include <string.h>
#include <arm_neon.h>

// AES-256 key expansion for ARM
static void aes256_key_expansion_arm(const uint8_t *key, uint8x16_t *enc_keys, uint8x16_t *dec_keys) {
    // Load initial key
    enc_keys[0] = vld1q_u8(key);
    enc_keys[1] = vld1q_u8(key + 16);
    
    // AES-256 key schedule (simplified - using lookup table approach)
    static const uint8_t rcon[] = {0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40};
    
    for (int i = 2; i < 15; i++) {
        uint8x16_t temp = enc_keys[i - 1];
        
        if (i % 2 == 0) {
            // RotWord + SubWord + Rcon
            temp = vqtbl1q_u8(temp, (uint8x16_t){13, 14, 15, 12, 13, 14, 15, 12, 13, 14, 15, 12, 13, 14, 15, 12});
            temp = vaeseq_u8(temp, vdupq_n_u8(0));
            temp = veorq_u8(temp, (uint8x16_t){rcon[(i-2)/2], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0});
        } else {
            // SubWord only
            temp = vaeseq_u8(temp, vdupq_n_u8(0));
        }
        
        uint8x16_t prev = enc_keys[i - 2];
        temp = veorq_u8(temp, prev);
        temp = veorq_u8(temp, vextq_u8(vdupq_n_u8(0), prev, 12));
        temp = veorq_u8(temp, vextq_u8(vdupq_n_u8(0), prev, 8));
        temp = veorq_u8(temp, vextq_u8(vdupq_n_u8(0), prev, 4));
        enc_keys[i] = temp;
    }
    
    // Generate decryption keys (inverse mix columns)
    dec_keys[0] = enc_keys[14];
    for (int i = 1; i < 14; i++) {
        dec_keys[i] = vaesimcq_u8(enc_keys[14 - i]);
    }
    dec_keys[14] = enc_keys[0];
}

// Single block AES-256 encrypt
static inline uint8x16_t aes256_encrypt_block_arm(uint8x16_t block, const uint8x16_t *enc_keys) {
    block = vaeseq_u8(block, enc_keys[0]); block = vaesmcq_u8(block);
    block = vaeseq_u8(block, enc_keys[1]); block = vaesmcq_u8(block);
    block = vaeseq_u8(block, enc_keys[2]); block = vaesmcq_u8(block);
    block = vaeseq_u8(block, enc_keys[3]); block = vaesmcq_u8(block);
    block = vaeseq_u8(block, enc_keys[4]); block = vaesmcq_u8(block);
    block = vaeseq_u8(block, enc_keys[5]); block = vaesmcq_u8(block);
    block = vaeseq_u8(block, enc_keys[6]); block = vaesmcq_u8(block);
    block = vaeseq_u8(block, enc_keys[7]); block = vaesmcq_u8(block);
    block = vaeseq_u8(block, enc_keys[8]); block = vaesmcq_u8(block);
    block = vaeseq_u8(block, enc_keys[9]); block = vaesmcq_u8(block);
    block = vaeseq_u8(block, enc_keys[10]); block = vaesmcq_u8(block);
    block = vaeseq_u8(block, enc_keys[11]); block = vaesmcq_u8(block);
    block = vaeseq_u8(block, enc_keys[12]); block = vaesmcq_u8(block);
    block = vaeseq_u8(block, enc_keys[13]);
    return veorq_u8(block, enc_keys[14]);
}

// Single block AES-256 decrypt
static inline uint8x16_t aes256_decrypt_block_arm(uint8x16_t block, const uint8x16_t *dec_keys) {
    block = vaesdq_u8(block, dec_keys[0]); block = vaesimcq_u8(block);
    block = vaesdq_u8(block, dec_keys[1]); block = vaesimcq_u8(block);
    block = vaesdq_u8(block, dec_keys[2]); block = vaesimcq_u8(block);
    block = vaesdq_u8(block, dec_keys[3]); block = vaesimcq_u8(block);
    block = vaesdq_u8(block, dec_keys[4]); block = vaesimcq_u8(block);
    block = vaesdq_u8(block, dec_keys[5]); block = vaesimcq_u8(block);
    block = vaesdq_u8(block, dec_keys[6]); block = vaesimcq_u8(block);
    block = vaesdq_u8(block, dec_keys[7]); block = vaesimcq_u8(block);
    block = vaesdq_u8(block, dec_keys[8]); block = vaesimcq_u8(block);
    block = vaesdq_u8(block, dec_keys[9]); block = vaesimcq_u8(block);
    block = vaesdq_u8(block, dec_keys[10]); block = vaesimcq_u8(block);
    block = vaesdq_u8(block, dec_keys[11]); block = vaesimcq_u8(block);
    block = vaesdq_u8(block, dec_keys[12]); block = vaesimcq_u8(block);
    block = vaesdq_u8(block, dec_keys[13]);
    return veorq_u8(block, dec_keys[14]);
}

// AES-256-IGE decrypt with ARM CE
void aes256_ige_decrypt_arm(
    const uint8_t *in,
    uint8_t *out,
    size_t len,
    const uint8_t *key,
    const uint8_t *iv
) {
    uint8x16_t enc_keys[15], dec_keys[15];
    aes256_key_expansion_arm(key, enc_keys, dec_keys);
    
    uint8x16_t prev_cipher = vld1q_u8(iv);
    uint8x16_t prev_plain = vld1q_u8(iv + 16);
    
    for (size_t i = 0; i < len; i += 16) {
        uint8x16_t cipher_block = vld1q_u8(in + i);
        
        // IGE: m_i = decrypt(c_i XOR m_{i-1}) XOR c_{i-1}
        uint8x16_t xored = veorq_u8(cipher_block, prev_plain);
        uint8x16_t decrypted = aes256_decrypt_block_arm(xored, dec_keys);
        uint8x16_t plain_block = veorq_u8(decrypted, prev_cipher);
        
        vst1q_u8(out + i, plain_block);
        
        prev_cipher = cipher_block;
        prev_plain = plain_block;
    }
}

// AES-256-IGE encrypt with ARM CE
void aes256_ige_encrypt_arm(
    const uint8_t *in,
    uint8_t *out,
    size_t len,
    const uint8_t *key,
    const uint8_t *iv
) {
    uint8x16_t enc_keys[15], dec_keys[15];
    aes256_key_expansion_arm(key, enc_keys, dec_keys);
    
    uint8x16_t prev_cipher = vld1q_u8(iv);
    uint8x16_t prev_plain = vld1q_u8(iv + 16);
    
    for (size_t i = 0; i < len; i += 16) {
        uint8x16_t plain_block = vld1q_u8(in + i);
        
        // IGE: c_i = encrypt(m_i XOR c_{i-1}) XOR m_{i-1}
        uint8x16_t xored = veorq_u8(plain_block, prev_cipher);
        uint8x16_t encrypted = aes256_encrypt_block_arm(xored, enc_keys);
        uint8x16_t cipher_block = veorq_u8(encrypted, prev_plain);
        
        vst1q_u8(out + i, cipher_block);
        
        prev_cipher = cipher_block;
        prev_plain = plain_block;
    }
}

#endif /* __aarch64__ */
