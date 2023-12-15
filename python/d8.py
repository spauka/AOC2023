from typing import NamedTuple
from numpy import lcm, int64
import re

class Node(NamedTuple):
    name: str
    L: str
    R: str

nodes = {}
with open("../inputs/input8") as f:
    instructions = f.readline().strip()
    f.readline()
    for line in f:
        node, left, right = re.match(r"(.+) = \((.+), (.+)\)", line).groups()
        nodes[node] = Node(node, left, right)

cnode = nodes["AAA"]
step = 0
ilen = len(instructions)
while cnode.name != "ZZZ":
    cnode = nodes[getattr(cnode, instructions[step%ilen])]
    step += 1
print(step)

cnodes = [node for node in nodes.values() if node.name[-1] == "A"]
multiples = {}
step = 0
while len(multiples) != len(cnodes):
    cinstr = instructions[step%ilen]
    step += 1
    for i in range(len(cnodes)):
        cnodes[i] = nodes[getattr(cnodes[i], cinstr)]
        if cnodes[i].name[-1] == "Z" and i not in multiples:
            multiples[i] = step
print(lcm.reduce(list(multiples.values()), dtype=int64))