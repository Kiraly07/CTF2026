---
title: "Echoes of the Relay"
ctf: "CSSCTF"
date: 2026-09-30
category: forensics
flag_format: "CSSCTF{...}"
---

## Solve

I found the deleted operator note in the EXT4 image with Sleuth Kit. It was inode 25; the diagnostic PNG was inode 24:

```bash
fls -r -a -d relay_backup.img
icat relay_backup.img 25 > emergency_note.txt
icat relay_backup.img 24 > relay_status.png
```

The note gives the ZIP password `severance2101` and says to look past the visible image. `relay_status.png` has a ZIP appended after its PNG `IEND` chunk. I carved the ZIP and read the extracted transmission:

```python
from pathlib import Path
import zipfile

data = Path("relay_status.png").read_bytes()
iend = data.find(b"IEND")
zip_off = data.find(b"PK\x03\x04", iend + 4)
assert iend >= 0 and zip_off >= 0
Path("hidden.zip").write_bytes(data[zip_off:])

with zipfile.ZipFile("hidden.zip") as zf:
    zf.extractall("out", pwd=b"severance2101")
print(Path("out/transmission/core_recovery.txt").read_text())
```

## Flag

`CSSCTF{d3l3t3d_d03snt_m34n_g0n3}`
