"""
ZenCode - compact urlsafe base64 wrapper
Useful for safe transfer of short tokens and small messages.
"""
from .utils import to_bytes, to_text, b64_encode, b64_decode

def zen_encode(text: str) -> str:
    """
    Encode text to a compact URL-safe string.
    """
    return b64_encode(to_bytes(text))

def zen_decode(token: str) -> str:
    """
    Decode a token previously encoded with zen_encode.
    """
    return to_text(b64_decode(token))
