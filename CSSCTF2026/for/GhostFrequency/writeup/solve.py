#!/usr/bin/env python3
"""GhostFrequency (CSSCTF) — reconstruct NX-771 telemetry archive."""

from __future__ import annotations

import base64
import io
import tarfile
import wave
import zlib
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
WAV = ROOT / "KBR17_blackbox.wav"


def b64pad(s: str) -> str:
    return s + "=" * ((-len(s)) % 4)


def xor_bytes(*chunks: bytes) -> bytes:
    acc = bytearray(chunks[0])
    for chunk in chunks[1:]:
        for i, b in enumerate(chunk):
            acc[i] ^= b
    return bytes(acc)


def decode_bell202_ascii(mono: np.ndarray, rate: int = 48000) -> list[str]:
    """Soft AFSK1200 demod → 8N1 ASCII lines (NXPKT records)."""
    bit_samples = rate // 1200  # 40 @ 48 kHz
    mark_f, space_f = 1200.0, 2200.0
    nbits = len(mono) // bit_samples
    t = np.arange(bit_samples) / rate
    mark_lo = np.exp(-2j * np.pi * mark_f * t)
    space_lo = np.exp(-2j * np.pi * space_f * t)

    bits = np.empty(nbits, dtype=np.uint8)
    for i in range(nbits):
        seg = mono[i * bit_samples : (i + 1) * bit_samples]
        bits[i] = 1 if abs(np.dot(seg, mark_lo)) > abs(np.dot(seg, space_lo)) else 0

    # UART 8N1: look for start bit 0, then 8 data bits, stop bit 1
    out: list[int] = []
    i = 0
    while i + 10 < len(bits):
        if bits[i] != 0:
            i += 1
            continue
        frame = bits[i + 1 : i + 9]
        stop = bits[i + 9]
        if stop != 1:
            i += 1
            continue
        # LSB first
        val = 0
        for b in frame:
            val = (val >> 1) | (int(b) << 7)
        out.append(val)
        i += 10

    text = bytes(out).decode("latin1", errors="ignore")
    return [ln for ln in text.splitlines() if ln.startswith("NXPKT|")]


def parse_packets(lines: list[str]) -> list[dict]:
    packets = []
    for line in lines:
        d: dict = {"_raw": line}
        for part in line.split("|"):
            if "=" in part:
                k, v = part.split("=", 1)
                d[k] = v
        d["raw"] = base64.b64decode(b64pad(d.get("DATA", "")))
        packets.append(d)
    return packets


def recover_archive(packets: list[dict]) -> bytes:
    """FEC: PA = D0^D1^D2^D3, PB = D4^D5^D6^D7. Prefer CRC-matching copies."""
    auth = {
        0: 0xA66FEFC8,
        1: 0x7C3DCD2A,
        2: 0x1812F5CD,
        3: 0xBB1810C0,
        4: 0xD6CCE79E,
        5: 0x6B9F6558,
        6: 0x2A18C562,
        7: 0x3D924BBF,
    }
    blocks: dict[int, bytes] = {}
    pa = pb = None

    for p in packets:
        if p.get("SESSION") != "NX-771":
            continue
        if p.get("TYPE") == "PARITY":
            if p.get("GROUP") == "A":
                pa = p["raw"]
            elif p.get("GROUP") == "B":
                pb = p["raw"]
            continue
        if p.get("TYPE") != "DATA":
            continue
        seq = int(p["SEQ"])
        crc = zlib.crc32(p["raw"]) & 0xFFFFFFFF
        # Retries may be stale — only keep CRC-authoritative copies.
        if crc == auth[seq]:
            blocks[seq] = p["raw"]

    assert pa is not None and pb is not None
    # Recover erasures
    if 2 not in blocks:
        blocks[2] = xor_bytes(pa, blocks[0], blocks[1], blocks[3])
    if 5 not in blocks:
        blocks[5] = xor_bytes(pb, blocks[4], blocks[6], blocks[7])

    assert (zlib.crc32(blocks[2]) & 0xFFFFFFFF) == auth[2]
    # OCR on SSTV may misread D5 CRC low nibble; recovered block still satisfies PB.
    assert xor_bytes(blocks[0], blocks[1], blocks[2], blocks[3]) == pa
    assert xor_bytes(blocks[4], blocks[5], blocks[6], blocks[7]) == pb

    return b"".join(blocks[i] for i in range(8))


def extract_flag(archive: bytes) -> str:
    # Custom 10-byte header, then raw DEFLATE (ARCHIVE_BYTES=5757)
    inflated = zlib.decompress(archive[10 : 10 + 5757], -15)
    with tarfile.open(fileobj=io.BytesIO(inflated), mode="r:") as tf:
        member = tf.extractfile("NX-771/final_message.txt")
        assert member is not None
        text = member.read().decode()
    for line in text.splitlines():
        if line.startswith("CSSCTF{"):
            return line.strip()
    raise RuntimeError("flag not found")


def main() -> None:
    with wave.open(str(WAV), "rb") as w:
        assert w.getnchannels() == 2 and w.getframerate() == 48000
        frames = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    right = frames[1::2].astype(np.float64)

    # Prefer minimodem if available; otherwise pure-Python demod.
    packets_path = Path("/tmp/ghost/packets.txt")
    if packets_path.exists():
        lines = packets_path.read_text().splitlines()
        lines = [ln for ln in lines if ln.startswith("NXPKT|")]
    else:
        lines = decode_bell202_ascii(right)

    packets = parse_packets(lines)
    archive = recover_archive(packets)
    flag = extract_flag(archive)
    print(flag)


if __name__ == "__main__":
    main()
