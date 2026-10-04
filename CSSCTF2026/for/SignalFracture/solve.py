#!/usr/bin/env python3
"""Signal Fracture (CSSCTF) — reconstruct emergency_burst_17 from spool + cache + uplink."""

import gzip
import hashlib
import io
import os
import struct
import tarfile
import zlib

from scapy.all import UDP, Raw, rdpcap

BASE = os.path.dirname(os.path.abspath(__file__))
EXTRACTED = os.path.join(BASE, "extracted")
IMG = os.path.join(EXTRACTED, "KBR17_relay.img")
PCAP = os.path.join(EXTRACTED, "KBR17_uplink.pcap")
FS = os.path.join(EXTRACTED, "fs")

EXPECTED = {
    0: "fdde3a6dc2c9d43e0bbf21b1e90d1214d5776405397ab54426ff7bb6bec8831d",
    1: "82fc22cae997c805035ef22fd98c260c626c67aaaef45301236bc549897e47ae",
    2: "5cd4fd1f9bdc1360dc272362ee421b4f62f2818c7d68332440042c3e46b8f732",
    3: "3258da54f56a49e79a1719d9145a6cd82691a0d2b10a9a1e8782e9cacf507dc6",
    4: "4e86900e878981dcaec4e63b381395496598282d68f2a63e578350bdccfe7daa",
    5: "27ffcedf5e0e4bbec59c36c662aa1397d729c9a8bcd6005131a048856efb3e58",
    6: "fa9dbecb99768ea4d8470546b270845127278e797e09f71073df7e5658bdabae",
    7: "a9d2e70930248e74b776c1db737637d2e2a354308d216921225216288a94b7d0",
}
TARGET = 0x6E2C17A9


def parse_header(buf, off=0):
    magic, sess, seq, total, plen, crc = struct.unpack_from(">IIHHII", buf, off)
    assert magic == 0x4E584652  # NXFR
    payload = buf[off + 0x14 : off + 0x14 + plen]
    assert (zlib.crc32(payload) & 0xFFFFFFFF) == crc
    return sess, seq, total, payload


def take(payloads, seq, payload, src):
    digest = hashlib.sha256(payload).hexdigest()
    if digest != EXPECTED[seq]:
        print(f"  skip seq={seq} from {src} (sha mismatch)")
        return
    payloads[seq] = payload
    print(f"  keep seq={seq} from {src} ({len(payload)} bytes)")


def main():
    payloads = {}

    # Cache-resident fragments (seq 1, 4)
    for name in os.listdir(FS):
        if not name.endswith(".blob"):
            continue
        data = open(os.path.join(FS, name), "rb").read()
        if not data.startswith(b"NXFR"):
            continue
        sess, seq, total, payload = parse_header(data)
        if sess == TARGET:
            take(payloads, seq, payload, name)

    # Uplink tap (seq 3, 6-retry, 7) — prefer catalog-matching copy on retries
    for i, pkt in enumerate(rdpcap(PCAP), 1):
        if UDP not in pkt or Raw not in pkt:
            continue
        raw = bytes(pkt[Raw].load)
        if not raw.startswith(b"NXFR"):
            continue
        sess, seq, total, payload = parse_header(raw)
        if sess == TARGET:
            take(payloads, seq, payload, f"pcap#{i}")

    # Raw spool ring on partition 2 (0xda) — index purged, data not zeroed
    with open(IMG, "rb") as f:
        f.seek(53248 * 512)
        part2 = f.read(65536 * 512)
    idx = 0
    while True:
        j = part2.find(b"NXFR", idx)
        if j < 0:
            break
        if j + 0x14 <= len(part2):
            plen = struct.unpack_from(">I", part2, j + 0x0C)[0]
            if plen < 100_000 and j + 0x14 + plen <= len(part2):
                try:
                    sess, seq, total, payload = parse_header(part2, j)
                except AssertionError:
                    idx = j + 4
                    continue
                if sess == TARGET:
                    take(payloads, seq, payload, f"spool@{j}")
        idx = j + 4

    missing = set(range(8)) - set(payloads)
    if missing:
        raise SystemExit(f"missing fragments: {sorted(missing)}")

    obj = b"".join(payloads[i] for i in range(8))
    tar_bytes = gzip.decompress(obj)
    with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as tf:
        msg = tf.extractfile("final_message.txt").read().decode()
    print(msg)
    for line in msg.splitlines():
        if "CSSCTF{" in line:
            print("FLAG:", line.split(":", 1)[-1].strip())


if __name__ == "__main__":
    main()
