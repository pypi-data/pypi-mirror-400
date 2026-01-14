/*
 * AES-IGE implementation with AES-NI intrinsics
 * For maximum performance on modern CPUs
 */

#include <stdint.h>
#include <string.h>

#ifdef _MSC_VER
#include <intrin.h>
#define cpuid(info, x) __cpuidex(info, x, 0)
#else
#include <x86intrin.h>
#include <cpuid.h>
#define cpuid(info, x) __cpuid_count(x, 0, info[0], info[1], info[2], info[3])
#endif

// Check for AES-NI support at runtime
static int has_aesni = -1;

static int check_aesni(void) {
    if (has_aesni >= 0) return has_aesni;
    int cpuinfo[4];
    cpuid(cpuinfo, 1);
    has_aesni = (cpuinfo[2] & (1 << 25)) != 0;
    return has_aesni;
}

// Helper for key expansion
static inline __m128i aes256_key_expand_1(__m128i key, __m128i keygened) {
    keygened = _mm_shuffle_epi32(keygened, 0xff);
    key = _mm_xor_si128(key, _mm_slli_si128(key, 4));
    key = _mm_xor_si128(key, _mm_slli_si128(key, 4));
    key = _mm_xor_si128(key, _mm_slli_si128(key, 4));
    return _mm_xor_si128(key, keygened);
}

static inline __m128i aes256_key_expand_2(__m128i key, __m128i keygened) {
    keygened = _mm_shuffle_epi32(keygened, 0xaa);
    key = _mm_xor_si128(key, _mm_slli_si128(key, 4));
    key = _mm_xor_si128(key, _mm_slli_si128(key, 4));
    key = _mm_xor_si128(key, _mm_slli_si128(key, 4));
    return _mm_xor_si128(key, keygened);
}

// AES-256 key expansion
static void aes256_key_expansion(const uint8_t *key, __m128i *enc_keys, __m128i *dec_keys) {
    enc_keys[0] = _mm_loadu_si128((const __m128i*)key);
    enc_keys[1] = _mm_loadu_si128((const __m128i*)(key + 16));
    
    enc_keys[2] = aes256_key_expand_1(enc_keys[0], _mm_aeskeygenassist_si128(enc_keys[1], 0x01));
    enc_keys[3] = aes256_key_expand_2(enc_keys[1], _mm_aeskeygenassist_si128(enc_keys[2], 0x00));
    enc_keys[4] = aes256_key_expand_1(enc_keys[2], _mm_aeskeygenassist_si128(enc_keys[3], 0x02));
    enc_keys[5] = aes256_key_expand_2(enc_keys[3], _mm_aeskeygenassist_si128(enc_keys[4], 0x00));
    enc_keys[6] = aes256_key_expand_1(enc_keys[4], _mm_aeskeygenassist_si128(enc_keys[5], 0x04));
    enc_keys[7] = aes256_key_expand_2(enc_keys[5], _mm_aeskeygenassist_si128(enc_keys[6], 0x00));
    enc_keys[8] = aes256_key_expand_1(enc_keys[6], _mm_aeskeygenassist_si128(enc_keys[7], 0x08));
    enc_keys[9] = aes256_key_expand_2(enc_keys[7], _mm_aeskeygenassist_si128(enc_keys[8], 0x00));
    enc_keys[10] = aes256_key_expand_1(enc_keys[8], _mm_aeskeygenassist_si128(enc_keys[9], 0x10));
    enc_keys[11] = aes256_key_expand_2(enc_keys[9], _mm_aeskeygenassist_si128(enc_keys[10], 0x00));
    enc_keys[12] = aes256_key_expand_1(enc_keys[10], _mm_aeskeygenassist_si128(enc_keys[11], 0x20));
    enc_keys[13] = aes256_key_expand_2(enc_keys[11], _mm_aeskeygenassist_si128(enc_keys[12], 0x00));
    enc_keys[14] = aes256_key_expand_1(enc_keys[12], _mm_aeskeygenassist_si128(enc_keys[13], 0x40));
    
    // Generate decryption keys (inverse mix columns)
    dec_keys[0] = enc_keys[14];
    dec_keys[1] = _mm_aesimc_si128(enc_keys[13]);
    dec_keys[2] = _mm_aesimc_si128(enc_keys[12]);
    dec_keys[3] = _mm_aesimc_si128(enc_keys[11]);
    dec_keys[4] = _mm_aesimc_si128(enc_keys[10]);
    dec_keys[5] = _mm_aesimc_si128(enc_keys[9]);
    dec_keys[6] = _mm_aesimc_si128(enc_keys[8]);
    dec_keys[7] = _mm_aesimc_si128(enc_keys[7]);
    dec_keys[8] = _mm_aesimc_si128(enc_keys[6]);
    dec_keys[9] = _mm_aesimc_si128(enc_keys[5]);
    dec_keys[10] = _mm_aesimc_si128(enc_keys[4]);
    dec_keys[11] = _mm_aesimc_si128(enc_keys[3]);
    dec_keys[12] = _mm_aesimc_si128(enc_keys[2]);
    dec_keys[13] = _mm_aesimc_si128(enc_keys[1]);
    dec_keys[14] = enc_keys[0];
}

// Single block AES-256 decrypt with AES-NI
static inline __m128i aes256_decrypt_block(__m128i block, const __m128i *dec_keys) {
    block = _mm_xor_si128(block, dec_keys[0]);
    block = _mm_aesdec_si128(block, dec_keys[1]);
    block = _mm_aesdec_si128(block, dec_keys[2]);
    block = _mm_aesdec_si128(block, dec_keys[3]);
    block = _mm_aesdec_si128(block, dec_keys[4]);
    block = _mm_aesdec_si128(block, dec_keys[5]);
    block = _mm_aesdec_si128(block, dec_keys[6]);
    block = _mm_aesdec_si128(block, dec_keys[7]);
    block = _mm_aesdec_si128(block, dec_keys[8]);
    block = _mm_aesdec_si128(block, dec_keys[9]);
    block = _mm_aesdec_si128(block, dec_keys[10]);
    block = _mm_aesdec_si128(block, dec_keys[11]);
    block = _mm_aesdec_si128(block, dec_keys[12]);
    block = _mm_aesdec_si128(block, dec_keys[13]);
    return _mm_aesdeclast_si128(block, dec_keys[14]);
}

// AES-256-IGE decrypt with AES-NI
// Formula: m_i = decrypt(c_i XOR m_{i-1}) XOR c_{i-1}
// IV: first 16 bytes = c_0 (previous cipher), next 16 bytes = m_0 (previous plain)
void aes256_ige_decrypt_ni(
    const uint8_t *in,
    uint8_t *out,
    size_t len,
    const uint8_t *key,
    const uint8_t *iv
) {
    if (!check_aesni()) {
        return;
    }
    
    __m128i enc_keys[15], dec_keys[15];
    aes256_key_expansion(key, enc_keys, dec_keys);
    
    // IV format for Telegram: first 16 bytes = c_0, next 16 bytes = m_0
    __m128i prev_cipher = _mm_loadu_si128((const __m128i*)iv);
    __m128i prev_plain = _mm_loadu_si128((const __m128i*)(iv + 16));
    
    for (size_t i = 0; i < len; i += 16) {
        __m128i cipher_block = _mm_loadu_si128((const __m128i*)(in + i));
        
        // IGE decrypt: m_i = decrypt(c_i XOR m_{i-1}) XOR c_{i-1}
        __m128i xored = _mm_xor_si128(cipher_block, prev_plain);
        __m128i decrypted = aes256_decrypt_block(xored, dec_keys);
        __m128i plain_block = _mm_xor_si128(decrypted, prev_cipher);
        
        _mm_storeu_si128((__m128i*)(out + i), plain_block);
        
        // Update: prev_cipher = c_i, prev_plain = m_i
        prev_cipher = cipher_block;
        prev_plain = plain_block;
    }
}

// Single block AES-256 encrypt with AES-NI
static inline __m128i aes256_encrypt_block(__m128i block, const __m128i *enc_keys) {
    block = _mm_xor_si128(block, enc_keys[0]);
    block = _mm_aesenc_si128(block, enc_keys[1]);
    block = _mm_aesenc_si128(block, enc_keys[2]);
    block = _mm_aesenc_si128(block, enc_keys[3]);
    block = _mm_aesenc_si128(block, enc_keys[4]);
    block = _mm_aesenc_si128(block, enc_keys[5]);
    block = _mm_aesenc_si128(block, enc_keys[6]);
    block = _mm_aesenc_si128(block, enc_keys[7]);
    block = _mm_aesenc_si128(block, enc_keys[8]);
    block = _mm_aesenc_si128(block, enc_keys[9]);
    block = _mm_aesenc_si128(block, enc_keys[10]);
    block = _mm_aesenc_si128(block, enc_keys[11]);
    block = _mm_aesenc_si128(block, enc_keys[12]);
    block = _mm_aesenc_si128(block, enc_keys[13]);
    return _mm_aesenclast_si128(block, enc_keys[14]);
}

// AES-256-IGE encrypt with AES-NI
// Formula: c_i = encrypt(m_i XOR c_{i-1}) XOR m_{i-1}
// IV: first 16 bytes = c_0 (previous cipher), next 16 bytes = m_0 (previous plain)
void aes256_ige_encrypt_ni(
    const uint8_t *in,
    uint8_t *out,
    size_t len,
    const uint8_t *key,
    const uint8_t *iv
) {
    if (!check_aesni()) {
        return;
    }
    
    __m128i enc_keys[15], dec_keys[15];
    aes256_key_expansion(key, enc_keys, dec_keys);
    
    // IV format for Telegram: first 16 bytes = c_0, next 16 bytes = m_0
    __m128i prev_cipher = _mm_loadu_si128((const __m128i*)iv);
    __m128i prev_plain = _mm_loadu_si128((const __m128i*)(iv + 16));
    
    for (size_t i = 0; i < len; i += 16) {
        __m128i plain_block = _mm_loadu_si128((const __m128i*)(in + i));
        
        // IGE encrypt: c_i = encrypt(m_i XOR c_{i-1}) XOR m_{i-1}
        __m128i xored = _mm_xor_si128(plain_block, prev_cipher);
        __m128i encrypted = aes256_encrypt_block(xored, enc_keys);
        __m128i cipher_block = _mm_xor_si128(encrypted, prev_plain);
        
        _mm_storeu_si128((__m128i*)(out + i), cipher_block);
        
        // Update: prev_cipher = c_i, prev_plain = m_i
        prev_cipher = cipher_block;
        prev_plain = plain_block;
    }
}
