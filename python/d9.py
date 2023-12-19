import numpy as np

sequences = []
with open("../inputs/input9") as f:
    for line in f:
        sequences.append(np.fromiter((int(x) for x in line.split()), dtype=np.int64))

def predict(sequence):
    diffs = np.diff(sequence)
    if np.all(diffs == 0):
        return sequence[-1]
    return predict(diffs) + sequence[-1]

def back_extrap(sequence):
    diffs = np.diff(sequence)
    if np.all(diffs == 0):
        return sequence[0]
    return sequence[0] - back_extrap(diffs)

next_elements = []
prev_elements = []
for s in sequences:
    next_elements.append(predict(s))
    prev_elements.append(back_extrap(s))
print(np.sum(next_elements))
print(np.sum(prev_elements))
