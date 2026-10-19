# You Wouldn't Git It — OSINT (125 pts)

"Everybody wants to be a content creator these days... When I go on social media all I want to do is doom scroll until I fall asleep." This is the sequel to The Vibes Are Freaking Me Out (chal 65), so everything I learned there applies: b1tfr34k, the HIPS extension, and the hidden-text tricks.

## How I solved it

The "doom scroll" line is literal — the DEADFACE social platform is **DoomScroll** at doomscroll.dctf.io.

Browsing `/explore` and searching tags, there's exactly one `#memes` post: **post 247**, posted by **gh0st404** ("me if i evr got a job tho"). That matches the challenge rant about content creators getting paid for memes.

The post's comments are where it gets fun. Most of them look empty or broken — but after chal 65, I already knew the HIPS trick: the extension hides text in invisible Unicode. The other comments carry zero-width characters that decode to "YES! YOU'RE ALL USING IT!" (they're literally using HIPS to talk in hidden text on the meme post).

b1tfr34k's comment reads as visible nonsense capslock rambling:

> GREEN GIRAFFES CHOCOLATE LEPERS LEAPING TANGERINES YEETING THE MYTHICAL POKEMON TO LEGENDARY PROPORTIONS

But it's followed by a run of Unicode **tag characters** (U+E0020–U+E007E) — the "hidden in plain sight" encoding from the same HIPS toolbox. Decoding each tag char as `chr(ord(c) - 0xE0000)` turns them straight into plaintext:

```python
hidden = [c for c in comment if 0xE0020 <= ord(c) <= 0xE007E]
print("".join(chr(ord(c) - 0xE0000) for c in hidden))
```

The joke about "13 hackers walked into a bar" falls out.

## Flag

```
deadface{13_h4ck3r5_walk3d_int0_a_bar_each_says_Ill_h4v3_a_r00t_b33r}
```
