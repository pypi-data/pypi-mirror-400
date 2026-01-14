from setuptools import setup, Extension
from Cython.Build import cythonize
import platform

machine = platform.machine().lower()
system = platform.system()

extensions = []

# x86/x64 - AES-NI
if machine in ('x86_64', 'amd64', 'x86', 'i386', 'i686'):
    if system == "Windows":
        extra_compile_args = ["/O2", "/arch:AVX"]
    else:
        extra_compile_args = ["-O3", "-maes", "-msse4.1"]
    
    extensions.append(Extension(
        "aesige.aes_ni",
        sources=["aesige/aes_ni.pyx", "aesige/aes_ni_impl.c"],
        extra_compile_args=extra_compile_args,
    ))

# ARM64 - ARM Crypto Extensions
elif machine in ('aarch64', 'arm64'):
    if system == "Darwin":
        extra_compile_args = ["-O3"]
    else:
        extra_compile_args = ["-O3", "-march=armv8-a+crypto"]
    
    extensions.append(Extension(
        "aesige.aes_arm",
        sources=["aesige/aes_arm.pyx", "aesige/aes_arm_impl.c"],
        extra_compile_args=extra_compile_args,
    ))

setup(
    name="aesige",
    version="1.0.0",
    description="Fast AES-256-IGE encryption with hardware acceleration",
    author="xGaDinc",
    packages=["aesige"],
    ext_modules=cythonize(extensions, language_level=3) if extensions else [],
    python_requires=">=3.8",
    setup_requires=["cython"],
)
