# Hail Caesar — Cryptography (5 pts)

A photo of sticky notes next to a computer. The handwritten note reads:

```
Zl qbt'f anzr vf Bqva
```

## How I solved it

Title says it all — Caesar. A shift of 13 (ROT13) decodes it:

```
Zl -> My    qbt'f -> dog's    anzr -> name    vf -> is    Bqva -> Odin
```

"My dog's name is Odin" — matches the dog doodle on the same note. OCR was useless on the cursive, but the word shapes `anzr`/`vf` were enough to confirm ROT13 and work out the rest.

## Flag

```
deadface{Odin}
```
