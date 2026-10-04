---
title: "Signal Fracture"
ctf: "CSSCTF"
date: 2026-09-30
category: forensics
flag_format: "CSSCTF{...}"
---

## Solve

I reconstructed session `6E2C17A9` from the relay image and uplink capture. The EXT4 partition contains the scheduler database and cache blobs; the second partition is a raw spool ring whose index was purged but whose records remain. `relay.db` lists eight fragments and SHA-256 hashes for each payload. The NXFR header is big-endian: magic, session ID, sequence, total, payload length, CRC32, then payload. CRC32 checks each candidate; the catalog hashes identify the right copies.

I recovered sequences 0, 2, and 5 from the spool, 1 and 4 from cache, and 3, 6, and 7 from the PCAP. Sequence 6 has two uplink retries, so I kept only the copy matching the catalog hash. After ordering payloads by sequence, I concatenated them, gunzipped the object, and extracted `final_message.txt` from the tar archive. The included `solve.py` implements this end to end; it requires Scapy to read the PCAP.

Key parameters for reproducing the solve: target session `0x6E2C17A9`; spool partition starts at sector 53248 and is 65536 sectors long. Verify SHA-256 over payload bytes only, not the fragment header.

## Flag

`CSSCTF{fragment_t3ll_th3_st0ry}`
