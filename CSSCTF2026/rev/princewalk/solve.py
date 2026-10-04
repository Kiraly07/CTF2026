#!/usr/bin/env python3
"""Recover CSSCTF flag from prince_walk without walking to (999999,999999)."""

import struct
import sys
from pathlib import Path

TARGET = 999999
PROG_VADDR = 0x4A80
PROG_ENTRIES = 0x2080
PROG_SIZE = PROG_ENTRIES * 8


def u32(x: int) -> int:
    return x & 0xFFFFFFFF


def rol32(x: int, n: int) -> int:
    n &= 31
    x = u32(x)
    return u32((x << n) | (x >> (32 - n)))


def mix(x: int) -> int:
    """fcn.00002c18 — 32-bit avalanche mixer."""
    x = u32(x)
    x ^= x >> 16
    x = u32(x * 0x7FEB352D)
    x ^= x >> 15
    x = u32(x * 0x846CA68B)
    x ^= x >> 16
    return x


def load_program(binary: Path) -> bytes:
    data = binary.read_bytes()
    # ELF: find .rodata file offset for vaddr 0x4a80
    # For this stripped PIE, .rodata starts at file offset 0x4000 / vaddr 0x4000
    # so file offset == vaddr for that region.
    if len(data) < PROG_VADDR + PROG_SIZE:
        raise SystemExit("binary too small")
    return data[PROG_VADDR : PROG_VADDR + PROG_SIZE]


def decrypt(prog: bytes, x: int = TARGET, y: int = TARGET) -> bytes:
    x = u32(x)
    y = u32(y)

    def word(idx: int) -> tuple[int, int]:
        return struct.unpack_from("<II", prog, idx * 8)

    regs = [0] * 16
    for i in range(16):
        regs[i] = mix(u32(x ^ rol32(y, i + 1)) ^ u32((i + 1) * 0x9E3779B9))

    seed = mix(u32(rol32(y, 0x13) + x) ^ 0xA4093822)
    out = bytearray(0x80)
    written = [False] * 0x80
    count = 0

    for pc in range(PROG_ENTRIES):
        t = u32(pc * 0xD9 + 0xCD6)
        q = ((t * 0xFC0FC0FD) >> 32) >> 13
        idx = u32(t - q * PROG_ENTRIES)

        w0, w1 = word(idx)
        a = mix(u32(pc * 0x9E3779B9) ^ seed) ^ w0
        b = mix(u32(seed + pc + 0x6A09E667)) ^ w1

        dest = (a >> 8) & 0xF
        s1 = regs[(a >> 12) & 0xF]
        s2 = regs[(a >> 16) & 0xF]
        imm = (a >> 20) & 0x1F
        op = a & 0xFF

        if op == 0x8B:
            regs[dest] = u32(rol32(s2, imm) + s1 + b)
        elif op == 0x48:
            regs[dest] = u32(rol32(u32(s2 + b), imm) ^ s1)
        elif op == 0x31:
            regs[dest] = u32(u32(u32(s2 + b) ^ s1) * u32(b | 1))
        elif op == 0x71:
            regs[dest] = u32(s1 - rol32(u32(s2 ^ b), imm))
        elif op == 0xB3:
            regs[dest] = u32((s1 & b) | (s2 & u32(~b)))
        elif op == 0x12:
            regs[dest] = mix(u32(s1 + s2 + b))
        elif op == 0xFF:
            regs[dest] = rol32(u32(s1 ^ b), u32(s2 ^ imm) & 0x1F)
        elif op == 0x83:
            out_idx = b >> 25
            if out_idx > 0x7F or written[out_idx]:
                raise RuntimeError(f"bad STORE at pc={pc}")
            byte = u32(s1 ^ rol32(s2, imm) ^ b) & 0xFF
            out[out_idx] = byte
            written[out_idx] = True
            count += 1
            regs[dest] = u32(regs[dest] ^ u32((out_idx + byte) * 0x45D9F3B))
        else:
            raise RuntimeError(f"bad opcode {op:#x} at pc={pc}")

        s1_now = regs[(a >> 12) & 0xF]
        v = u32(regs[dest] ^ u32(s1_now ^ seed) ^ a)
        seed = u32(rol32(v, 9) + b + u32(pc * 0x3C6EF372))

    if count != 0x80:
        raise RuntimeError(f"expected 128 stores, got {count}")

    n = out[0]
    if not (1 <= n <= 0x7B):
        raise RuntimeError(f"bad length {n}")

    h = 0x811C9DC5
    for i in range(1, n + 1):
        c = out[i]
        if c <= 0x1F and c != 0x0A:
            raise RuntimeError(f"non-printable {c:#x}")
        if c > 0x7E:
            raise RuntimeError(f"non-printable {c:#x}")
        h = u32((h ^ c) * 0x1000193)

    trailer = out[n + 1] | (out[n + 2] << 8) | (out[n + 3] << 16) | (out[n + 4] << 24)
    if trailer != h:
        raise RuntimeError(f"FNV mismatch {trailer:#x} != {h:#x}")

    return bytes(out[1 : n + 1])


def main() -> None:
    binary = Path(sys.argv[1] if len(sys.argv) > 1 else "prince_walk")
    msg = decrypt(load_program(binary))
    print(msg.decode())
    for line in msg.decode().splitlines():
        if line.startswith("CSSCTF{"):
            print(f"\nFLAG: {line}")
            break


if __name__ == "__main__":
    main()
