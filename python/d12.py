import tqdm.auto as tqdm

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
        # Too few broken springs
        return 0
    elif sum(c == "#" for c in layout) > sum(c == "#" for c in target):
        # Too many broken springs
        return 0
    elif len(target) == 0:
        # No more matching to do!
        return 1

    if layout[0] == target[0]: # If layout, target are same, consume next tokens
        return count(layout[1:], target[1:], layout[0], level+1)
    elif (prev, layout[0], target[0]) == (".", ".", "#"): # If we've seen a ., consume as many as we need from layout
        return count(layout[1:], target, layout[0], level+1)
    elif (prev, layout[0], target[0]) == ("#", ".", "#"): # If we see a ., but are in the middle of a run in target, fail
        return 0
    elif (layout[0], target[0]) == ("#", "."): # Fail if current run of # is too long
        return 0
    elif layout[0] == "?": # Count alternatives
        p1 = count("." + layout[1:], target, prev, level+1)
        p2 = count("#" + layout[1:], target, prev, level+1)
        if debug:
            print(" "*level, level, p1, p2)
        cache[(layout, target, prev)] = p1 + p2
        return p1 + p2
    raise RuntimeError(f"Unexpected config: ({layout}, {target})") # Shouldn't get here :O

counts_p1 = []
for config in tqdm.tqdm(springs):
    counts_p1.append(count(*config))
print(sum(counts_p1))

counts_p2 = []
for layout, target in tqdm.tqdm(springs):
    counts_p2.append(count("?".join([layout]*5), ".".join([target]*5)))
print(sum(counts_p2))

with open("../inputs/output12", "w") as f, open("../inputs/input12") as i:
    for l, c_p1, c_p2 in zip(i, counts_p1, counts_p2):
        f.write(f"{l.strip()} {c_p1} {c_p2}\n")
