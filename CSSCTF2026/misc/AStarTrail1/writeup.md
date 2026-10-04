---
title: "A Star Trail 1"
ctf: "CSSCTF"
date: 2026-09-30
category: misc
flag_format: "CSSCTF{...}"
---

## Solve

I treated `A_Star_Trail.png` as an undirected graph: the white dashed lines are legal hops, and their labels are travel times in days. Tracing the lines to their endpoints shows that Earth is a node where the 5.0- and 10.7-day routes meet. Dijkstra's algorithm gives the unique shortest route to Lancer-RXKRD:

`Earth → Pallus-XA → 12-Puck-8 → Jip-Reia → Taylor-3489 → Lancer-RXKRD`

Its travel time is `10.7 + 1.8 + 0.4 + 5.5 + 2.6 = 21.0` days, within the 25-day limit. The map is not to scale, so pixel distance is not a useful A* heuristic. The next shortest simple route takes 21.6 days. The flag uses the first character of each intermediate stop only (not Earth or Lancer-RXKRD), followed by the duration to one decimal place.

## Flag

`CSSCTF{P1JT-21.0}`
