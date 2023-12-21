import numpy as np
from heapq import heappush, heappop
import tqdm.auto as tqdm
from utils import Grid, Coord

backwards = {
    "N": "S",
    "S": "N",
    "E": "W",
    "W": "E"
}

def dist(coord, dest):
    return np.sum(np.abs(coord - dest))

def minimal_loss(g, start, dest, min_straight=1, max_straight=3):
    to_visit = [(dist(start, dest), 0, start, ())]
    visited = {}
    ccoord = start

    with tqdm.tqdm() as pbar:
        while to_visit:
            pbar.update()
            _, heat_loss, ccoord, last_n = heappop(to_visit)
            if (ccoord, last_n) in visited:
                assert visited[(ccoord, last_n)] <= heat_loss
                continue
            visited[(ccoord, last_n)] = heat_loss

            nb = g.n[ccoord]
            for d, n in zip(nb.valid_dirs, nb.coords):
                # Check we're not going in the same direction for too long
                if last_n and d == backwards[last_n[-1]]: # Can't reverse
                    continue
                if len(last_n) == max_straight and all(ld == d for ld in last_n):
                    continue
                # Only try to turn if we can
                if last_n and d != last_n[-1] and not all(last_n[-1] == ld for ld in last_n[-min_straight:]):
                    continue

                if len(last_n) == max_straight:
                    next_path = last_n[1:] + (d,)
                else:
                    next_path = last_n + (d,)
                next_cost = heat_loss+g[n]

                if (n, next_path) not in visited or next_cost < visited[(n, next_path)]:
                    heappush(to_visit, (dist(n, dest)+next_cost, next_cost, n, next_path))

    return min(loss for (ccoord, _), loss in visited.items() if ccoord == dest)

g = Grid.load_dense_file("../inputs/input17", dtype=np.int16)
start = Coord(0, g.shape[1]-1)
dest = Coord(g.shape[0]-1, 0)
print(minimal_loss(g, start, dest))

print(minimal_loss(g, start, dest, 4, 10))