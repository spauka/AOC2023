#%%
import networkx as nx
from functools import reduce
from operator import mul

debug = False
with open("../inputs/input25") as f:
    inp = f.read().replace(":", "").splitlines()
    g = nx.parse_adjlist(inp)

cut = nx.minimum_edge_cut(g)
if debug:
    for c in cut:
        g.edges[c]["color"] = "tab:red"
    nx.draw(g, edge_color=[e.get("color", "black") for e in g.edges.values()])

for c in cut:
    g.remove_edge(*c)
components = [sorted(n) for n in nx.connected_components(g)]
print(reduce(mul, (len(c) for c in components)))
