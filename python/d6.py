from utils import read_numbers
import numpy as np

with open("../inputs/input6") as f:
    times = read_numbers(f.readline())
    distances = read_numbers(f.readline())

with open("../inputs/input6") as f:
    time = read_numbers(f.readline().replace(" ", ""))[0]
    distance = read_numbers(f.readline().replace(" ", ""))[0]

def calculate_distances(max_time):
    distances = np.cumsum(np.ones(max_time, dtype=int)) - 1
    distances = distances * (max_time - distances)
    return distances

prod = 1
for d, t in zip(distances, times):
    prod *= np.sum(calculate_distances(t) > d)
print(prod)

print(np.sum(calculate_distances(time) > distance))