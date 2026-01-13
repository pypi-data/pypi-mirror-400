"""
OmegaHash - ultra-strong hashing using PBKDF2-HMAC-SHA512
This is designed for password storage / highest strength irreversible hashing.

Provides:
- omega_hash(password, salt=None, iterations=200_000) -> token
Token contains salt + hex derived key separated by $
Format: salt$hex
"""
import os
import hashlib
import binascii
from typing import Optional
from .utils import to_hex, to_bytes

def omega_hash(password: str, salt: Optional[str] = None, iterations: int = 200_000) -> str:
    if salt is None:
        salt_bytes = os.urandom(16)
    else:
        salt_bytes = to_bytes(salt)
    dk = hashlib.pbkdf2_hmac("sha512", to_bytes(password), salt_bytes, iterations, dklen=64)
    return to_hex(salt_bytes) + "$" + to_hex(dk)
