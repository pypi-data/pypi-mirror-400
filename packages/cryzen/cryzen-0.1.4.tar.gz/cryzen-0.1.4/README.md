# cryzen

`cryzen` is a small, focused Python library providing 3 reversible ciphers and 3 irreversible hashing schemes,
designed to be simple to use and suitable for many common tasks.

**Important:** This library intentionally exposes friendly, unique function names (FluxCipher, ZenCode, AstraCrypt, NovaHash, TerraHash, OmegaHash).
Internally standard primitives are used (AES, BLAKE2, SHA256, PBKDF2).

## Features

- FluxCipher (flux_encrypt / flux_decrypt) — XOR-based reversible cipher (fast, NOT recommended for strong secrets)
- ZenCode (zen_encode / zen_decode) — URL-safe compact base64 wrapper for tokens
- AstraCrypt (astra_encrypt / astra_decrypt) — AES-256-CBC reversible encryption (requires `pycryptodome`)
- NovaHash (nova_hash) — fast irreversible BLAKE2b-based hash
- TerraHash (terra_hash) — SHA-256 irreversible hash
- OmegaHash (omega_hash) — PBKDF2-HMAC-SHA512 (salted) irreversible hash for passwords

## Installation (development)

```bash
# For AES support install pycryptodome
pip install pycryptodome

# then install locally for testing
pip install cryzen
```

## Quick usage

```python
from cryzen import flux_encrypt, flux_decrypt, zen_encode, zen_decode
from cryzen import astra_encrypt, astra_decrypt
from cryzen import nova_hash, terra_hash, omega_hash

# flux
ct = flux_encrypt("hello world", key="s3cr3t")
print(flux_decrypt(ct, key="s3cr3t"))

# zencode
t = zen_encode("keep this")
print(zen_decode(t))

# astra (AES) - requires pycryptodome
token = astra_encrypt("sensitive", "my_secret_key")
print(astra_decrypt(token, "my_secret_key"))

# hashes
print(nova_hash("value"))
print(terra_hash("value", salt="optional"))
print(omega_hash("password"))  # returns salt$derived_hex
```

## API & help()

Each function includes a docstring. Use Python's built-in `help()` or `dir()`:

```py
import cryzen
help(cryzen.flux_encrypt)
dir(cryzen)
```

## Security notes

- `flux_encrypt` is **not** cryptographically secure — use only for obfuscation or non-critical tasks.
- `astra_encrypt` is secure when secret_key is strong and kept private. Use `pycryptodome` for AES implementation.
- Use `omega_hash` for password storage (store full token).
- Never hardcode secrets in distributed code.
- **Source Code on GitHub:** [Osman_Hadi Repository](https://github.com/mahadi99900/Osman_Hadi)

### (Contact Me):
- **WhatsApp & Telegram:** [+8801701902728](https://wa.me/8801701902728)
- **Email:** [islammdmahadi943@gmail.com](mailto:islammdmahadi943@gmail.com)

## License

MIT. See LICENSE file.
