---
title: "The Astrolabe Overwrite"
ctf: "CSSCTF"
date: 2026-10-01
category: misc
flag_format: "CSSCTF{...}"
---

## Solve

`nexus_core` is a four-register VM whose opcode table changes after every instruction. After printing a beacon, it accepts up to 512 hex characters of bytecode. I worked backward from the halt checks over `p = 65521`; the four field values that satisfy the recurrence and projective checks are uniquely `(1, 218, 59611, 783)`, independent of the beacon.

The VM starts with rolling key `0x5a` and opcode table `[0x10, 0x20, 0x30, 0x35, 0x40, 0x50, 0x7f, 0xff]`. For each instruction, it decodes `table[(b0 ^ key) & 7]`, updates the key to `(key * 31 + reg0_low) & 0xff`, then swaps table entries indexed by `reg0 & 7` and `reg1 & 7`. The unique solution must be loaded as `(u_i + beacon) mod 65521`. Four immediate loads cost 4 cycles; 36 relative jumps with offset 0 cost 108; halt costs 10. The total, 122, falls in the accepted 112–128 window.

`misc/TheAstrolobeOverwrite/solve.py` reads the live beacon, assembles the bytecode while tracking the key and table swaps, sends it to the service, and prints the returned flag. Run it with Python; optionally pass a host and port as arguments. The assembler uses only load, zero-offset jump, and halt instructions.

## Flag

`CSSCTF{0ur0b0r0s_g00d_j0b_b01s_heh3_67}`
