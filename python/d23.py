import numpy as np
from pprint import pprint
from typing import Optional
from collections import deque, defaultdict
from utils import Grid, Coord, Neighbours

slopes = tuple(bytes([b]) for b in b"><^v#")
valid_moves = {
    b".": ("U", "D", "L", "R"),
    b">": ("R",),
    b"<": ("L",),
    b"^": ("U",),
    b"v": ("D",)
}

def find_nodes(g: Grid):
    nodes = set()
    for c in g.iter_coord():
        if g[c] != b".":
            continue
        if any(n in slopes[:-1] for n in g.n[c]) and all(n in slopes for n in g.n[c]):
            nodes.add(c)
    return nodes

def search(g: Grid, start: Coord, ignore_slopes: bool=False, nodes: set[Coord]=set(), visited: Optional[dict[Coord, int]]=None):
    if visited is None:
        visited = {}
    to_visit = deque([(start, 0, set(start))])
    while to_visit:
        cnode, dist, path = to_visit.pop()
        visited[cnode] = dist
        if ignore_slopes:
            moves = tuple("DLRU")
        else:
            moves = valid_moves[g[cnode]]
        for move in moves:
            n = cnode + Neighbours.DIRS[move]
            if n in g and g[n] != b"#":
                if n in path:
                    continue
                if n in nodes:
                    visited[n] = dist+1
                    continue
                elif (n not in visited) or (n in visited and dist+1 > visited[n]):
                    to_visit.append((n, dist+1, path|set([n])))
    
    return visited

def longest_path(connections, start):
    visited = {}
    to_visit = deque([(start, 0, set(start))])
    while to_visit:
        cnode, dist, path = to_visit.pop()
        if cnode not in visited or (cnode in visited and dist > visited[cnode]):
            visited[cnode] = dist
        for n in connections[cnode]:
            if n in path:
                continue
            next_dist = dist + connections[cnode][n]
            to_visit.append((n, next_dist, path|set([n])))
    return visited

def connect_nodes(g: Grid, nodes: set[Coord], ignore_slopes=False):
    visited = {}
    neighbours: dict[Coord, dict[Coord, int]] = defaultdict(dict)
    for node in nodes:
        if not ignore_slopes: # We have to reset paths since they are no longer symmetric
            visited = {}
        visited = search(g, node, ignore_slopes, nodes, visited)
        for nnode in nodes:
            if node != nnode and (node, nnode) not in neighbours and nnode in visited:
                neighbours[node][nnode] = visited[nnode]
                if ignore_slopes:
                    neighbours[nnode][node] = visited[nnode]
            visited.pop(nnode, None)
    return neighbours

g = Grid.load_dense_file("../inputs/input23", dtype="|S1")
start = Coord(1, g.shape[1]-1)
end = Coord(g.shape[0]-2, 0)
nodes = find_nodes(g)
nodes.update([start, end])

connections = connect_nodes(g, nodes, False)
visited = longest_path(connections, start)
print(visited[end])

connections = connect_nodes(g, nodes, True)
visited = longest_path(connections, start)
print(visited[end])
