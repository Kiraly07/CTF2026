# Hidden Loot Box — Steganography (15 pts)

"Never judge a book by its cover." A single page at http://45.79.200.170:3001/ showing a loot box.

## How I solved it

I started steg-braining on cover.jpg — exiftool, strings, the works. Total waste of time. The JPEG is clean. This isn't file steg at all, it's a web trick.

`curl` the page source and the gimmick is right there:

```html
<div class="loot-frame">
  <img class="secret" src="/static/hidden.png" alt="old loot box">
  <img class="cover"  src="/static/cover.jpg" alt="loot box">
</div>
```

Two images stacked. The CSS explains the rest:

```css
.secret { position: relative;      z-index: 1; }
.cover  { position: absolute; inset: 0; z-index: 2; }
```

The cover is absolutely positioned **on top of** the secret image — the browser only ever paints cover.jpg. hidden.png is sitting there underneath the whole time, served as a perfectly normal file. "Never judge a book by its cover" indeed.

So just grab it:

```
curl -o hidden.png http://45.79.200.170:3001/static/hidden.png
```

The flag is literally rendered as text inside that PNG. Any image viewer (or tesseract if you're lazy) reads it out. `uh_I_feel_exposed` is pretty self-referential for an image that was exposed the whole time.

## Flag

```
deadface{uh_I_feel_exposed}
```
