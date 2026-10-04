#!/usr/bin/env python3
"""2(-1) Senses — recover the flag from WAV metadata + the spectrogram name.

The artist/comment INFO tags hold the flag skeleton
CSSCTF{WHOS_THIS_FLUFFMASTER_MR...}
The spectrogram (about 2.3–4.5 kHz) spells CHINASKI next to a profile.
That name is the cat/track on Venetian Snares' Songs About My Cats,
the same album as the track Fluff Master.
"""

import wave
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import signal

WAV = Path(__file__).with_name("2senses_puzzle.wav")
OUT = Path(__file__).with_name("spectrogram.png")


def info_tags(path: Path) -> dict[str, str]:
    data = path.read_bytes()
    off = 12
    tags = {}
    while off + 8 <= len(data):
        cid = data[off : off + 4]
        size = int.from_bytes(data[off + 4 : off + 8], "little")
        payload = data[off + 8 : off + 8 + size]
        if cid == b"LIST" and payload[:4] == b"INFO":
            p = 4
            while p + 8 <= len(payload):
                key = payload[p : p + 4].decode("latin1")
                n = int.from_bytes(payload[p + 4 : p + 8], "little")
                tags[key] = payload[p + 8 : p + 8 + n].split(b"\x00", 1)[0].decode("latin1")
                p += 8 + n + (n & 1)
        off += 8 + size + (size & 1)
    return tags


def save_spectrogram(path: Path, out: Path) -> None:
    with wave.open(str(path), "rb") as wf:
        sr = wf.getframerate()
        x = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float64)
    f, _t, sxx = signal.spectrogram(
        x, sr, nperseg=2048, noverlap=2048 - 64, scaling="spectrum", mode="magnitude"
    )
    db = 20 * np.log10(sxx + 1e-12)
    band = (f >= 1500) & (f <= 8000)
    crop = db[band]
    lo, hi = np.percentile(crop, 55), np.percentile(crop, 99.5)
    img = np.clip((crop - lo) / (hi - lo), 0, 1)
    img = (img[::-1] * 255).astype(np.uint8)
    Image.fromarray(img).save(out)


def main() -> None:
    tags = info_tags(WAV)
    artist = tags["IART"]  # CSSCTF{WHOS_THIS_FLUFFMASTER_MR...
    close = tags["ICMT"]  # }
    # The spectrogram spells CHINASKI. That alias was rejected in the flag.
    # Henry Chinaski is Charles Bukowski's alter ego; the profile is the man.
    name = "BUKOWSKI"
    flag = artist.replace("...", f"_{name}") + close
    save_spectrogram(WAV, OUT)
    print(flag)


if __name__ == "__main__":
    main()
