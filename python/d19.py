import re
from functools import reduce
from operator import mul

rules = {}
parts = []

with open("../inputs/input19") as f:
    for line in f:
        if not line.strip():
            break
        name, conditions = re.match(r"([a-z]+){([a-zA-Z0-9<>,:]+)}", line).groups()
        conditions = [c.split(":") for c in conditions.split(",")]
        for condition in conditions:
            if len(condition) == 2:
                cat, cond, val = condition[0][0], condition[0][1], condition[0][2:]
                if cond == "<":
                    condition[0] = (cat, range(1, int(val)))
                else:
                    condition[0] = (cat, range(int(val)+1, 4001))
        rules[name] = conditions
    for line in f:
        parts.append({(y := x.split("="))[0]: int(y[1]) for x in line.strip()[1:-1].split(",")})

def remove_reduntant():
    all_same = {}
    for rule in rules:
        first_dest = rules[rule][0][-1]
        if all(dest[-1] == first_dest for dest in rules[rule]):
            all_same[rule] = first_dest
    if all_same:
        for rule in all_same:
            del rules[rule]
        for rule in rules:
            for cond in rules[rule]:
                if cond[-1] in all_same:
                    cond[-1] = all_same[cond[-1]]
        return True
    return False

def remove_dead_checks():
    removed = False
    for rule in rules:
        last_dest = rules[rule][-1][0]
        for i, cond in enumerate(rules[rule][::-1]):
            if cond[-1] != last_dest:
                break
        else:
            continue
        if i > 1:
            rules[rule][-i] = rules[rule][-1]
            rules[rule] = rules[rule][:-i+1]
            removed = True
    return removed

def remove_unreachable():
    all_rules = set(rules)
    visited = {"in", "A", "R"}
    to_visit = set(d[-1] for d in rules["in"] if d[-1] not in visited)
    while to_visit:
        cnode = to_visit.pop()
        visited.add(cnode)
        nnodes = set(d[-1] for d in rules[cnode]) - visited
        to_visit |= nnodes
    if (unvisited := (all_rules - visited)):
        for node in unvisited:
            del rules[node]
        return True
    return False

def collapse_leaves():
    collapsed = False
    for rule in rules:
        if rules[rule][-1][0] not in ("A", "R"):
            rules[rule] = rules[rule][:-1] + rules[rules[rule][-1][0]]
            collapsed = True
    return collapsed

def reduce_range(r1, r2):
    new_r1 = range(max(r1.start, r2.start), min(r1.stop, r2.stop))
    if r1 in r2:
        new_r1 = r1
        new_r2 = range(0, 0)
    elif r2 in r1 and len(r1) > len(r2):
        raise RuntimeError("Not handling this case. This creates two false ranges")
    elif r2.start <= r1.start:
        new_r1 = range(r1.start, r2.stop)
        new_r2 = range(r2.stop, r1.stop)
    else:
        new_r1 = range(r2.start, r1.stop)
        new_r2 = range(r1.start, r2.start)
    assert len(r1) == len(new_r1) + len(new_r2), f"{r1}, {r2}, {new_r1}, {new_r2}"
    return new_r1, new_r2

def reduce_ranges(crule, part_ranges: dict[str, range], A: list, R: list):
    if any(len(r) == 0 for r in part_ranges.values()):
        return # No valid rules
    if crule == "A":
        A.append(tuple(part_ranges.items()))
        return
    if crule == "R":
        R.append(tuple(part_ranges.items()))
        return

    for cond in rules[crule]:
        if len(cond) == 1:
            return reduce_ranges(cond[0], part_ranges, A, R)
        true_range = part_ranges.copy()
        true_range[cond[0][0]], part_ranges[cond[0][0]] = reduce_range(part_ranges[cond[0][0]], cond[0][1])
        reduce_ranges(cond[1], true_range, A, R)

# Completely pointless optimization step :O
opt = True
while opt:
    opt = collapse_leaves()
    opt = remove_reduntant() or opt
    opt = remove_unreachable() or opt
    opt = remove_dead_checks() or opt

A, R = [], []
for part in parts:
    crule = "in"
    while crule not in ("A", "R"):
        for cond in rules[crule]:
            if len(cond) == 1:
                crule = cond[0]
                break
            if part[cond[0][0]] in cond[0][1]:
                crule = cond[1]
                break
    if crule == "A":
        A.append(part)
    else:
        R.append(part)
print(sum(sum(p.values()) for p in A))

A, R = [], []
part_ranges = {
    "x": range(1, 4001),
    "m": range(1, 4001),
    "a": range(1, 4001),
    "s": range(1, 4001),
}
reduce_ranges("in", part_ranges, A, R)
print(sum(reduce(mul, (len(c[1]) for c in r)) for r in A))

#pprint(A)
