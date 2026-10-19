# Infrequent Emojis — Cryptography (90 pts)

spookyboi's DoomScroll post 252: a big image plus emoji-coded comments underneath.

## How I solved it

**Part 1 — the comments.** They're a monoalphabetic substitution cipher: 26 distinct emojis → letters. I solved it with simulated annealing + bigram scoring (dictionary hits got it to 188/196 words). Decoded:

```
the lookup table is live. all active communications must shift to this format
to bypass standard string scanners.
```

That gives the mapping (🕯=e ☣=t 🌙=s 📟=i 🖤=o 💀=a 🦇=n 🔮=r 🕸=l 💾=h ⚰=c 🌩=u 🦴=g 🦉=p ⛓=m 🧪=y 🪦=d 🩸=f 📡=k ☠=b 🔥=w ☢=v 🔌=j 🔏=z 👁=q 🥀=x).

**Part 2 — the flag.** The main post image is written in the *same* emoji cipher. OCR is useless on emoji glyphs, so I built a template matcher: rendered each of the 26 emojis from NotoColorEmoji with PIL, composited on the background, and matched by L2 distance. The image is 6 rows of emoji plus literal `{`, `}` and `_` bars:

```
Row0: deadfac  Row1: e{pleas  Row2: e_try_o
Row3: ut_my_n   Row4: ew_stan  Row5: dard}
```

## Flag

```
deadface{please_try_out_my_new_standard}
```
