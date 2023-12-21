from utils import Grid, Neighbours, Coord

REFLECT = {
    ("R", b"/"): "U",
    ("U", b"/"): "R",
    ("L", b"/"): "D",
    ("D", b"/"): "L",
    ("R", b"\\"): "D",
    ("U", b"\\"): "L",
    ("L", b"\\"): "U",
    ("D", b"\\"): "R",
}
DPAIRS = {
    "U": "V",
    "D": "V",
    "L": "H",
    "R": "H",
}

def beam_path(c, d, pathlen, visited):
    if visited is None:
        visited = set()

    while True:
        visited.add((c, d))

        if (nd := (d, g[c])) in REFLECT:
            d = REFLECT[nd]
        elif g[c] == b"|" and DPAIRS[d] == "H":
            beam_path(c, "U", pathlen, visited)
            d = "D"
        elif g[c] == b"-" and DPAIRS[d] == "V":
            beam_path(c, "L", pathlen, visited)
            d = "R"

        pathlen += 1
        c = c + Neighbours.DIRS[d]
        if c not in g or (c, d) in visited:
            break

    return visited

def lbpath(c, d="R", pathlen=0, visited=None):
    if visited is None:
        visited = set()
    beam_path(c, d, pathlen, visited)
    return len(set(c for c, _ in visited))

g = Grid.load_dense_file("../inputs/input16", dtype="|S1")
xs, ys = g.shape
print(lbpath(Coord(0, ys-1)))

energized = []

for xc in range(xs):
    energized.append(lbpath(Coord(xc, 0), "U"))
    energized.append(lbpath(Coord(xc, ys-1), "D"))
for yc in range(ys):
    energized.append(lbpath(Coord(0, yc), "R"))
    energized.append(lbpath(Coord(xs-1, yc), "L"))

print(max(energized))
