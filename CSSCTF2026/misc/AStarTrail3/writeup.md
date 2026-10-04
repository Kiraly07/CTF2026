---
title: "A Star Trail 3"
ctf: "CSSCTF"
date: 2026-10-01
category: misc
flag_format: "CSSCTF{...}"
---

## Solve

The 25,000 planet records in `map2.zip` still have coordinates but their neighbour lists are `[CORRUPTED]`. In A Star Trail 2, the surviving links matched the Delaunay triangulation of the coordinates exactly, so I used the same route rule here. Build the triangulation with `scipy.spatial.Delaunay`, make each triangle edge a bidirectional hop, and weight it by Euclidean distance.

A* from `iJ2ZcO` to `pJk9vy`, with straight-line distance as the heuristic, gives the unique shortest path: 196 stops (195 hops), length `144.047367`, versus a direct separation of `138.287`. The flag takes character `i mod 6` from stop `i`, zero-based, including the origin. This script rebuilds the graph and prints the flightpath code; it needs NumPy and SciPy.

```python
import heapq, math, re, zipfile
import numpy as np
from scipy.spatial import Delaunay

start, goal = "iJ2ZcO", "pJk9vy"
ids, points = [], []
with zipfile.ZipFile("map2.zip") as zf:
    for name in zf.namelist():
        if name.endswith(".md"):
            ids.append(name.rsplit("/", 1)[-1][:-3])
            text = zf.read(name).decode()
            x, y = map(float, re.search(r"Coords:\s*([0-9.+-]+),\s*([0-9.+-]+)", text).groups())
            points.append((x, y))

index = {node: i for i, node in enumerate(ids)}
adj = [set() for _ in ids]
for tri in Delaunay(np.asarray(points)).simplices:
    for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
        adj[int(a)].add(int(b))
        adj[int(b)].add(int(a))

def dist(a, b):
    return math.dist(points[a], points[b])

gi = index[goal]
def heuristic(node):
    return dist(node, gi)

si = index[start]
queue, best, prev = [(heuristic(si), 0.0, si)], {si: 0.0}, {}
while queue:
    _, cost, node = heapq.heappop(queue)
    if cost != best[node]:
        continue
    if node == gi:
        break
    for nxt in adj[node]:
        new = cost + dist(node, nxt)
        if new < best.get(nxt, float("inf")):
            best[nxt], prev[nxt] = new, node
            heapq.heappush(queue, (new + heuristic(nxt), new, nxt))

path, node = [], gi
while node != si:
    path.append(ids[node])
    node = prev[node]
path.append(start)
path.reverse()
code = "".join(node[i % 6] for i, node in enumerate(path))
print(f"CSSCTF{{{code}}}")
print(f"stops={len(path)} time={best[gi]:.6f} edges={sum(map(len, adj)) // 2}")
```

## Flag

`CSSCTF{itr6G8jMTXbOjCmClmMElZxQLqSXqnf53z1Z73liVas3ypn5CJZ4ZGlqZo6Fkc2onoJ6vx5SLfqqEyBotfjpxskQknpUgK9VMfBsFqzc0iEHDbMvv1hwXAo4U1NaimtTt9esb6mskMdUkbgBAjg3TTS1UeTSvf7LFZR0Vxf8KOgkzxHmvO0ifOFaVnwNgwUqpeo9}`
