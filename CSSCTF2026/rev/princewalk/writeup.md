---
title: "PRINCE WALK"
ctf: "CSSCTF"
date: 2026-09-30
category: reverse
flag_format: "CSSCTF{...}"
---

The game only unlocks the mission text at `(999999, 999999)`. The binary's target check uses `0xf423f` for both coordinates. Rather than walk there or edit the Int32 values with PINCE, I reversed the destination decryptor VM and ran it offline.

`fcn.00002c52` seeds 16 registers and a rolling seed from `(x, y)` with `rol32` and avalanche constants `0x7feb352d` / `0x846ca68b`, then executes `0x2080` scrambled 8-byte instructions at `.rodata@0x4a80`. Opcode `0x83` stores output bytes; after 128 stores, the program checks the length and FNV-1a before copying out the message.

```bash
python3 solve.py prince_walk
```

The solver emulates opcodes `0x8b/0x48/0x31/0x71/0xb3/0x12/0xff/0x83` and prints the recovered mission text.

## Flag

```text
CSSCTF{P12INC3_0R_P1NC3?}
```
