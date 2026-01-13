"""
FluxCipher - simple XOR-based reversible cipher
NOT suitable for strong security, provided for compatibility/legacy or obfuscation.
"""
from typing import Optional
from .utils import to_bytes, b64_encode, b64_decode, to_text

def _derive_key_bytes(key: Optional[str], length: int = 32) -> bytes:
    # Create a repeating key bytes of desired length
    if key is None:
        key = "cryzen_default_flux_key"
    kb = to_bytes(key)
    return (kb * (length // len(kb) + 1))[:length]

def flux_encrypt(text: str, key: Optional[str] = None) -> str:
    """
    Encrypt text using repeating-key XOR and return URL-safe base64-ish string.

    Args:
        text: plaintext
        key: secret key (string). If None, a library default is used (not recommended).

    Returns:
        Encrypted string (URL-safe).
    """
    data = to_bytes(text)
    k = _derive_key_bytes(key, len(data))
    out = bytes([b ^ k[i] for i, b in enumerate(data)])
    return b64_encode(out)

def flux_decrypt(token: str, key: Optional[str] = None) -> str:
    """
    Decrypt a token produced by flux_encrypt.

    Args:
        token: encrypted token (string)
        key: secret key (must match encryption key)

    Returns:
        Original plaintext string.
    """
    raw = b64_decode(token)
    k = _derive_key_bytes(key, len(raw))
    out = bytes([b ^ k[i] for i, b in enumerate(raw)])
    return to_text(out)
