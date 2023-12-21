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
    to_visit = [(dist(start, dest), 0, start, "E", 0)]
    visited = {}
    ccoord = start

    with tqdm.tqdm() as pbar:
        while to_visit:
            pbar.update()
            _, heat_loss, ccoord, last_d, n_d = heappop(to_visit)
            if (ccoord, last_d, n_d) in visited:
                assert visited[(ccoord, last_d, n_d)] <= heat_loss
                continue
            visited[(ccoord, last_d, n_d)] = heat_loss

            nb = g.n[ccoord]
            for d, n in zip(nb.valid_dirs, nb.coords):
                # Check we're not going in the same direction for too long
                if d == backwards[last_d]: # Can't reverse
                    continue
                if n_d == max_straight and d == last_d:
                    continue
                # Only try to turn if we can
                if n_d < min_straight and d != last_d:
                    continue

                if d == last_d:
                    nn_d = n_d + 1
                else:
                    nn_d = 1
                next_cost = heat_loss+g[n]

                if (n, d, nn_d) not in visited or next_cost < visited[(n, d, nn_d)]:
                    heappush(to_visit, (dist(n, dest)+next_cost, next_cost, n, d, nn_d))

    return min(loss for (ccoord, _, _), loss in visited.items() if ccoord == dest)

g = Grid.load_dense_file("../inputs/input17", dtype=np.int16)
start = Coord(0, g.shape[1]-1)
dest = Coord(g.shape[0]-1, 0)
print(minimal_loss(g, start, dest))

print(minimal_loss(g, start, dest, 4, 10))