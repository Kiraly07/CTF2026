---
title: "TheFalseTimeline"
ctf: "CSSCTF"
date: 2026-09-30
category: forensics
flag_format: "CSSCTF{...}"
---

## Solve

The relay log claims KAI-7 ran the emergency export at 03:17, but the image's other records contradict it. I extracted the EXT4 files from `nexus_relay.img` (`xz -dk nexus_relay.img.xz`, then `fls -r -p` and `icat`). The useful artifacts were `/etc/machine-id`, `/opt/nexus/lib/exporter.py`, `/var/cache/nexus/.ekey-cache`, `/var/lib/nexus/metadata.db`, `auth.log`, `audit.log`, and the forged `relay.log`.

`auth.log` and the database show KAI-7 logged out at 03:05 after only a status check. Root switched to `svc-relay` at 03:10; that service's session `aab0c8b2-f8b1-4f11-9a72-6d8123a1005a` ran `nx-export --emergency` at epoch `4157543568` (03:12:48, AEST +10 in 2101). The audit log records UID 998 for the export. The later `touch -r` hid the cache file's mtime, and `relay.log` was altered to frame KAI-7.

The exporter derives the AES-GCM key as `SHA256(machine_id|session_uuid|event_epoch)`. The `.ekey-cache` blob begins with `NXKEY_V1`, followed by a 12-byte nonce and ciphertext. Using the service session and audit/job epoch decrypts the flag:

```python
import hashlib
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

machine_id = Path("machine-id").read_text().strip()
blob = Path(".ekey-cache").read_bytes()
assert blob.startswith(b"NXKEY_V1")
nonce, ciphertext = blob[8:20], blob[20:]
material = "aab0c8b2-f8b1-4f11-9a72-6d8123a1005a|4157543568"
key = hashlib.sha256(f"{machine_id}|{material}".encode()).digest()
print(AESGCM(key).decrypt(nonce, ciphertext, None).decode())
```

## Flag

`CSSCTF{kai_did_not_do_it}`
