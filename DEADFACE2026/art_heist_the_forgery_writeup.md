# Art Heist: The Forgery — Forensics (25 pts)

A ZIP of five painting scans. One of them is LAMIA's forgery.

## How I solved it

`Painting_002.png` (the Mona Lisa) sticks out immediately when you compare metadata:

- Different file mtime (Oct 14, vs Sep 1 for the rest)
- Software tag: **"LAMIA Restoration Utility 0.0.13"** (the others say "Atelier Archive")
- Extra PNG tEXt chunks: "checksum mismatch; palette recovered from cache"
- XMP Creator: "Leonardo da Vinci / LAMIA", Title "Mona Lisa Loading", Description "Authenticity status: pending..."

And the XMP `dc:Identifier` field contains the flag. LAMIA really does sign her work.

## Flag

```
deadface{L4MIA_SIGNS_HER_WORK}
```
