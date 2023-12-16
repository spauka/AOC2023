import numpy as np
from collections import deque
from utils import Grid, Coord, Neighbours
from itertools import product

neighbours = {
    ord("|"): ("U", "D"),
    ord("-"): ("L", "R"),
    ord("L"): ("R", "U"),
    ord("J"): ("L", "U"),
    ord("7"): ("L", "D"),
    ord("F"): ("R", "D"),
    ord("."): (),
}

def calc_distances(g, start):
    distances = {start: 0}
    to_visit = deque()
    # Figure out what the starting tile is (for p2)
    dmap = []
    for n in g.n[start].coords:
        for dir in neighbours[g[n]]:
            if n + Neighbours.DIRS[dir] == start:
                dmap.append(dir)
                to_visit.append((n, 1))
    dmap = tuple(dmap)
    for pipe, n in neighbours.items():
        if n == dmap:
            g[start] = pipe

    # Visit each neighbour while we can
    while to_visit:
        coord, distance = to_visit.popleft()
        if coord in distances:
            continue
        distances[coord] = distance
        for dir in neighbours[g[coord]]:
            next_coord = coord + Neighbours.DIRS[dir]
            if next_coord not in distances:
                to_visit.append((next_coord, distance+1))

    return distances

def check_enclosed(g, distances):
    parities = np.zeros_like(g.grid)
    corners = tuple(ord(c) for c in ("L", "F", "J", "7"))
    for y in range(g.shape[1]):
        parity = 0
        prev = 0
        for x in range(g.shape[0]):
            if (x, y) not in distances:
                pass
            elif (prev, g[x, y]) in ((ord("L"), ord("7")), (ord("7"), ord("L"))):
                parity += 1
                prev = 0
            elif (prev, g[x, y]) in ((ord("F"), ord("J")), (ord("J"), ord("F"))):
                parity += 1
                prev = 0
            elif (prev, g[x, y]) in ((ord("L"), ord("J")), (ord("J"), ord("L"))):
                prev = 0
            elif (prev, g[x, y]) in ((ord("F"), ord("7")), (ord("7"), ord("F"))):
                prev = 0
            elif g[x, y] in corners:
                prev = g[x, y]
            elif g[x, y] == ord("|"):
                prev = 0
                parity += 1
            parities[x, y] = parity
    return parities

def count_enclosed(g, loop, parities):
    count = 0
    for coord in product(range(g.shape[0]), range(g.shape[1])):
        if coord in loop:
            continue
        if parities[coord]%2 == 1:
            count += 1
    return count

g = Grid.load_dense_file("../inputs/input10", dtype=np.int8, conv_char=True)
start = Coord(*(x[0] for x in np.where(g.grid == ord("S"))))

distances = calc_distances(g, start)
parities = check_enclosed(g, distances)
print(max(distances.values()))
print(count_enclosed(g, distances, parities))
