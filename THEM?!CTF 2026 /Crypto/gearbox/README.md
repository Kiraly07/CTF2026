# THEMCTF 2026 — Gearbox (crypto)

**Flag:** `THEMCTF{th3_5l0w_g34r5_kn0w_th3_53cr3t}`

## TL;DR

A bounded discrete-log problem: recover `x` in a known interval `[lower, upper]`
such that `g^x mod p == y`, then use `x` to derive a SHAKE-256 keystream and
decrypt the flag. The interval has size exactly `2^53`, far too small for the
hardness of the 4096-bit prime to matter. **Pollard's kangaroo (lambda) algorithm**
solves a bounded DLP in `O(sqrt(N))` group operations (~`2 * 2^26.5 ~= 1.9e8` ops),
which is a few minutes of single-threaded C+GMP.

## Files

- `chall.py` — challenge logic (keystream + tag + decrypt; the `main()` just
  prints stats, the crypto primitives are the interesting part).
- `output.txt` — public instance: `p, g, lower, upper, y, nonce, ciphertext, tag`.

## The scheme

```python
DOMAIN = b"THEMCTF gearbox v1"

def keystream(exponent, nonce, length):
    material = DOMAIN + b"\0stream\0" + int_to_bytes(exponent) + nonce
    return hashlib.shake_256(material).digest(length)

def tag(exponent, nonce, plaintext):
    material = DOMAIN + b"\0tag\0" + int_to_bytes(exponent) + nonce + plaintext
    return hashlib.sha256(material).digest()[:16]

def decrypt(exponent, nonce, ciphertext, expected_tag):
    stream = keystream(exponent, nonce, len(ciphertext))
    plaintext = bytes(a ^ b for a, b in zip(ciphertext, stream))
    if tag(exponent, nonce, plaintext) != expected_tag:
        raise ValueError("bad discrete log")
    return plaintext
```

The whole key is the secret **exponent** `x`:

- keystream = `SHAKE256(DOMAIN || "\0stream\0" || x || nonce)` XORed over the ciphertext,
- a SHA-256 tag binds `x`, `nonce`, and the plaintext (acts as a correctness check),
- the only public link to `x` is `y = g^x mod p`.

So the entire challenge reduces to: **solve the discrete log `x` from `y`.**

## Why it's solvable

`p` is a 4096-bit prime and `g = 5`, so a generic DLP would be hopeless.
But the challenge hands us a tight search interval:

```
N = upper - lower + 1 = 9007199254740992 = 2^53
```

A discrete log known to live in an interval of width `N` is a *bounded* DLP.
Pollard's kangaroo algorithm solves it in `~2*sqrt(N) ~= 1.9e8` group
multiplications regardless of how big `p` is. That is trivially feasible.

The recovered exponent sits at:

```
x          = 23090212326807100415368332154642657776039126990759936506647603928177622930604387499850196060509753389356269877319643
x - lower  = 1061372570683010   (~2^50 into the interval)
```

## Pollard's kangaroo (the solver)

Implemented in C with GMP for speed (`solve_kangaroo.c`, compiled as
`solve_kangaroo_mix`). The classic tame/wild design:

1. **Pseudo-random walk.** `R = 64` jump sizes are derived from a fixed
   `splitmix64` seed; `jumps[i] = g^stepsz[i] mod p`. A hash of the current
   group element selects which jump to take, so two walks that ever land on the
   same element stay together forever.

2. **Tame kangaroo.** Start at `g^upper` (the right end of the interval) and walk
   forward `~N + slack` total distance, recording **distinguished points**
   (elements whose hash has the low `DP_BITS = 16` bits zero) into a hash table,
   keyed by the element hash with the accumulated distance stored.

3. **Wild kangaroo.** Start at `y = g^x` and walk with the same jump rule.
   Whenever it hits a distinguished point already in the table, the two walks
   have collided. Then:

   ```
   x = upper + tame_dist - wild_dist
   ```

   Verify with `g^x mod p == y` and that `x` is in `[lower, upper]`.

Key parameters in the source:

```c
#define R 64           // number of jump types
#define DP_BITS 16     // 1/65536 of points are distinguished
#define TABLE_CAP (1u << 22)
// mean jump ~ 2^27, near-optimal for an interval of 2^53
```

Mean jump size `~2^27` is tuned near `sqrt(N)`, giving the textbook optimum:
the tame walk covers the interval in `~sqrt(N)` steps, and the wild walk meets
the trail after a comparable number of steps. Total runtime here was ~16 minutes
single-threaded on a 4-core box (the run is fully deterministic — fixed seed —
so it reproduces the same `x` every time).

## End-to-end solve

```
# 1) recover x (bounded DLP via kangaroo)
./solve_kangaroo_mix        # prints x to stdout after ~16 min

# 2) derive keystream from x and decrypt + verify tag
python3 decrypt_flag.py "$(cat x_result.txt)"
```

`decrypt_flag.py`:

```python
from chall import load_output, decrypt
from pathlib import Path
import sys

x = int(sys.argv[1])
v = load_output(Path("output.txt"))
p, g, y = int(v["p"]), int(v["g"]), int(v["y"])
lower, upper = int(v["lower"]), int(v["upper"])

assert lower <= x <= upper
assert pow(g, x, p) == y                       # discrete log correct
pt = decrypt(x, v["nonce"], v["ciphertext"], v["tag"])  # raises on bad tag
print("FLAG:", pt.decode())
```

Output:

```
[+] x verified: g^x == y, x in interval
[+] tag verified
FLAG: THEMCTF{th3_5l0w_g34r5_kn0w_th3_53cr3t}
```

## Takeaways

- The size of the modulus is a red herring. **A discrete log restricted to a small
  interval is easy**, no matter how large `p` is — `O(sqrt(interval))`, not
  `O(sqrt(p))`.
- `2^53` is the sweet spot the author chose: large enough that naive brute force
  (`2^53` steps) is out of reach, small enough that kangaroo (`~2^27` steps) is
  minutes of work.
- The SHAKE/SHA-256 keystream-and-tag construction is sound; it isn't the weak
  point. The only attackable surface is the bounded exponent. Once `x` is known,
  decryption is mechanical and the SHA-256 tag confirms the answer.
- The flag — "the slow gears know the secret" — is a nod to the slow, patient
  hops of the kangaroo walk grinding through the interval.
