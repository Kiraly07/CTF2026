# Headshot — Steganography (10 pts)

The download is a ZIP with four PNGs: headshot001-003 plus an extra `headshot003.png_original`. That naming basically tells you which file was tampered with.

## How I solved it

Compared headshot003.png against its original and ran exiftool over everything. The tampered one has an extra PNG tEXt Comment chunk:

```
Comment: deadface{b00m_h34Dsh0TTT}
```

Done. Sometimes the easy ones really are that easy — the challenge is just noticing the `_original` file and diffing against it.

## Flag

```
deadface{b00m_h34Dsh0TTT}
```
