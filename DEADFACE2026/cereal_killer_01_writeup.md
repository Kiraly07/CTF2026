# Cereal Killer 01 — Reverse Engineering (50 pts)

A tinyurl link. What's behind it: a 32-bit x86 ELF.

## How I solved it

The tinyurl interstitial leaks the real CDN URL (`...re01/re01-lin-x86.bin`) — download it with a browser User-Agent or the CDN ignores you.

Reversing the binary: the password check compares `SHA1(input)` (standard constants) against a hex string that's stored **wide** (UTF-16LE) and encoded with a **custom base64 alphabet**, also stored wide at 0x4920:

```
ZKj9n+yf0wDVX1s/5YbdxSo=ILaUpPBCHg8uvNO4klm6iJGhQ7eFrWczAMEq3RTt
```

Decode with that alphabet → expected hash `68158678a3f9d76a3d1ca12d20b2d6af9bd3f290`. Rockyou cracks it: **cookiecrisp**.

There's a second blob in the same custom-wide-base64 at 0x47e0: 59 bytes of RC4 ciphertext. RC4 with key "cookiecrisp" decrypts to a URL ("Good job! You are ALMOST there..."):

```
https://Lerealkiller.lyttonlabs.org/unwanted-guests/ick.png
```

That subdomain is dead (NXDOMAIN), but the image also lives on the DEADFACE CDN at `.../2026/img/ick.png`. OCR it and the flag is written on the image, signed by "Dr. Charles K. Gesch-ICK-ter, Director, Lytton Labs".

## Flag

```
deadface{You-Vill-Eat-Ze-Bugz-Und-You-Vill-Be-Happy!!!}
```
