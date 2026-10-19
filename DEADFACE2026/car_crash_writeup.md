# Car Crash — OSINT (50 pts)

One photo of a traffic accident with a commercial truck. Figure out which company owns the truck and when that company was founded. Flag is the founding date: `deadface{MM_DD_YYYY}`.

## How I solved it

EXIF was a dead end — the image is AI-generated (C2PA metadata mentions gpt-image), so no GPS or camera data to lean on.

The trick is the truck itself. I ran tesseract on an upscaled, grayscaled copy of the image:

```
convert 41_car_crash.png -resize 200% -colorspace Gray ocr.png
tesseract ocr.png out - psm 11
```

psm 11 (sparse text mode) picks up scattered text like storefront signage (MOD PIZZA, WESTWOOD SQUARE, etc. — location fluff) and, most importantly, the DOT number on the truck cab:

```
USDOT: 080806
```

USDOT numbers are public. Look up 80806 on FMCSA (ai.fmcsa.dot.gov/SMS/Carrier/80806) and you get **J.B. Hunt Transport Services**, Lowell, Arkansas.

From there it's a plain lookup: J.B. Hunt was founded **August 10, 1961** (Wikipedia infobox).

## Flag

```
deadface{08_10_1961}
```
