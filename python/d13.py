import numpy as np

def check_symmetry(g, nmatches=0):
    g_size = g.shape[0]
    for i in range(1, g_size):
        start = 0
        if i > g_size//2:
            start = i - (g_size - i)
        mismatches = np.sum(g[start:i,:][::-1,:] != g[i:2*i,:])
        if mismatches == nmatches:
            return i
    return None

all_grids = []
with open("../inputs/input13") as f:
    g_array = []
    for line in f:
        if not line.strip():
            all_grids.append(np.array(g_array, dtype=np.uint8))
            g_array.clear()
            continue
        g_array.append([ord(c) for c in line.strip()])
all_grids.append(np.array(g_array, dtype=np.uint8))

symmetries = []
for grid in all_grids:
    if (sym := check_symmetry(grid)):
        symmetries.append(sym*100)
        continue
    symmetries.append(check_symmetry(grid.T))
print(sum(symmetries))

symmetries = []
for grid in all_grids:
    if (sym := check_symmetry(grid, 1)):
        symmetries.append(sym*100)
        continue
    symmetries.append(check_symmetry(grid.T, 1))
print(sum(symmetries))
