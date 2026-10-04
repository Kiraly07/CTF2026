---
title: "2(-1) Senses"
ctf: "CSSCTF Semester 2 2026"
date: 2026-09-30
category: osint
flag_format: "CSSCTF{...}"
---

The WAV's `LIST INFO` tags give the flag skeleton: `IART` contains `CSSCTF{WHOS_THIS_FLUFFMASTER_MR...` and `ICMT` contains `}`. The missing name is drawn in the spectrogram. Keep the volume low; the file has harsh high-frequency energy.

```python
import wave
import numpy as np
from PIL import Image
from scipy import signal

with wave.open("2senses_puzzle.wav", "rb") as wf:
    sr = wf.getframerate()
    x = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float64)

f, _, sxx = signal.spectrogram(
    x, sr, nperseg=2048, noverlap=2048 - 64,
    scaling="spectrum", mode="magnitude"
)
db = 20 * np.log10(sxx + 1e-12)
band = (f >= 1500) & (f <= 8000)
crop = db[band]
lo, hi = np.percentile(crop, 55), np.percentile(crop, 99.5)
img = np.clip((crop - lo) / (hi - lo), 0, 1)
Image.fromarray((img[::-1] * 255).astype(np.uint8)).save("spectrogram.png")
```

The image spells **Chinaski** and draws a man's profile. Searching the name with “Fluff Master” points to Venetian Snares' *Songs About My Cats*: “Chinaski” and “Fluff Master” are tracks, and “Look” is known for cat photos hidden in its spectrogram. Chinaski is the alter ego of Charles Bukowski, so the missing name is `BUKOWSKI` (the alias guesses `MR_CHINASKI` and `MR.CHINASKI` were rejected).

## Flag

```text
CSSCTF{WHOS_THIS_FLUFFMASTER_MR_BUKOWSKI}
```
