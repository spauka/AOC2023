import re
import numpy as np
from utils import Coord, Neighbours

instrs = []
large_instrs = []
dir_map = {"0": "R", "1": "D", "2": "L", "3": "U"}
with open("../inputs/input18") as f:
    for line in f:
        d, c, lc, ld = re.match(r"([RDLU]) ([0-9]+) \(#([0-9a-f]{5})([0-3])\)", line).groups()
        instrs.append((d, int(c)))
        large_instrs.append((dir_map[ld], int(lc, 16)))

def find_vertices(instrs):
    vertices = np.zeros((len(instrs)+1, 2), dtype=np.int64)
    cloc = Coord(0, 0)
    for i, (d, c) in enumerate(instrs):
        cloc = cloc + (Neighbours.DIRS[d] * c)
        vertices[i+1,:] = cloc
    return vertices

def calculate_area(vertices):
    perimeter = np.sum(np.sqrt((vertices[:-1,1] - vertices[1:,1])**2 + (vertices[:-1,0] - vertices[1:,0])**2), dtype=np.int64)
    internal_area = np.abs(np.sum((vertices[:-1,1] + vertices[1:,1]) * (vertices[:-1,0] - vertices[1:,0])))//2
    return internal_area + perimeter//2 + 1

print(calculate_area(find_vertices(instrs)))
print(calculate_area(find_vertices(large_instrs)))
