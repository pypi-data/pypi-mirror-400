# AesIGE - Fast AES-IGE with hardware acceleration
# Drop-in replacement for tgcrypto

import platform

__version__ = "1.0.0"

_machine = platform.machine().lower()

# Try hardware-accelerated implementations
if _machine in ('x86_64', 'amd64', 'x86', 'i386', 'i686'):
    try:
        from .aes_ni import ige256_encrypt, ige256_decrypt
        _backend = "AES-NI"
    except ImportError:
        _backend = None
elif _machine in ('aarch64', 'arm64'):
    try:
        from .aes_arm import ige256_encrypt, ige256_decrypt
        _backend = "ARM-CE"
    except ImportError:
        _backend = None
else:
    _backend = None

# Fallback to tgcrypto
if _backend is None:
    try:
        from tgcrypto import ige256_encrypt, ige256_decrypt
        _backend = "tgcrypto"
    except ImportError:
        raise ImportError(
            "aesige: No hardware crypto available and tgcrypto not installed. "
            "Install fallback with: pip install tgcrypto"
        )

__all__ = ["ige256_encrypt", "ige256_decrypt", "__version__"]
