# Velvet Rope — THEMCTF 2026

**Category:** Crypto  
**Flag:** `THEMCTF{th3_b0unc3r_0nly_ch3ck5_th3_dr355_c0d3}`

---

## Overview

The challenge provides a remote oracle service that performs RSA decryption but only reveals whether the result is **PKCS#1 v1.5 conforming** — it never gives the plaintext. This is the textbook precondition for **Bleichenbacher's adaptive chosen-ciphertext attack** (1998).

### Public Parameters

| Parameter | Value |
|-----------|-------|
| n | 1024-bit modulus |
| e | 65537 |
| k | 128 bytes (block size) |
| c | target ciphertext |

The oracle accepts hex-encoded ciphertexts and responds with `valid` or `invalid`, indicating whether `pow(c, d, n)` decodes to a block matching the PKCS#1 v1.5 format:

```
00 02 <at least 8 non-zero random bytes> 00 <message>
```

Maximum queries: 1,500,000 per session.

---

## Vulnerability

The `pkcs1_v15_conforming()` check is a classic **padding oracle**. Each query leaks 1 bit of information about the plaintext, and the structure of the PKCS#1 v1.5 format allows adaptive refinement of candidate plaintext intervals through repeated chosen-ciphertext queries.

This is **CVE-2012-5081** territory — the same class of attack that broke real-world RSA implementations (Bleichenbacher '98).

---

## Attack Strategy: Bleichenbacher's Adaptive Chosen-Ciphertext Attack

### Step 0: Setup

- `B = 2^(8*(k-2))` = `2^1008`  
- Conforming plaintexts lie in `[2B, 3B)` (i.e., the top byte is `00 02`)

### Step 1: Blinding

Check if the original ciphertext `c` is already PKCS-conforming. If not, find an `s₀` such that `c₀ = c · s₀^e mod n` decrypts to a conforming block.

In this case, `c` was already conforming → `s₀ = 1`, no blinding needed.

### Step 2: Adaptive Search

Iteratively find values `sᵢ` that produce conforming ciphertexts, narrowing the plaintext interval `M = [a, b]` each round:

- **Step 2a** (initial, `i=1`): Search `s ≥ ⌈n/(3B)⌉` linearly
- **Step 2b** (when `|M| > 1` interval): Search `s > s_prev` linearly  
- **Step 2c** (when `|M| = 1` interval): Search in the narrowed range derived from `M` and `s_prev`

### Step 3: Interval Narrowing

For each conforming `s`, compute all valid `r` values and intersect the resulting intervals. Merge overlapping intervals to produce the new `M`.

### Termination

When `|M| = 1` (single value), that value is the padded plaintext. Remove the PKCS#1 v1.5 padding to recover the flag.

---

## Optimisation: Pipelined Queries

The naive Bleichenbacher implementation sends one ciphertext per round-trip, which over a network would take millions of seconds. The solve script **pipelines** candidate queries:

1. Generate a batch of `BATCH=4000` candidate `s` values
2. Send all corresponding ciphertexts in one TCP write
3. Read all responses back in one pass
4. Return the first conforming `s` from the batch

Adaptive chunking: start with 8 candidates, grow to 4× up to 4000 per batch. This keeps wasted queries tiny in the common case (steps 2b/2c) while ramping up for the long step 2a linear scan.

---

## Recovered Flag

```
00026e17959bc60963a818d1583a1f032b754727108b3beca555eb7490806f5ee6dc45ddc61834731708088de3f60f3864f5ffa461d0cb196181eaa51c52f7d48abf3028041ecd642277a131ff201b9e005448454d4354467b7468335f6230756e6333725f306e6c795f636833636b355f7468335f64723335355f633064337d
```

Flag: `THEMCTF{th3_b0unc3r_0nly_ch3ck5_th3_dr355_c0d3}`

---

## Key Takeaways

- Any oracle that leaks PKCS#1 v1.5 padding validity is vulnerable to Bleichenbacher's attack
- The name "Velvet Rope" is a hint: the bouncer (oracle) only checks if you're "dressed properly" (PKCS conforming) — he doesn't let you in (decrypt) or tell you what's inside
- 1024-bit RSA with a padding oracle is completely broken with <25K queries

---

## Files

| File | Description |
|------|-------------|
| `chall.py` | Challenge server (oracle + TCP service) |
| `public.txt` | Public parameters (n, e, c, k) |
| `solve.py` | Bleichenbacher attack implementation |
| `solve.log` | Full solve log with 991 rounds of output |
