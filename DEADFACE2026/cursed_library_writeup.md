# Cursed Library — PWN (235 pts)

Remote: 159.65.228.107:5004. The zip is 537MB of noise: the real ELF is only ~33KB
(the rest is a giant random blob appended after the section headers — ignore it).
PIE + glibc 2.42 (libc/ld shipped in the zip, patchelf to run locally).

## How I solved it

Menu binary: 1) peruse (lists cwd), 2) checkout, 3) leave.

`checkout()` does `gets()` into a 96-byte stack buffer at `rbp-0x60` — no canary,
so 96 bytes to saved rbp, 104 to RIP. Three relevant behaviors:

- Input `BookOfTheDead` calls `BookOfTheDead()` (0x1ba1) which printf's `%p` of
  itself → **PIE leak** (base + 0x1ba1).
- Input `Necronomicon.txt` is forbidden (strcmp + `..` check) — that's the flag
  file on the server, so you can't just cat it through the app.
- `Necronomicon()` (0x1b6a) is never called by normal flow; it printf's
  `puts(): %p` → **libc leak**. Reach it by ROP.

Exploit (single connection, exploit.py in work/cursedlib/):

1. Option 2 + `BookOfTheDead` → PIE base.
2. Option 2 + overflow: `A`*96 + fake rbp + ret(0x1016) + Necronomicon + ret(0x1016)
   + main(0x1229). The ret gadgets keep rsp 16-byte aligned so main's puts/printf
   don't SIGSEGV on movaps. Necronomicon leaks libc puts (0x82060 in the shipped libc).
3. main re-runs (reprints the whole banner art, fine), option 2 again:
   `A`*96 + fake rbp + libc ret + pop rdi (libc 0x2a9b7) + /bin/sh (0x1aaea4)
   + system (0x54790) → shell.

Then `cat Necronomicon.txt`. Avoid 0x0a bytes in the chain (gets newline) —
retry the connection if the random base gives you one.

## Flag

```
deadface{T#3_L1br4ry_Kn0w5_A11}
```
