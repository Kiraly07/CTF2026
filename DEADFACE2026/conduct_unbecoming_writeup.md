# Conduct Unbecoming — Steganography (75 pts)

A "recovered document" from Night Veil University: a Student Conduct Notice for Cornelius Kellerman. We need the **asset-id used to create the document**.

## All the obvious stuff fails first

I went through the whole menu before finding it, so you don't have to:

- exiftool -a -u -g1: only Affinity Photo 2.6.5 XMP history and IPTC "NVU Conduct Notice" — no asset id
- steghide/stegseek with rockyou: nothing
- JSteg-style DCT extraction + chi-square: clean, no embedding
- No trailing data after EOI, binwalk/ELA: nothing
- Spatial LSBs: nothing

The flag is not in metadata or steganography. It's printed **in the image itself**.

## The actual trick: printer tracking dots

The document image carries a nearly-invisible **Machine Identification Code**-style dot grid — yellow-ish pixels around RGB (255,255,247) on white paper. That's faint enough to survive grayscale conversion, OCR, and ELA without anyone noticing.

The way in was the **Cb chroma channel**: pixels with Cb ≤ 124 all clustered in one tiny 86×147px block at the bottom-right corner of the page (next to the "Page 1 of 1" footer, outside the text area). Nothing else on the page is blue-deficient like that.

Masking the blue-deficient pixels in that region exposes a regular lattice of ~4px dots at 12px pitch: **15 rows × 8 columns**.

Decoding:

- Row 0: all 8 dots present — sync row
- Rows 1–12: one ASCII byte each, dot present = 1, MSB leftmost

```
01001110 01010110 01010101 00101101 01010000 01010010 01001001 01001110 01010100 00101101 00110001 00110111
 N        V        U        -        P        R        I        N        T        -        1        7
```

- Rows 13–14: empty (message done)

## Flag

```
deadface{NVU-PRINT-17}
```
