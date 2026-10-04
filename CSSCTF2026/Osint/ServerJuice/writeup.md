---
title: "Social"
ctf: "CSS CTF 2026: Return of Nexus"
date: 2026-09-30
category: osint
flag_format: "CSSCTF{...}"
---

The challenge points to the public Instagram account `cybersecuritysydney`. Its bio and recent captions had no flag, so I scrolled to the older posts and checked the comments. Logged-out profile JSON only returns the first 12 of 26 posts; the timeline query `PolarisProfilePostsTabContentQuery_connection` (`doc_id` `28844755988451916`) takes `username=cybersecuritysydney` and an `end_cursor` in the form `<media_pk>_60933756878` to fetch the rest.

The flag is in a comment on [`DWL9S-wkyJT`](https://www.instagram.com/p/DWL9S-wkyJT/), an AGM/voting notice. It is comment `18081636491372527` from `harrysalvesen`.

## Flag

```text
CSSCTF{premiumreserve}
```
