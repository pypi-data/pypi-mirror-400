"""
Hey there! Welcome to Cryzen. 

I built this library to make cryptography and hashing simple and accessible 
for everyone, especially for those working in mobile-first environments. 
Whether you're looking to secure a user's password or just want to hide 
some data quickly, Cryzen has a tool for you.

Here’s a quick guide on how to use what's inside:

-------------------------------------------------------------------------------
 1. ENCRYPTION & DECRYPTION (When you need to get the data back)
-------------------------------------------------------------------------------

● AstraCrypt: This is the heavyweight champion here. It uses AES-256-CBC 
  to keep your data super secure. (Requires 'pycryptodome')
  
  Example:
    >>> from cryzen import astra_encrypt, astra_decrypt
    >>> my_token = astra_encrypt("Hey Mahadi!", "your-secret-key")
    >>> print(astra_decrypt(my_token, "your-secret-key"))

● FluxCipher: Fast and simple XOR cipher for quick data masking.
  
● ZenCode: URL-safe Base64 wrapper for tokens.

-------------------------------------------------------------------------------
 2. SECURE HASHING (One-way only, no going back!)
-------------------------------------------------------------------------------

● OmegaHash: PBKDF2-HMAC-SHA512 for passwords (200,000 rounds).
● TerraHash: Standard SHA-256 for integrity checks.
● NovaHash: Fast BLAKE2b hashing for performance.

Author: Mahadi
License: MIT
Find me on GitHub: https://github.com/mahadi99900/cryzen

Happy Coding! 💻
"""

from .astracrypt import astra_encrypt, astra_decrypt
from .flux import flux_encrypt, flux_decrypt
from .nova import nova_hash
from .omega import omega_hash
from .terra import terra_hash
from .zencode import zen_encode as zencode_encrypt, zen_decode as zencode_decrypt

__all__ = [
    'astra_encrypt', 'astra_decrypt',
    'flux_encrypt', 'flux_decrypt',
    'nova_hash', 'omega_hash',
    'terra_hash',
    'zencode_encrypt', 'zencode_decrypt'
]

def hello():
    print("Cryzen v0.1.3 is ready and loaded!")
