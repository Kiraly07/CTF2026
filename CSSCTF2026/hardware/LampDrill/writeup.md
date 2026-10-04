---
title: "LampDrill"
ctf: "CSSCTF"
date: 2026-09-30
category: reverse
flag_format: "CSSCTF{...}"
---

## Solve

This was an SVG logic diagram, not an executable. The first 12 circles encode four two-input examples: dark is `1`, light is `0`, and the arrow gives the result. They show an AND gate (`11 → 1`; `10`, `01`, and `00 → 0`). The next 48 circles are 24 input pairs. AND each pair, read left to right, and group the result into bytes, most-significant bit first.

The SVG keeps the circle order and fill values, so I parsed it directly instead of sampling pixels from the PNG:

```python
import re
import xml.etree.ElementTree as ET

root = ET.parse("lampDrill.svg").getroot()
ns = "{http://www.w3.org/2000/svg}"
circles = [p for p in root.iter(ns + "path") if " C " in p.get("d", "")]
bits = [int(re.search(r"fill:\s*([^;]+)", p.get("style", "")).group(1) == "#1c1915")
        for p in circles]
assert len(bits) == 60
assert bits[:12] == [1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0]

out = [bits[i] & bits[i + 1] for i in range(12, 60, 2)]
text = "".join(chr(int("".join(map(str, out[i:i + 8])), 2))
               for i in range(0, len(out), 8))
print(f"CSSCTF{{{text}}}")
```

The decoded text is `css`.

## Flag

`CSSCTF{css}`
