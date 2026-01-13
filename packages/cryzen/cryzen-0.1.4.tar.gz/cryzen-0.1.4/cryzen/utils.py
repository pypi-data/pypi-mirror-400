"""
Utility helper functions used internally by cryzen modules.
"""
from typing import Union
import base64
import binascii

def to_bytes(data: Union[str, bytes], encoding: str = "utf-8") -> bytes:
    if isinstance(data, bytes):
        return data
    return data.encode(encoding)

def to_text(data: Union[str, bytes], encoding: str = "utf-8") -> str:
    if isinstance(data, str):
        return data
    return data.decode(encoding)

def b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")

def b64_decode(data: str) -> bytes:
    # Add padding if required
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)

def to_hex(data: bytes) -> str:
    return binascii.hexlify(data).decode("ascii")

def from_hex(text: str) -> bytes:
    return binascii.unhexlify(text)
