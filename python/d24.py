import numpy as np
import sympy
from itertools import combinations
from utils import read_numbers

hailstones = []
with open("../inputs/input24") as f:
    for line in f:
        hailstone = np.fromiter(read_numbers(line, allow_negative=True), dtype=np.int64).reshape((2, 3)).T
        hailstones.append(hailstone)

min_loc = 200000000000000
max_loc = 400000000000000

# Calculate intersection times
count = 0
for i, j in combinations(range(len(hailstones)), 2):
    x1, x2 = hailstones[i][:2,:], hailstones[j][:2,:]
    A = np.column_stack((-x1[:,1], x2[:,1]))
    C = x1[:,0] - x2[:,0]
    try:
        X = np.linalg.solve(A, C)
        loc = x1[:,0] + X[0]*x1[:,1]
        if np.all(np.logical_and(X > 0, loc >= min_loc, loc <= max_loc)):
            count += 1
    except np.linalg.LinAlgError:
        print(f"Pair {i}-{j} parallel")
        pass # Parallel hailstones
print(count)

def line_intersect_eqns(h, tvar):
    posns, vels = sympy.symbols('a,b,c'), sympy.symbols('i,j,k')
    eqns = []
    for p, v, (hp, hv) in zip(posns, vels,h):
        eqns.append(p + v*tvar - hp - hv*tvar)
    return eqns
eqns = []
for h, tvar in zip(hailstones, sympy.symbols('t,r,s')):
    eqns.extend(line_intersect_eqns(h, tvar))
soln = sympy.solve(eqns, sympy.symbols("a,b,c,i,j,k,t,r,s"))[0]
print(soln)
print(sum(soln[:3]))
