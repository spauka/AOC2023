import numpy as np
from utils import read_numbers

minc, maxc = np.ones(3, np.int64)*1_000_000, np.zeros(3, np.int64)
cubes = []
with open("../inputs/input22") as f:
    for line in f:
        cube = np.array(read_numbers(line), dtype=np.int64).reshape((2, 3))
        minc, maxc = np.min(np.stack((minc, cube[0,:])), axis=0), np.max(np.stack((maxc, cube[1,:])), axis=0)
        cubes.append(cube)
g = np.zeros(maxc+1, dtype=np.int64)

def cube_slice(cube):
    return tuple(slice(s, e+1) for s, e in zip(*cube))

def will_fall(cube, already_fallen):
    return set(i for i in supports[cube] if len(supported_by[i] - {cube} - already_fallen) == 0)

# Place cubes in grid, sorted by their starting z dimension
cubes.sort(key=lambda x: (x[0,2], x[0,0], x[0,1])) # Sort z, x, y
supports = {}
supported_by = {}
for i, cube in enumerate(cubes):
    cs = cube_slice(cube)
    below = g[cs[0], cs[1], :cube[0][2]]
    blocked_below = np.stack(np.where(below > 0))
    if blocked_below.size == 0:
        cube[:, 2] = cube[:, 2] - cube[0, 2]
    else:
        max_z = np.max(blocked_below[2,:])
        cube[:, 2] = cube[:, 2] - (cube[0, 2] - max_z - 1)

    cs = cube_slice(cube)
    g[cs] = i+1
    cubes[i] = cube

for i, cube in enumerate(cubes):
    # Calculate the new cube slice
    cs = cube_slice(cube)
    directly_above = cs[:-1] + (cube[1, 2] + 1,)
    directly_below = cs[:-1] + (cube[0, 2] - 1,)
    supports[i+1] = set(np.ravel(g[directly_above])) - {0}
    supported_by[i+1] = set(np.ravel(g[directly_below])) - {0}

disintegratable = []
for i in range(1, 1+len(cubes)):
    if len(will_fall(i, set())) == 0:
        disintegratable.append(i+1)
print(len(disintegratable))

num_will_fall = []
for i in range(1, 1+len(cubes)):
    falling_bricks = set()
    next_to_fall = will_fall(i, falling_bricks)
    while next_to_fall:
        next_brick = next_to_fall.pop()
        falling_bricks.add(next_brick)
        next_to_fall |= will_fall(next_brick, falling_bricks) - falling_bricks
    num_will_fall.append(len(falling_bricks))
print(sum(num_will_fall))
