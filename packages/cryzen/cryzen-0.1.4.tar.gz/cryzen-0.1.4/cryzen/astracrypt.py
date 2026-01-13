"""
AstraCrypt - AES-256-CBC based encryption (reversible)
Requires: pycryptodome (install with `pip install pycryptodome`)

This module provides:
- astra_encrypt(plaintext, secret_key) -> token (urlsafe base64)
- astra_decrypt(token, secret_key) -> plaintext

Implementation details:
- Derive 32-byte AES key by hashing the provided secret_key (SHA256).
- Uses random IV (16 bytes) per encryption and PKCS7 padding.
- Token format: base64url( iv + ciphertext )
"""
from typing import Optional
from .utils import to_bytes, to_text, b64_encode, b64_decode, to_hex
import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

BLOCK_SIZE = AES.block_size  # 16

def _pad(data: bytes) -> bytes:
    pad_len = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + bytes([pad_len]) * pad_len

def _unpad(data: bytes) -> bytes:
    if not data:
        return b""
    pad_len = data[-1]
    if pad_len < 1 or pad_len > BLOCK_SIZE:
        raise ValueError("Invalid padding")
    return data[:-pad_len]

def _derive_key(secret_key: Optional[str]) -> bytes:
    if secret_key is None:
        secret_key = "cryzen_default_astra_key"
    return hashlib.sha256(to_bytes(secret_key)).digest()

def astra_encrypt(plaintext: str, secret_key: Optional[str]) -> str:
    """
    Encrypt plaintext with AES-256-CBC. Returns URL-safe token.
    """
    key = _derive_key(secret_key)
    iv = get_random_bytes(BLOCK_SIZE)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct = cipher.encrypt(_pad(to_bytes(plaintext)))
    return b64_encode(iv + ct)

def astra_decrypt(token: str, secret_key: Optional[str]) -> str:
    """
    Decrypt token produced by astra_encrypt.
    """
    raw = b64_decode(token)
    iv = raw[:BLOCK_SIZE]
    ct = raw[BLOCK_SIZE:]
    key = _derive_key(secret_key)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = _unpad(cipher.decrypt(ct))
    return to_text(pt)
