---
title: "A Star Trail 2"
ctf: "CSSCTF"
date: 2026-09-30
category: misc
flag_format: "CSSCTF{...}"
---

## Solve

Each Markdown file in `map.zip` describes a planet: its six-character ID is the filename, `Coords:` gives its point in `[0, 100] × [0, 100]`, and `[[ID]]` lines list legal hops. The links are bidirectional. I weighted each edge by Euclidean distance and ran A* from `S0jRxc` to `yRJyDb`, using straight-line distance to the goal as the heuristic.

The fewest-hop route is only 13 hops, but it uses long Delaunay edges and produces gibberish; the minimum-distance route has 136 stops. Its length is `144.933334` (straight-line separation `138.623`), and it is unique. The flag takes character `i mod 6` from stop `i`, zero-based, including the start and destination. This sample includes phrases such as “Delaunay triangulation,” “Dijkstra,” and “Voronoi graphs.”

This short solver parses the map and prints the flightpath code:

```python
import heapq, math, re, zipfile

start, goal = "S0jRxc", "yRJyDb"
coords, links = {}, {}
with zipfile.ZipFile("map.zip") as zf:
    for name in zf.namelist():
        if name.endswith(".md"):
            node = name.rsplit("/", 1)[-1][:-3]
            text = zf.read(name).decode()
            x, y = map(float, re.search(r"Coords:\s*([0-9.+-]+),\s*([0-9.+-]+)", text).groups())
            coords[node] = (x, y)
            links[node] = re.findall(r"\[\[([^\]]+)\]\]", text)

def dist(a, b):
    return math.dist(coords[a], coords[b])

def h(node):
    return dist(node, goal)

queue, best, prev = [(h(start), 0.0, start)], {start: 0.0}, {}
while queue:
    _, cost, node = heapq.heappop(queue)
    if cost != best[node]:
        continue
    if node == goal:
        break
    for nxt in links[node]:
        new = cost + dist(node, nxt)
        if new < best.get(nxt, float("inf")):
            best[nxt], prev[nxt] = new, node
            heapq.heappush(queue, (new + h(nxt), new, nxt))

path, node = [], goal
while node != start:
    path.append(node)
    node = prev[node]
path.append(start)
path.reverse()
code = "".join(node[i % 6] for i, node in enumerate(path))
print(f"CSSCTF{{{code}}}")
print(f"stops={len(path)} time={best[goal]:.6f}")
```

## Flag

`CSSCTF{STARmaPdElAUNaYTriaNGulATioNDIjKStrAVoRonoiGrAPHSdetERmiNaNTcolineaRALGOrITHmSLeEandsCHAcHTERTANgEnTSmErGECirCuMcIrcLEcOnVEXhuLLgeOMeTRy}`
