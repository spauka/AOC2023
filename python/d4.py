import utils
from collections import defaultdict

nwinners = []
with open("../inputs/input4") as f:
    for line in f:
        inp = line.split(":")[1].split("|")
        winners, numbers = [set(utils.read_numbers(x)) for x in inp]
        nwinners.append(len(numbers.intersection(winners)))
    
print(sum(2**(nwinner-1) for nwinner in nwinners if nwinner))

cards = [1 for _ in range(len(nwinners))]
for i, nwinner in enumerate(nwinners):
    for j in range(i+1, min(len(nwinners), i+nwinner+1)):
        cards[j] += cards[i]

print(sum(cards))

