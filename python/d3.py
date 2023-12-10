import re
from functools import reduce
from operator import add
from utils import Grid

g = Grid.load_dense_file("../inputs/input3", incl_diag=True, dtype=str)
numbers = [list(re.finditer("\\d+", "".join(g[:, y]))) for y in range(g.shape[1])]

parts = 0
for y in range(g.shape[1]):
    for num in numbers[y]:
        neighbours = set(reduce(add, (g.n[x, y].coords for x in range(*num.span()))))
        if re.findall("[^\d.]", "".join(g[n] for n in neighbours)):
            parts += int(num.group())

gears = 0
for y in range(g.shape[1]):
    for gear in re.finditer("\\*", "".join(g[:, y])):
        neighbours = set()
        for n in g.n[gear.span()[0], y].coords:
            for number in numbers[n[1]]:
                if n[0] in range(*number.span()):
                    neighbours.add(number)
        if len(neighbours) == 2:
            gears += int(neighbours.pop().group())*int(neighbours.pop().group())

print(parts, gears)
