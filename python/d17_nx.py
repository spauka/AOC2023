#%%
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from utils import Grid, Coord

DIRS = {
    "R": Coord(1, 0), # R
    "L": Coord(-1, 0), # L
    "U": Coord(0, 1), # U
    "D": Coord(0, -1) # D
}
NDIRS = {
    "R": ("U", "D"),
    "L": ("U", "D"),
    "U": ("L", "R"),
    "D": ("L", "R")
}

#def construct_graph(weights, start, dest, min_steps=1, max_steps=3):
#    g = nx.DiGraph()
#    sn = (start[0], start[1], 0, 0)
#    en = (dest[0], dest[1], 0, 0)
#
#    for dir, m in DIRS.items():
#        for step in range(max_steps+1):
#            for x in range(weights.shape[0]):
#                for y in range(weights.shape[1]):
#                    sx, sy = m + (x, y)
#                    if (sx, sy) in weights:
#                        g.add_edge((x, y, step, dir), (sx, sy, step+1, dir), weight=weights[sx, sy])
#                    if step >= min_steps:
#                        for nd in NDIRS[dir]:
#                            ns = DIRS[nd] + (x, y)
#                            if ns in weights:
#                                sx, sy = ns
#                                g.add_edge((x, y, step, dir), (sx, sy, 1, nd), weight=weights[sx, sy])
#
#    for dir, m in DIRS.items():
#        ns = start + m
#        if ns in weights:
#            sx, sy = ns
#            g.add_edge(sn, (sx, sy, 1, dir), weight=weights[sx, sy])
#        for step in range(max_steps+1):
#            g.add_edge((dest[0], dest[1], step, dir), en, weight=0)
#
#    return g, sn, en

def construct_better_graph(weights, start, dest, min_steps=1, max_steps=3):
    g = nx.DiGraph()
    sn = (start[0], start[1], 0)
    en = (dest[0], dest[1], 0)

    for dir, m in DIRS.items():
        for step in range(min_steps, max_steps+1):
            gstart, gstop = m*-step, m*-step + weights.shape
            for x in range(max(gstart[0], 0), min(gstop[0], weights.shape[0])):
                for y in range(max(gstart[1], 0), min(gstop[1], weights.shape[1])):
                    sx, sy = m*step + (x, y)
                    for pd in NDIRS[dir]:
                        # Calculate weight of edge
                        scx, scy = m + (x, y)
                        xstart, xstop = min(scx, sx), max(scx, sx)
                        ystart, ystop = min(scy, sy), max(scy, sy)
                        weight = np.sum(weights[xstart:xstop+1, ystart:ystop+1])
                        g.add_edge((x, y, pd), (sx, sy, dir), weight=weight)


    for dir in DIRS:
        g.add_edge(sn, (start[0], start[1], dir), weight=0)
        g.add_edge((dest[0], dest[1], dir), en, weight=0)

    return g, sn, en

debug = True
weights = Grid.load_dense_file("../inputs/input17s", dtype=np.int16)
start = Coord(0, weights.shape[1]-1)
dest = Coord(weights.shape[0]-1, 0)

#g, sn, en = construct_graph(weights, start, dest)
#if debug:
#    sp = nx.shortest_path(g, sn, en, "weight")
#    pg = np.zeros_like(weights.grid, dtype=np.int8)
#    for x, y, _, _ in sp:
#        pg[x, y] = 1
#    fig, ax = plt.subplots()
#    ax.pcolormesh(pg.T)
#print(nx.shortest_path_length(g, sn, en, "weight"))

g, sn, en = construct_better_graph(weights, start, dest)
print(g)
if debug:
    sp = nx.shortest_path(g, sn, en, "weight")
    pg = np.zeros_like(weights.grid, dtype=np.int8)
    for x, y, _ in sp:
        pg[x, y] = 1
    fig, ax = plt.subplots()
    ax.pcolormesh(weights.grid.T)
    for c in weights.iter_coord():
        ax.annotate(str(weights[c]), c+(0.25, 0.25), color="tab:red")
    for sc, ec in zip(sp[:-1], sp[1:]):
        ax.annotate("", xy=(ec[0]+0.5, ec[1]+0.5), xytext=(sc[0]+0.5, sc[1]+0.5), arrowprops=dict(arrowstyle="->", color="tab:orange"))
print(nx.shortest_path_length(g, sn, en, "weight"))

#g, sn, en = construct_graph(weights, start, dest, 4, 10)
#if debug:
#    sp = nx.shortest_path(g, sn, en, "weight")
#    pg = np.zeros_like(weights.grid, dtype=np.int8)
#    for x, y, _, _ in sp:
#        pg[x, y] = 1
#    fig, ax = plt.subplots()
#    ax.pcolormesh(pg.T)
#print(nx.shortest_path_length(g, sn, en, "weight"))

g, sn, en = construct_better_graph(weights, start, dest, 4, 10)
print(g)
if debug:
    sp = nx.shortest_path(g, sn, en, "weight")
    pg = np.zeros_like(weights.grid, dtype=np.int8)
    for x, y, _ in sp:
        pg[x, y] = 1
    fig, ax = plt.subplots()
    ax.pcolormesh(weights.grid.T)
    for c in weights.iter_coord():
        ax.annotate(str(weights[c]), c+(0.25, 0.25), color="tab:red")
    for sc, ec in zip(sp[:-1], sp[1:]):
        ax.annotate("", xy=(ec[0]+0.5, ec[1]+0.5), xytext=(sc[0]+0.5, sc[1]+0.5), arrowprops=dict(arrowstyle="->", color="tab:orange"))
print(nx.shortest_path_length(g, sn, en, "weight"))
# %%
