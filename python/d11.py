import numpy as np
from itertools import combinations
from utils import Grid

g = Grid.load_dense_file("../inputs/input11", conv_char=True, dtype=np.uint8)
xblanks = np.where(np.all(g.grid == ord("."), axis=0))[0] # Horizontal Blanks
yblanks = np.where(np.all(g.grid == ord("."), axis=1))[0] # Vertical Blanks
galaxies = np.array(np.where(g.grid == ord("#"))).T

def calc_distances(expand=1):
    distance = 0
    for g1, g2 in combinations(range(galaxies.shape[0]), 2):
        xmin, ymin = np.min([galaxies[g1,:], galaxies[g2,:]], axis=0)
        xmax, ymax = np.max([galaxies[g1,:], galaxies[g2,:]], axis=0)
        nxblanks = np.sum(np.logical_and(yblanks > xmin, yblanks < xmax))
        nyblanks = np.sum(np.logical_and(xblanks > ymin, xblanks < ymax))
        dist = np.sum(np.abs(galaxies[g1,:] - galaxies[g2,:]))
        distance += dist + expand*(nxblanks + nyblanks)
    return distance

print(calc_distances(1))
print(calc_distances(1_000_000 - 1))