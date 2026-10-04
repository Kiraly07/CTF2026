---
title: "Welcome to Star City"
ctf: "CSSCTF"
date: 2026-09-30
category: web
flag_format: "CSSCTF{...}"
---

The homepage links to `style.css`; the flag is in a trailing comment encoded as Base64, then URL-encoded. I fetched the stylesheet and decoded the comment:

```bash
curl -s http://34.116.80.78:9981/style.css | tail -c 120
```

```python
import base64
import urllib.parse

s = "Q1NTQ1RGJTdCd2VfQlUxTFRfdGhpc19jaXR5X2Zyb21fcjBja19hbmRfUjAxMSU3RA"
pad = s + "=" * ((4 - len(s) % 4) % 4)
print(urllib.parse.unquote(base64.b64decode(pad).decode()))
```

## Flag

```text
CSSCTF{we_BU1LT_this_city_from_r0ck_and_R011}
```
