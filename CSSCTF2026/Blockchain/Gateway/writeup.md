---
title: "Gateway"
ctf: "CSSCTF"
date: 2026-10-01
category: misc
flag_format: "CSSCTF{CSS{...}}"
---

The challenge normally expects a contract to pass three doors: call `enter()` through a contract (`tx.origin != msg.sender`), send ether to set `funded`, then call `claim()` with `keccak256(abi.encodePacked("gateway to the flag"))`. The password is in storage slot 1, readable with `eth_getStorageAt`.

That on-chain route was unavailable remotely. The launcher at `34.116.80.78:31337` crashes on options 1 and 2 because the `/new` backend returns an empty body and `launcher.py` fails at `requests.post(...).json()`. Option 3 bypasses the backend. Enter the case-sensitive team ticket `CSS` to get the flag:

```python
from pwn import remote

r = remote("34.116.80.78", 31337)
r.recvuntil(b"action? ")
r.sendline(b"3")
r.recvuntil(b"ticket please: ")
r.sendline(b"CSS")
print(r.recvline().decode().strip())
r.close()
```

Flag:

```text
CSSCTF{CSS{B451C_BL0CKCH41N_5K1LL5}}
```
