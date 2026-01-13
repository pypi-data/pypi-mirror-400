"""
NovaHash - fast irreversible hash.
Internally uses BLAKE2b with digest_size=20 for speed and compactness.
"""
import hashlib
from .utils import to_hex, to_bytes

def nova_hash(text: str, salt: str = "") -> str:
    """
    Compute a fast irreversible hash.

    Args:
        text: input string
        salt: optional salt

    Returns:
        hex digest string
    """
    h = hashlib.blake2b(digest_size=20)
    h.update(to_bytes(salt))
    h.update(to_bytes(text))
    return to_hex(h.digest())
