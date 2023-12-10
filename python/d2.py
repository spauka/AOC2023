import re
from operator import mul
from functools import reduce
from collections import defaultdict

starting_config = {
    "red": 12,
    "green": 13,
    "blue": 14,
}

games = []
with open("../inputs/input2") as f:
    for line in f:
        _, configs = line.split(":")
        draws = []
        for config in configs.split(";"):
            draws.append({cube.strip(): int(count) for count, cube in (x.split() for x in config.split(","))})
        games.append(draws)

possible_games = 0
power_sum = 0
for i, game in enumerate(games):
    minimal_set = defaultdict(int)
    for draw in game:
        if any(starting_config[cube] < count for cube, count in draw.items()):
            break
    else:
        possible_games += i+1
    
    power_sum += reduce(mul, (max(draw.get(c, 0) for draw in game) for c in starting_config.keys()))

print(possible_games)
print(power_sum)
