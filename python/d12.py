import tqdm.auto as tqdm
from itertools import chain, repeat

imap = {".": 0, "#": 1, "?": 2}
rmap = {0: ".", 1: "#", 2: "?"}
springs = []
with open("../inputs/input12") as f:
    for line in f:
        layout, arrangement = line.strip().split()
        arrangement = ".".join("#"*int(x) for x in arrangement.split(","))
        springs.append((layout, arrangement))

cache = {}
def count(layout: str, target: str, prev: str = ".", level=0, debug=False):
    if (layout, target, prev) in cache:
        return cache[(layout, target, prev)]

    if sum(c in ("?", "#") for c in layout) < sum(c == "#" for c in target):
        return 0
    if sum(c == "#" for c in layout) > sum(c == "#" for c in target):
        return 0
    if len(target) == 0:
        return 1

    if layout[0] == target[0]:
        return count(layout[1:], target[1:], layout[0], level+1)
    elif (prev, layout[0], target[0]) == (".", ".", "#"):
        return count(layout[1:], target, layout[0], level+1)
    elif (prev, layout[0], target[0]) == ("#", ".", "#"):
        return 0
    elif (layout[0], target[0]) == ("#", "."):
        return 0
    elif (layout[0], target[0]) == ("#", "#"):
        return count(layout[1:], target[1:], layout[0], level+1)
    elif layout[0] == "?":
        p1 = count("." + layout[1:], target, prev, level+1)
        p2 = count("#" + layout[1:], target, prev, level+1)
        if debug:
            print(" "*level, level, p1, p2)
        cache[(layout, target, prev)] = p1 + p2
        return p1 + p2
    raise RuntimeError(f"Unexpected config: ({layout}, {target})")

counts_p1 = []
for config in tqdm.tqdm(springs):
    counts_p1.append(count(*config))
print(sum(counts_p1))

counts_p2 = []
for layout, target in tqdm.tqdm(springs):
    layout = "?".join([layout]*5)
    target = ".".join([target]*5)
    counts_p2.append(count(layout, target))
print(sum(counts_p2))

with open("../inputs/output12", "w") as f, open("../inputs/input12") as i:
    for l, c_p1, c_p2 in zip(i, counts_p1, counts_p2):
        f.write(f"{l.strip()} {c_p1} {c_p2}\n")
