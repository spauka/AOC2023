import numpy as np
import hashlib
from utils import Grid

g = Grid.load_dense_file("../inputs/input14", dtype="|S1")

def roll_north(g):
    for y in range(1, g.shape[1]):
        boulders = np.where(g[:,-y-1] == b"O")[0]
        for boulder in boulders:
            above = np.where(g[boulder, -y:] != b".")[0]
            if above.size == 0:
                g[boulder, -y-1] = b"."
                g[boulder, -1] = b"O"
            elif (move := min(above)) > 0:
                g[boulder, -y-1] = b"."
                g[boulder, -(y-move)-1] = b"O"

def roll_south(g):
    for y in range(1, g.shape[1]):
        boulders = np.where(g[:,y] == b"O")[0]
        for boulder in boulders:
            below = np.where(g[boulder, :y] != b".")[0]
            if below.size == 0:
                g[boulder, y] = b"."
                g[boulder, 0] = b"O"
            elif (move := max(below)) < y-1:
                g[boulder, y] = b"."
                g[boulder, move+1] = b"O"

def roll_west(g):
    for x in range(1, g.shape[0]):
        boulders = np.where(g[x,:] == b"O")[0]
        for boulder in boulders:
            left = np.where(g[:x, boulder] != b".")[0]
            if left.size == 0:
                g[x, boulder] = b"."
                g[0, boulder] = b"O"
            elif (move := max(left)) < x-1:
                g[x, boulder] = b"."
                g[move+1, boulder] = b"O"

def roll_east(g):
    for x in range(1, g.shape[0]):
        boulders = np.where(g[-x-1,:] == b"O")[0]
        for boulder in boulders:
            right = np.where(g[-x:, boulder] != b".")[0]
            if right.size == 0:
                g[-x-1, boulder] = b"."
                g[-1, boulder] = b"O"
            elif (move := min(right)) > 0:
                g[-x-1, boulder] = b"."
                g[-(x-move)-1, boulder] = b"O"

def score_grid(g):
    score = 0
    for y in range(g.shape[1]):
        score += np.sum(g[:,y] == b"O") * (y+1)
    return score

def print_grid(g):
    for y in range(g.shape[1]):
        print("".join(b.decode("ascii") for b in g[:,-y-1]))
    print()

repeat = {}
scores = []
target = 1000000000
for i in range(target):
    roll_north(g)
    if i == 0:
        print(score_grid(g))
    roll_west(g)
    roll_south(g)
    roll_east(g)
    if (h := hashlib.sha256(g.grid.data).digest()) in repeat:
        break
    repeat[h] = i
    scores.append(score_grid(g))

offset = repeat[h]
cycle = i - offset
target_iteration = (target - offset) % cycle
print(scores[offset + target_iteration - 1])
print(f"Cycle length: {cycle}")
#roll_south(g)
#print("".join(b.decode("ascii") for b in g[:,0]))
#print(g)
