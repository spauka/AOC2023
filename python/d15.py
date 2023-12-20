import re

with open("../inputs/input15") as f:
    instrs = f.readline().strip().split(",")

def aochash(s):
    vals = s.encode("ascii")
    cval = 0
    for val in vals:
        cval = ((cval+val) * 17) % 256
    return cval

def find_lens(lenses, lens):
    for i, l in enumerate(lenses):
        if l[0] == lens: return i
    raise ValueError

boxes = [list() for _ in range(256)]
for instr in instrs:
    if (m := re.match("([a-z]+)-", instr)):
        lens = m.groups()[0]
        slot = aochash(lens)
        try:
            i = find_lens(boxes[slot], lens)
            boxes[slot].pop(i)
        except ValueError:
            pass
    elif (m := re.match("([a-z]+)=([0-9])", instr)):
        lens, power = m.groups()
        slot = aochash(lens)
        try:
            i = find_lens(boxes[slot], lens)
            boxes[slot][i] = (lens, int(power))
        except ValueError:
            boxes[slot].append((lens, int(power)))
    else:
        raise ValueError(f"Invalid instr: {instr}")

print(sum(aochash(instr) for instr in instrs))
print(sum((i+1)*sum((s+1)*p for s, (_, p) in enumerate(box)) for i, box in enumerate(boxes)))
