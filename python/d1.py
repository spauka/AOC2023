import re

digits = {
    "one": "o1e", 
    "two": "t2o", 
    "three": "t3e", 
    "four": "f4r", 
    "five": "f5e", 
    "six": "s6x", 
    "seven": "s7n", 
    "eight": "e8t", 
    "nine": "n9e",
}

values = []
with open("../inputs/input1") as f:
    for line in f:
        for d, i in digits.items():
            line = line.replace(d, i)
        if (match := re.findall(r"\d+", line)):
            values.append("".join(match))
            
print(sum(int(x[0] + x[-1]) for x in values))