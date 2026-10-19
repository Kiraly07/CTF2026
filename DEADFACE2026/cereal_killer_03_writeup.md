# Cereal Killer 03 — Reverse Engineering (500 pts)

The Reptilians edition of the Cereal Killer series. A tinyurl (https://tinyurl.com/2j5jvbdn) hides the CDN link to `re03-win-x64.bin` (Windows x64 PE, 145KB) — the Lytton Labs "device" the Lizard People use to communicate. Pull the flag out of it.

## Layer 1 — the password

Lizard-overlord ASCII banner, then a password prompt. The hash looks like SHA1 at first glance (constants 67452301/efcdab89/... on the stack) — that's a decoy; those are actually the **MD5 IV**, and the routine is a hand-rolled standard MD5 (K table and rotation table in .rdata give it away). The digest is compared against `0d107d09f5bbe40cade3de5c71e9e9b7`:

```
john --format=raw-md5 --wordlist=rockyou.txt
→ letmein
```

## Layer 2 — the anti-run trap (the fun part)

Typing the right password gets you "Access denied.... we are unworthy..." — even though you're correct. Why:

- main registers a Vectored Exception Handler and spawns a thread that **suspends main and installs a hardware execution breakpoint** via `SetThreadContext` (Dr0 = 0x140001ad0 — the success routine — Dr7 = 1).
- When main calls the success routine, the breakpoint fires; the VEH sees RIP == 0x140001ad0, sets a global to **0xd1cefa11badc0de5** ("dicefall badcode"), and redirects RIP to the denial path.

So the program never prints the flag on a correct run — but the trap leaks the magic constant you need.

## Layer 3 — decrypting the flag

The success routine derives the keying material:

- `seed = MD5("letmein").digest()[:8] as LE uint64 ^ 0xd1cefa11badc0de5`
- xorshift64 PRNG (`x^=x<<13; x^=x>>7; x^=x<<17`), low byte per step as keystream
- XOR against the 55-byte encrypted blob at 0x1400185a0

The plaintext is MD5-verified in-binary (5d02e679a7bfae73...) before printing — replicate it offline:

```python
seed = int.from_bytes(hashlib.md5(b"letmein").digest()[:8], "little") ^ 0xd1cefa11badc0de5
x = seed
out = bytearray()
for _ in range(55):
    x ^= (x << 13) & 0xFFFFFFFFFFFFFFFF
    x ^= x >> 7
    x ^= (x << 17) & 0xFFFFFFFFFFFFFFFF
    out.append(x & 0xff)
flag = bytes(a ^ b for a, b in zip(blob, out))
```

MD5 matches the embedded check, and out comes the flag.

## Flag

```
deadface{Liz4rds_L0ve_Krampuffs_for_some_odd_reason...}
```
