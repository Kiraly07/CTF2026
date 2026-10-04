#!/usr/bin/env python3
"""The Astrolabe Overwrite / Ouroboros Singularity solver.

The nexus_core VM checks four field elements u0..u3 over p = 65521.
Registers must be loaded as reg_i = (u_i + beacon) mod p, then the
weighted cycle count must land in [112, 128]. The u vector is unique
and independent of the beacon.
"""

import re
import socket
import sys

MOD = 65521
HOST = "34.116.80.78"
PORT = 7654

# Unique solution of the halt predicate (beacon subtracted out).
U = (1, 218, 59611, 783)

OP_LOAD = 0x10
OP_JMP = 0x50
OP_HALT = 0x7F
BASE_TABLE = [0x10, 0x20, 0x30, 0x35, 0x40, 0x50, 0x7F, 0xFF]


class Assembler:
    """Encode a straight-line program for the self-permuting opcode map."""

    def __init__(self):
        self.reg = [0, 0, 0, 0]
        self.key = 0x5A
        self.cycles = 0
        self.table = BASE_TABLE[:]
        self.code = bytearray()

    def _emit(self, op, dst, b2, b3):
        index = self.table.index(op)
        opcode = (index ^ (self.key & 7)) & 7
        self.code += bytes([opcode, dst & 3, b2 & 0xFF, b3 & 0xFF])
        self.key = (self.key * 31 + (self.reg[0] & 0xFF)) & 0xFF

    def _swap(self):
        i = self.reg[0] & 7
        j = self.reg[1] & 7
        self.table[i], self.table[j] = self.table[j], self.table[i]

    def load(self, dst, imm):
        imm %= MOD
        self._emit(OP_LOAD, dst, (imm >> 8) & 0xFF, imm & 0xFF)
        self.reg[dst] = imm
        self.cycles += 1
        self._swap()

    def jmp0(self):
        # Relative offset 0: PC becomes the already-advanced PC. Costs 3.
        self._emit(OP_JMP, 0, 0, 0)
        self.cycles += 3
        self._swap()

    def halt(self):
        self._emit(OP_HALT, 0, 0, 0)
        self.cycles += 10


def build_payload(beacon):
    asm = Assembler()
    for i, u in enumerate(U):
        asm.load(i, (u + beacon) % MOD)
    # 4 loads cost 4. Thirty-six jumps cost 108. Halt adds 10 -> 122 cycles.
    for _ in range(36):
        asm.jmp0()
    asm.halt()
    if not 112 <= asm.cycles <= 128:
        raise RuntimeError(f"cycle window missed: {asm.cycles}")
    return bytes(asm.code)


def solve(host=HOST, port=PORT):
    with socket.create_connection((host, port), timeout=20) as sock:
        sock.settimeout(15)
        data = b""
        while b"bytes): " not in data:
            chunk = sock.recv(1)
            if not chunk:
                break
            data += chunk
        text = data.decode()
        beacon = int(re.search(r"0x([0-9A-Fa-f]+)", text).group(1), 16)
        payload = build_payload(beacon)
        sock.sendall(payload.hex().encode() + b"\n")
        out = b""
        while True:
            try:
                chunk = sock.recv(4096)
            except socket.timeout:
                break
            if not chunk:
                break
            out += chunk
    full = text + out.decode(errors="replace")
    match = re.search(r"CSSCTF\{[^}]+\}", full)
    if not match:
        sys.stderr.write(full)
        sys.exit(1)
    return match.group(0)


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else HOST
    port = int(sys.argv[2]) if len(sys.argv) > 2 else PORT
    print(solve(host, port))
