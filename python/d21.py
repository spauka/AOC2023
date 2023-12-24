import numpy as np
from pprint import pprint
import tqdm.auto as tqdm
from utils import Grid, Coord, Neighbours

g = Grid.load_dense_file("../inputs/input21s", dtype="|S1")
start = Coord(*np.ravel(np.where(g.grid == b"S")))
g[start] = b"."

#xs, ys = g.shape
#n = 3
#g.grid = np.tile(g.grid, (2*n + 1, 2*n + 1))
#start = start + (xs*n, ys*n)

reachable = [set([start])]
eog = False
debug = True
for step in tqdm.trange(128, disable=debug):
    next_reachable = set()
    previous = reachable[-1]
    for coord in previous:
        for n in Neighbours.STRT.values():
            actual_coord = coord + n
            grid_coord = Coord(c%s for c, s in zip(coord + n, g.shape))
            if g[grid_coord] == b".":
                next_reachable.add(actual_coord)
            if not eog and actual_coord != grid_coord:
                print(f"Outside grid at step: {step}")
                eog = True
    reachable.append(next_reachable)

    if debug:
        print(f"Iter: {step}")
        pg = g.copy()
        for c in next_reachable:
            if c in g:
                pg[c] = "O"
        print(f"  Count: {np.sum(pg.grid == b'O')}")
print([len(r) for r in reachable])
