# punctuation — Crypto Writeup

**Event:** THEMCTF 2026
**Category:** Crypto
**Flag:** `THEMCTF{punctu4t10n_turn5_1nt0_p0lyn0m14l5}`

## Challenge

We're given a single source file and its output.

`chall.py`:

```python
#!/usr/bin/env python3
from secret import FLAG, p, q

def bytes_to_long(data: bytes) -> int:
    return int.from_bytes(data, "big")

assert FLAG.startswith(b"THEMCTF{") and FLAG.endswith(b"}")
assert p != q

n = p * q
e = 3

m_question = bytes_to_long(b"THEM?" + FLAG + b"!")
m_bang     = bytes_to_long(b"THEM!" + FLAG + b"?")

print(f"n = {n}")
print(f"e = {e}")
print(f"c_question = {pow(m_question, e, n)}")
print(f"c_bang = {pow(m_bang, e, n)}")
print(f"flag_len = {len(FLAG)}")
```

`output.txt` gives `n`, `e = 3`, the two ciphertexts, and `flag_len = 43`.

## Observations

The same secret (`FLAG`) is encrypted twice, under the **same modulus** `n` and the **same small exponent** `e = 3`. The only difference between the two plaintexts is the surrounding punctuation:

- `m_question = "THEM?" + FLAG + "!"`
- `m_bang     = "THEM!" + FLAG + "?"`

Both messages have length `5 + 43 + 1 = 49` bytes. They differ in exactly two byte positions:

- **Index 4** (the 5th byte): `?` (`0x3f`) vs `!` (`0x21`)
- **Last byte (index 48):** `!` (`0x21`) vs `?` (`0x3f`)

Because those two positions are fixed and known, the difference between the two messages is a **known constant**, independent of the flag:

```
delta = m_question - m_bang
      = (0x3f - 0x21) * 256^44 + (0x21 - 0x3f) * 256^0
      = 30 * 256^44 - 30
      = 30 * (256^44 - 1)
```

(Position index 4 from the left in a 49-byte big-endian integer sits at byte power `49 - 1 - 4 = 44`; the last byte sits at power `0`.)

Two messages with a **known linear relationship**, encrypted under a small exponent with the same modulus, is the textbook setup for the **Franklin–Reiter related-message attack**.

## Franklin–Reiter attack

Let `m = m_bang`. Then `m_question = m + delta`. We know:

```
c_bang     = m^3            mod n
c_question = (m + delta)^3  mod n
```

Define two polynomials over the ring `Z_n[x]`:

```
g1(x) = x^3 - c_bang              # has root x = m
g2(x) = (x + delta)^3 - c_question  # also has root x = m
```

Both polynomials share the root `x = m`, so `(x - m)` divides both. Computing the **polynomial GCD** of `g1` and `g2` over `Z_n` yields a linear polynomial `a1·x + a0`, from which:

```
m = -a0 / a1  (mod n)
```

This works as long as `(x - m)` is the only common factor (true with overwhelming probability here), and the GCD never needs an inverse of a non-invertible element. If it ever did, that would instead factor `n` — still a win.

Once we recover `m = m_bang`, we convert it back to bytes, strip the `THEM!` prefix and `?` suffix, and read the flag.

## Solver

```python
#!/usr/bin/env python3
n = ...   # from output.txt
e = 3
c_question = ...
c_bang = ...
flag_len = 43

# total message length = 5 (prefix) + 43 (flag) + 1 (suffix) = 49 bytes
# delta = m_question - m_bang, a known constant
delta = 30 * (256**44 - 1)

# --- minimal polynomial arithmetic over Z_n ---
def trim(p):
    while len(p) > 1 and p[-1] % n == 0:
        p.pop()
    return p

def poly_mod_reduce(a, b):
    a = a[:]
    inv_lead = pow(b[-1], -1, n)
    while len(a) >= len(b):
        coef = (a[-1] * inv_lead) % n
        shift = len(a) - len(b)
        for i in range(len(b)):
            a[i+shift] = (a[i+shift] - coef*b[i]) % n
        trim(a)
        if len(a) < len(b):
            break
    return trim(a)

def poly_gcd(a, b):
    a, b = trim(a[:]), trim(b[:])
    while not (len(b) == 1 and b[0] == 0):
        a, b = b, poly_mod_reduce(a, b)
    return a

# g1 = x^3 - c_bang
g1 = [(-c_bang) % n, 0, 0, 1]
# g2 = (x + delta)^3 - c_question
d = delta % n
g2 = [(pow(d, 3, n) - c_question) % n, (3*d*d) % n, (3*d) % n, 1]

g = poly_gcd(g1, g2)            # linear: [a0, a1]
a0, a1 = g[0], g[1]
m = (-a0 * pow(a1, -1, n)) % n  # = m_bang

msg = m.to_bytes((m.bit_length()+7)//8, "big")
assert msg.startswith(b"THEM!") and msg.endswith(b"?")
print("FLAG:", msg[5:-1].decode())
```

Running it:

```
gcd degree: 1
recovered (m_bang): b'THEM!THEMCTF{punctu4t10n_turn5_1nt0_p0lyn0m14l5}?'
FLAG: THEMCTF{punctu4t10n_turn5_1nt0_p0lyn0m14l5}
```

## Flag

```
THEMCTF{punctu4t10n_turn5_1nt0_p0lyn0m14l5}
```

## Takeaways

- Encrypting two messages with a **known difference** under the same RSA modulus and a **low public exponent** breaks the scheme via Franklin–Reiter, regardless of how strong `n` is.
- The flavor of this challenge: the only "difference" between the two encryptions is punctuation — and that tiny known delta is exactly what turns recovery into a polynomial GCD. As the flag says, *punctuation turns into polynomials*.
- No factoring of `n` is needed; the attack works purely in `Z_n[x]`.
