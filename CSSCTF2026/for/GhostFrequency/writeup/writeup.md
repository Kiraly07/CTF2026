---
title: "GhostFrequency"
ctf: "CSSCTF"
date: 2026-09-30
category: forensics
flag_format: "CSSCTF{...}"
---

## Solve

The stereo WAV carries two channels: Martin M1 SSTV on the left and Bell 202 AFSK telemetry on the right. The SSTV diagnostic gives the recovery rules: `PA = D0 ^ D1 ^ D2 ^ D3`, `PB = D4 ^ D5 ^ D6 ^ D7`, the CRC32 values for the data blocks, and `ARCHIVE_BYTES: 5757`. Split the channels with `ffmpeg`; decode the right at 1200 baud, mark 1200 Hz, space 2200 Hz, 8N1 (for example, with `minimodem -r -f right.wav 1200 -M 1200 -S 2200 -8 -q`).

For session `NX-771`, the packets include data sequences 0, 1, 3, 4, 6, and 7 plus both parity blocks; sequences 2 and 5 are missing. Recover them by XORing the corresponding parity with the other three data blocks in that group. Retries can be stale: sequence 6 has two copies, and only the one with CRC32 `2A18C562` matches the diagnostic table; discard `C04CF7F5`. Join `D0` through `D7` in order. Skip the 10-byte header, raw-DEFLATE exactly 5757 bytes, then open the resulting tar and read `NX-771/final_message.txt`.

The end-to-end `writeup/solve.py` reads the WAV, demodulates the right channel in Python (or uses cached `/tmp/ghost/packets.txt`), applies FEC, checks CRCs, and extracts the flag. It needs NumPy.

## Flag

`CSSCTF{th3_gh0st_fr3qu3ncy_w4s_n3v3r_s1l3nt}`
