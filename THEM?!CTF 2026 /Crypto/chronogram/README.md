# Chronogram — Crypto Writeup

**Event:** THEM 2026
**Category:** Crypto
**Flag:** `THEMCTF{th3_g34r5_k33p_gr1nd1ng}`

## TL;DR

A local RSA time-lock puzzle (RSW / "time-lock crypto"). The secret key is
`y = seed^(2^rounds) mod n`, computed by performing `rounds` sequential modular
squarings. Because the factorization of `n` is not given, there is no shortcut:
you just have to grind through all 240,000,000 squarings. After ~37 minutes the
key pops out, derives the keystream + tag, and decrypts the flag.

## Files

- `chall.py` — reference implementation (loader, timelock, keystream, tag, decrypt).
- `output.txt` — the public parameters: `n`, `seed`, `rounds`, `nonce`, `ciphertext`, `tag`.
- `solve.py` — the grind script (this writeup's solution).
- `solve.log` — full progress log ending with the recovered key + flag.

## The Parameters

```
n          4096-bit modulus (factorization NOT provided)
seed       4096-bit base value
rounds     240,000,000
nonce      afd7af1062a504206b54a6d3ba531046              (16 bytes)
ciphertext 758cdf4935f7cb7d5ea928f1f652aa77386234a6b4ab70c694ad6895366ac413  (32 bytes)
tag        12ed56d7d7f0b0c04f11f89b1760e710              (16 bytes)
```

## How the Scheme Works

The whole thing lives in `chall.py`. Key pieces:

```python
DOMAIN = b"THEMCTF chronogram v1"

def timelock(seed, modulus, rounds):
    state = seed % modulus
    for _ in range(rounds):
        state = state * state % modulus   # one sequential squaring
    return state

def keystream(secret, modulus, nonce, length):
    material = DOMAIN + b"\0stream\0" + int_to_fixed_bytes(secret, modulus) + nonce
    return hashlib.shake_256(material).digest(length)

def tag(secret, modulus, nonce, plaintext):
    material = DOMAIN + b"\0tag\0" + int_to_fixed_bytes(secret, modulus) + nonce + plaintext
    return hashlib.sha256(material).digest()[:16]
```

The recovered secret `y` is fed (as a fixed 512-byte big-endian blob) into a
SHAKE-256 keystream that XORs the ciphertext, and a truncated SHA-256 tag that
authenticates the plaintext. So the entire problem reduces to **computing `y`**.

## Why There's No Shortcut

This is the classic Rivest–Shamir–Wagner time-lock puzzle.

If you knew the factorization `n = p·q`, you could collapse the 240M squarings
into a single modular exponentiation:

```
e = 2^rounds mod φ(n)        # one exp in the exponent group
y = seed^e mod n             # one exp -> done instantly
```

But `n` is a generic 4096-bit modulus with **no factors given**. Without `φ(n)`
you cannot reduce the exponent `2^rounds`, and repeated squaring is conjectured
to be inherently sequential — you cannot parallelize it. So the only path is to
actually perform all 240,000,000 squarings one after another. That sequential
wall is the entire "puzzle": it costs real wall-clock time and nothing more.

## The Solve

Just run the squaring loop. The only practical note is to use a fast bignum
library — `gmpy2` (libgmp) is dramatically faster than Python's native `int` for
4096-bit modular multiplication.

```python
#!/usr/bin/env python3
import ast, hashlib, time
from pathlib import Path
import gmpy2

DOMAIN = b"THEMCTF chronogram v1"

def int_to_fixed_bytes(value, modulus):
    return int(value).to_bytes((int(modulus).bit_length() + 7) // 8, 'big')

def keystream(secret, modulus, nonce, length):
    material = DOMAIN + b"\0stream\0" + int_to_fixed_bytes(secret, modulus) + nonce
    return hashlib.shake_256(material).digest(length)

def tag(secret, modulus, nonce, plaintext):
    material = DOMAIN + b"\0tag\0" + int_to_fixed_bytes(secret, modulus) + nonce + plaintext
    return hashlib.sha256(material).digest()[:16]

# load params from output.txt ...
n = gmpy2.mpz(v['n'])
y = gmpy2.mpz(v['seed']) % n
rounds = int(v['rounds'])

for i in range(rounds):
    y = (y * y) % n          # the one and only operation that matters

ct = v['ciphertext']
stream = keystream(y, n, v['nonce'], len(ct))
pt = bytes(a ^ b for a, b in zip(ct, stream))
assert tag(y, n, v['nonce'], pt) == v['tag']
print(pt.decode())
```

Full runnable version is in `solve.py`.

## Result

The grind completed in **~2216 seconds (~37 minutes)** at roughly **108,000
squarings/second** on this box (see `solve.log`):

```
240000000/240000000 100.00% elapsed=2216.7s eta=0.0s
y = 5398453968107657785524171010924656177933959215046617335...
plaintext = b'THEMCTF{th3_g34r5_k33p_gr1nd1ng}'
tag ok = True
```

The tag check passes, confirming the recovered `y` is correct.

## Flag

```
THEMCTF{th3_g34r5_k33p_gr1nd1ng}
```

The flag itself is a wink at the mechanic: there is no clever break, you just let
the gears keep grinding through a quarter-billion squarings.
