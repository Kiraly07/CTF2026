# Cascading Chain — Crypto Writeup

**Event:** THEM 2026
**Category:** Crypto
**Flag:** `THEM?!CTF{x0r_x0r_x0r_cha1n1ng_g0es_brrrr}`

---

## Challenge

We are handed four hex blobs of equal length (42 bytes each):

```
c1 = 36273f225d4e393b2414025f1030025f1030025f10301907035e145e0c082508520a0930001d081d1012
c2 = 0e021b000e021b000e021b000e021b000e021b000e021b000e021b000e021b000e021b000e021b000e02
c3 = 180504021805040218050402180504021805040218050402180504021805040218050402180504021805
c4 = 202020204b49263932131d5d06371d5d06371d5d0637060515590b5c1a0f3a0a440d1632161a171f0615
```

The name "Cascading Chain" is the whole hint: the ciphertexts are links in an
XOR chain, where each link mixes in the next repeating key.

## Observations

Two things jump out immediately:

1. **c2 and c3 are perfectly periodic with period 4.** They are just a 4-byte
   pattern repeated 10.5 times. A purely periodic ciphertext carries no message
   — it is a key XORed against another key.

   ```
   c2 period = 0e021b00
   c3 period = 18050402
   ```

2. **c1 and c4 are NOT periodic.** They carry the actual plaintext (the flag).

3. **The whole chain XORs to zero:**

   ```python
   c1 ^ c2 ^ c3 ^ c4 == b"\x00" * 42   # True
   ```

That last property is the structural giveaway. If a set of values XORs to zero,
they telescope — each term's contribution is cancelled by another.

## Recovering the key

We know every THEM flag starts with `THEM?!CTF{`. XOR that crib against the
start of `c1`:

```python
key_prefix = xor(c1[:10], b"THEM?!CTF{")
# -> b"bozobozobo"
```

The result is the word **`bozo`** repeating with period 4. So:

```
c1 = flag ⊕ "bozo"
```

Decrypting `c1` with the repeating key `bozo` gives the flag directly:

```python
flag = repeating_xor(c1, b"bozo")
# THEM?!CTF{x0r_x0r_x0r_cha1n1ng_g0es_brrrr}
```

That alone solves the challenge — but here is *why* the cascade works.

## The cascade explained

Recovering the other links reveals three keys, each a cheeky 4-letter word:

```
k1 = "bozo"
k2 = "lmao"
k3 = "them"
```

And the four ciphertexts are:

```
c1 = P  ⊕ k1        (plaintext masked by bozo)
c2 = k1 ⊕ k2        ("bozo" ⊕ "lmao")
c3 = k2 ⊕ k3        ("lmao" ⊕ "them")
c4 = P  ⊕ k3        (plaintext masked by them)
```

Verification:

```python
xor(b"bozo", b"lmao") == c2[:4]      # True
xor(b"lmao", b"them") == c3[:4]      # True
repeating_xor(c4, b"bozo")           # reveals the BOZO-flavoured link
repeating_xor(xor(c1, c4), b"bozo")  # -> "themthemthem..."  (= k1 ⊕ k3)
```

Now the telescoping is obvious. XOR the whole chain:

```
c1 ⊕ c2 ⊕ c3 ⊕ c4
  = (P ⊕ k1) ⊕ (k1 ⊕ k2) ⊕ (k2 ⊕ k3) ⊕ (P ⊕ k3)
  =  P ⊕ P ⊕ k1 ⊕ k1 ⊕ k2 ⊕ k2 ⊕ k3 ⊕ k3
  =  0
```

Every term appears exactly twice, so the entire chain cancels to zero. That is
the "cascading chain" — adjacent links share a key, and the two endpoints share
the plaintext, so it collapses completely.

## Solution

```python
#!/usr/bin/env python3
from itertools import cycle

c1 = bytes.fromhex("36273f225d4e393b2414025f1030025f1030025f10301907035e145e0c082508520a0930001d081d1012")
c2 = bytes.fromhex("0e021b000e021b000e021b000e021b000e021b000e021b000e021b000e021b000e021b000e021b000e02")
c3 = bytes.fromhex("180504021805040218050402180504021805040218050402180504021805040218050402180504021805")
c4 = bytes.fromhex("202020204b49263932131d5d06371d5d06371d5d0637060515590b5c1a0f3a0a440d1632161a171f0615")

known_prefix = b"THEM?!CTF{"

def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def repeating_xor(data, key):
    return bytes(x ^ y for x, y in zip(data, cycle(key)))

# The loop cancels under XOR: c1 ^ c2 ^ c3 ^ c4 == 0.
assert xor(xor(xor(c1, c2), c3), c4) == b"\x00" * len(c1)

# Recover the repeating key from the known flag prefix.
key = xor(c1[:len(known_prefix)], known_prefix)[:4]   # b"bozo"

flag = repeating_xor(c1, key)
print(f"key = {key.decode()}")
print(flag.decode())
```

Output:

```
key = bozo
THEM?!CTF{x0r_x0r_x0r_cha1n1ng_g0es_brrrr}
```

## Takeaways

- A ciphertext that is **perfectly periodic** carries no message — it is one key
  masking another (`k_i ⊕ k_{i+1}`).
- When a set of XOR values **sums to zero**, look for a telescoping structure:
  shared keys between adjacent terms cancel out.
- A **known plaintext prefix** (here the flag header `THEM?!CTF{`) instantly
  recovers a short repeating XOR key — no brute force needed.

**Flag:** `THEM?!CTF{x0r_x0r_x0r_cha1n1ng_g0es_brrrr}`
