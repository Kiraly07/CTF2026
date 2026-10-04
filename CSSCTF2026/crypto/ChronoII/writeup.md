---
title: "ChronoII"
ctf: "CSSCTF"
date: 2026-09-30
category: crypto
flag_format: "CSSCTF{...}"
---

The ciphertext from `/capture.json` and `/api/feed` repeats every 77 UTC seconds. Let `m = epoch % 77`; all 77 residues decrypt to the same plaintext with a shared 77-character key indexed by `(43 * m + i) mod 77`. Using the known `CSSCTF` prefix recovers this key:

```text
PHDDJKDQJKAIIBLMHDJKIILFBENFLMHIBMDJHKFENFQEJDCIINHKFJFHLFFIGIINMCHEGDQJFIGNA
```

The cipher shifts letters mod 26 and digits mod 10, advancing `i` only on alphanumeric characters. This script fetches a capture, computes its epoch, and decrypts it:

```python
import json
from datetime import datetime
from urllib.request import urlopen

KEY = "PHDDJKDQJKAIIBLMHDJKIILFBENFLMHIBMDJHKFENFQEJDCIINHKFJFHLFFIGIINMCHEGDQJFIGNA"
SHIFTS = [ord(c) - ord("A") for c in KEY]
A = 43

def decrypt(ct, m):
    out, i = [], 0
    for c in ct:
        if c.isalpha():
            shift = SHIFTS[(A * m + i) % 77]
            base = ord("A") if c.isupper() else ord("a")
            out.append(chr((ord(c) - base - shift) % 26 + base))
            i += 1
        elif c.isdigit():
            shift = SHIFTS[(A * m + i) % 77]
            out.append(str((int(c) - shift) % 10))
            i += 1
        else:
            out.append(c)
    return "".join(out)

data = json.load(urlopen("http://34.116.80.78:8001/capture.json"))
rec = data[0]
epoch = int(datetime.fromisoformat(rec["timestamp"].replace("Z", "+00:00")).timestamp())
print(decrypt(rec["ciphertext"], epoch % 77))
```

Flag:

```text
CSSCTF{th3_cl0ck_r3m3mb3rs_3very_s3c0nd}
```
