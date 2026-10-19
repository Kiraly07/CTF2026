# DECODE-DLE — Cryptography (25 pts)

Don't be fooled by the name — the "Decoddle" image isn't a colored-squares puzzle, it's a classic **logic lock** puzzle (the kind where you guess a 3-digit code from clue rows like "one number correct, wrong place").

## How I solved it

I laid out the grid: 5 clue rows, each with three boxed digits plus a text clue to the right. OCR'd the clue texts:

1. One number is correct but in the wrong place
2. Nothing is correct
3. Two numbers correct, both in the wrong place
4. One number correct and in the right place
5. Two numbers correct, both in the wrong place

Reading the actual digit glyphs was the annoying part — I clustered identical glyph shapes across rows (8 unique glyphs total), then identified each digit with tesseract plus rendering each glyph as ASCII art and template-matching against every installed font. Grid:

```
8 6 3 |  2 5 0 |  1 6 8 |  7 3 5 |  6 8 7
```

Then just brute-forced 000-999 against all five clues. Exactly one code satisfies everything: **716**.

Sanity check: 863 → 6 misplaced ✓, 250 → nothing ✓, 168 → 1 and 6 misplaced ✓, 735 → 7 in place ✓, 687 → 6 and 7 misplaced ✓.

## Flag

```
deadface{716}
```
