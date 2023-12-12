import re
import bisect
from typing import Optional
from functools import reduce
from utils import read_numbers

def close_gaps(cmap: list, max_val: Optional[int] = None):
    i = 0
    while i < len(cmap)-1:
        if cmap[i][0].stop != cmap[i+1][0].start:
            new_range = range(cmap[i][0].stop, cmap[i+1][0].start)
            cmap.insert(i+1, (new_range, new_range))
        else:
            i += 1
    if max_val is not None and cmap[-1][0].stop < max_val:
        new_range = range(cmap[-1][0].stop, max_val)
        cmap.append((new_range, new_range))
    return cmap

def combine_levels(next_results):
    next_results = iter(next_results)
    new_results = tuple(list(x) for x in next(next_results))
    for next_result in next_results:
        for i, next_level in enumerate(next_result):
            new_results[i].extend(next_level)
    return tuple(tuple(sorted(x, key=lambda x: x.start)) for x in new_results)

def map_seeds(trange, maps, level=0):
    if len(maps) == level: return ((trange,),)

    cind = bisect.bisect_left(maps[level], trange.start, key=lambda x: x[0].stop)
    next_ranges = []

    rstart = maps[level][cind][1].start + (trange.start - maps[level][cind][0].start)
    while trange.stop > maps[level][cind][0].stop:
        next_ranges.append(range(rstart, maps[level][cind][1].stop))
        cind += 1
        if cind >= len(maps[level]): # Maps outside the given ranges
            rstart = maps[level][cind-1][0].stop
            rstop = trange.stop
            break
        rstart = maps[level][cind][1].start
    else:
        rstop = maps[level][cind][1].stop - (maps[level][cind][0].stop - trange.stop)
    next_ranges.append(range(rstart, rstop))

    assert len(trange) == sum(len(x) for x in next_ranges)

    new_results = combine_levels([map_seeds(x, maps, level+1) for x in next_ranges])
    return (tuple(next_ranges),) + tuple(new_results)

maps = []
initial_seeds = []
with open("../inputs/input5") as f:
    initial_seeds = read_numbers(f.readline())
    cmap = []
    for line in f:
        if not line.strip(): continue
        if re.match("(\w+)-to-(\w+) map:", line):
            if cmap: maps.append(cmap)
            cmap = []
            continue
        dest, source, rlen = read_numbers(line)
        cmap.append((range(source, source+rlen), range(dest, dest+rlen)))
    maps.append(cmap)
maps = [close_gaps(sorted(m, key=lambda x:x[0].start)) for m in maps]

seed_maps = combine_levels(map_seeds(range(seed, seed), maps) for seed in initial_seeds)
seed_maps = sorted(seed_maps[len(maps)], key=lambda x: x.start)
print(seed_maps[0].start)

planted_seeds = [range(sstart, sstart+slen) for sstart, slen in zip(*[iter(initial_seeds)]*2)]
results = sorted(combine_levels(map_seeds(x, maps) for x in planted_seeds)[len(maps)], key=lambda x: x.start)
print(results[0].start)
