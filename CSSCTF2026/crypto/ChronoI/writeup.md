---
title: "ChronoI"
ctf: "CSSCTF"
date: 2026-09-30
category: crypto
flag_format: "CSSCTF{...}"
---

The timestamp `2026/09/21 14:35:07` gives the Vigenère key. Strip its non-digits, then map each digit `d` to `A + d`, producing `CACGAJCBBEDFAH`. The ciphertext is `ESUITO{gwfvb_xejqnf_nimgt_b_whhrlv}`; decrypt letters with the repeating key and leave punctuation unchanged:

```python
ct = "ESUITO{gwfvb_xejqnf_nimgt_b_whhrlv}"
ts = "2026/09/21 14:35:07"
key = "".join(chr(ord("A") + int(d)) for d in ts if d.isdigit())

out, i = [], 0
for c in ct:
    if c.isalpha():
        shift = ord(key[i % len(key)]) - ord("A")
        base = ord("A") if c.isupper() else ord("a")
        out.append(chr((ord(c) - base - shift) % 26 + base))
        i += 1
    else:
        out.append(c)
print("".join(out))
```

Flag:

```text
CSSCTF{every_second_hides_a_secret}
```
