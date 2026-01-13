"""
TerraHash - standard strong hashing (sha256)
"""
import hashlib
from .utils import to_hex, to_bytes

def terra_hash(text: str, salt: str = "") -> str:
    """
    SHA-256 based irreversible hash.

    Args:
        text: input string
        salt: optional salt

    Returns:
        hex digest
    """
    h = hashlib.sha256()
    h.update(to_bytes(salt))
    h.update(to_bytes(text))
    return to_hex(h.digest())
