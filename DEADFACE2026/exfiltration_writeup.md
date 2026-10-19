# Exfiltration — Steganography (75 pts)

The ZIP unpacks to 20 JPEGs (`image_01.jpg` ... `image_20.jpg`), all tiny and boring. No appended data after EOI, no steghide password, nothing.

## How I solved it

exiftool showed each image has two interesting fields: an **EXIF DateTimeOriginal** (timestamps spanning 14:02–15:12) and an **ImageUniqueID** like `IMG_6365`, `IMG_7b`, `IMG_61`...

The ImageUniqueIDs aren't unique IDs — the hex digits decode straight to ASCII pairs:

```
IMG_6465 = "de"   IMG_61 = "a"   IMG_6466 = "df"
IMG_6365 = "ce"   IMG_7b = "{"   IMG_7469 = "ti" ...
```

Key detail: the **filenames are not in message order**. Sorting by DateTimeOriginal gives the real order. Concatenate the decoded characters in timestamp order and the message falls out.

## Flag

```
deadface{timing-is-everything}
```
