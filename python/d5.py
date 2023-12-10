import re
from pprint import pprint
from utils import read_numbers
import tqdm.auto as tqdm

maps = []
initial_seeds = []

with open("../inputs/input5") as f:
    initial_seeds = read_numbers(f.readline())
    f.readline()
    cmap = None
    for line in f:
        if not line.strip():
            continue
        if re.match("(\w+)-to-(\w+) map:", line):
            if cmap is not None:
                maps.append(cmap)
            cmap = []
            continue
        dest, source, rlen = read_numbers(line)
        cmap.append((range(source, source+rlen), range(dest, dest+rlen)))
    maps.append(cmap)

def map_seed(tnum, maps, level=0):
    if len(maps) == level: return (tnum,)
    for source, dest in maps[level]:
        if tnum in source:
            next_tnum = dest.start + (tnum - source.start)
            return (tnum,) + map_seed(next_tnum, maps, level+1)
    return (tnum,) + map_seed(tnum, maps, level+1)

seed_maps = [map_seed(seed, maps) for seed in initial_seeds]
seed_maps.sort(key=lambda x: x[-1])
print(seed_maps[0][-1])

rmaps = [sorted([x[::-1] for x in m], key=lambda x: x[0].start) for m in maps[::-1]]
planted_seeds = [range(sstart, sstart+slen) for sstart, slen in zip(*[iter(initial_seeds)]*2)]
cloc = 0
with tqdm.tqdm() as pbar:
    while True:
        cmap = map_seed(cloc, rmaps)
        cseed = cmap[-1]
        if any(cseed in planted for planted in planted_seeds):
            break
        pbar.update(1)
        cloc += 1

print(f"Loc -> Seed: {cmap}")
print(f"Seed -> Loc: {map_seed(cseed, maps)}")
print(cseed, cloc)