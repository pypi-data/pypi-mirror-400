# AesIGE

Fast AES-256-IGE encryption with **hardware acceleration**.

- **x86/x64**: AES-NI instructions (Intel/AMD)
- **ARM64**: ARM Crypto Extensions (Apple M1/M2, AWS Graviton)

Drop-in replacement for `tgcrypto` - **2-3x faster**.

## Installation

```bash
pip install aesige
```

## Usage

```python
import aesige

key = b"0" * 32  # 256-bit key
iv = b"0" * 32   # 256-bit IV
data = b"x" * 32  # Must be multiple of 16

encrypted = aesige.ige256_encrypt(data, key, iv)
decrypted = aesige.ige256_decrypt(encrypted, key, iv)
```

## Benchmarks (x86_64)

| Library | Decrypt (1KB) | Encrypt (1KB) |
|---------|---------------|---------------|
| tgcrypto | 14.8 µs | 24.3 µs |
| **aesige** | **7.4 µs** | **7.7 µs** |
| Speedup | **2x** | **3.2x** |

## Supported Platforms

| Platform | Backend |
|----------|---------|
| Windows/Linux/macOS x64 | AES-NI |
| macOS ARM (M1/M2) | ARM CE |
| Linux ARM64 | ARM CE |
| Other | tgcrypto fallback |

## License

Apache License 2.0
