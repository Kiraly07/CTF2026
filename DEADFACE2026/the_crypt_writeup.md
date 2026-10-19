# The Crypt — PWN (100 pts)

Remote: 159.65.228.107:5001. Simple binary, classic bugs.

## How I solved it

Reversing `main`: it compares your input against a 24-byte blob at `0x405080` XOR'd with `0x13`. Undo the XOR and you get the password:

```
Open_The_Door_To_Nowhere
```

After the password matches, `whispering_madness()` calls `gets()` into a 0x40-byte stack buffer. There's a win function, `nowhere()` at `0x401660`, that just opens and cats the flag file. No PIE, no canary — so it's a plain ret2win:

```python
payload = b"Open_The_Door_To_Nowhere\n" + b"A"*72 + p64(0x401660)
```

(72 = 0x40 buffer + saved rbp.) Send that as the overflow line and the binary prints the flag.

## Flag

```
deadface{d3crypt3d_1nt0_n0th1ng}
```
