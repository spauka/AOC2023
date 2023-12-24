import re
from hashlib import sha256
from collections import deque
import numpy as np
import tqdm.auto as tqdm

class PulseQueue(deque):
    def __init__(self):
        super().__init__()
        self.low_pulses = 0
        self.high_pulses = 0

    def append(self, pulse):
        super().append(pulse)
        if pulse[-1] == 0:
            self.low_pulses += 1
        else:
            self.high_pulses += 1

class Module:
    def __init__(self, name, outputs):
        self.name = name
        self.outputs = outputs
        self.inputs = set()
        self.depends = set()
        self.hash = int.from_bytes(sha256(self.name.encode('ascii')).digest(), 'little')

    def add_input(self, input):
        self.inputs.add(input)
    def init(self):
        visited = set()
        to_visit = set(self.inputs)
        self.depends |= self.inputs
        while to_visit:
            cnode = to_visit.pop()
            visited.add(cnode)
            self.depends |= modules[cnode].inputs
            to_visit |= modules[cnode].inputs - visited
    def __hash__(self):
        return self.hash

    def pulse(self, source, pulse, pulse_queue):
        for output in self.outputs:
            pulse_queue.append((output, self.name, pulse))

    def cycle_length(self):
        raise NotImplementedError()
    def low_pulses(self):
        raise NotImplementedError()
    def high_pulses(self):
        raise NotImplementedError()


class Broadcast(Module):
    def cycle_length(self):
        return 1
    def low_pulses(self):
        return 1
    def high_pulses(self):
        return 0

class Output(Module):
    def pulse(self, source, pulse, pulse_queue):
        global debug
        if debug:
            print(f"{source} -> {pulse}")

class Conj(Module):
    def __init__(self, name, outputs):
        super().__init__(name, outputs)
        self.states = None

    def init(self):
        super().init()
        self.states = {x: 0 for x in self.inputs}

    def pulse(self, source, pulse, pulse_queue):
        self.states[source] = pulse
        pulse = 1 - int(all(v == 1 for v in self.states.values()))
        super().pulse(source, pulse, pulse_queue)

    def cycle_length(self):
        if len(self.inputs) == 1:
            return modules[next(iter(self.inputs))].cycle_length()
        raise NotImplementedError()
        return np.lcm.reduce([modules[i].cycle_length() for i in self.inputs])

    def low_pulses(self):
        if len(self.inputs) == 1: # Inverter
            return modules[next(iter(self.inputs))].high_pulses()
        raise NotImplementedError()

    def high_pulses(self):
        if len(self.inputs) == 1: # Inverter
            return modules[next(iter(self.inputs))].low_pulses()
        raise NotImplementedError()

    def __hash__(self):
        return self.hash ^ int.from_bytes(sha256(self.states.data).digest(), 'little')

class Flip(Module):
    def __init__(self, name, outputs):
        super().__init__(name, outputs)
        self.state = 0

    def init(self):
        super().init()
        if len(self.inputs) > 1: print(f"Flip-Flop Module {self.name} has {len(self.inputs)} inputs ({self.inputs})")

    def cycle_length(self):
        num_cycles = np.lcm.reduce([modules[i].cycle_length() for i in self.inputs])
        num_low_per_cycle = 0
        for input in self.inputs:
            num_low_per_cycle += modules[input].low_pulses() * (num_cycles//modules[input].cycle_length())
        if num_low_per_cycle%2 == 1:
            return 2*num_cycles
        return num_cycles

    def low_pulses(self):
        num_cycles = np.lcm.reduce([modules[i].cycle_length() for i in self.inputs])
        num_low_per_cycle = 0
        for input in self.inputs:
            num_low_per_cycle += modules[input].low_pulses() * num_cycles//modules[input].cycle_length()
        if num_low_per_cycle%2 == 1:
            return num_low_per_cycle
        return num_low_per_cycle//2

    def high_pulses(self):
        return self.low_pulses()

    def pulse(self, source, pulse, pulse_queue):
        if pulse == 0:
            self.state = 1 - self.state
            super().pulse(source, self.state, pulse_queue)

    def __hash__(self):
        return self.hash ^ int.from_bytes(sha256(self.state).digest(), 'little')

modules = {"output": Output("output", [])}
with open("../inputs/input20") as f:
    for line in f:
        module, outputs = re.match(r"([%&a-z]+) -> ([a-z, ]+)$", line).groups()
        outputs = [o.strip() for o in outputs.split(',')]
        if module[0] == "%":
            modules[module[1:]] = Flip(module[1:], outputs)
        elif module[0] == '&':
            modules[module[1:]] = Conj(module[1:], outputs)
        else:
            modules[module] = Broadcast(module, outputs)

    for module in modules.values():
        for output in module.outputs:
            if output in modules:
                modules[output].add_input(module.name)
            else:
                print(f"In module {module.name} dead output: {output}")
    for module in modules.values():
        module.init()

for module in sorted(modules):
    module = modules[module]
    print(f"Module {module.name} depends on: {module.depends}")
    try:
        print(f"  Module {module.name} cycle length: {module.cycle_length()}. ({module.low_pulses()}/{module.high_pulses()} L/H)")
    except NotImplementedError:
        print(f"  Module {module.name} cycle length: Not figured out yet")

debug = True
pulse_queue = PulseQueue()
num_iterations = 1000
iter = 0
with tqdm.tqdm(disable=debug) as pbar:
    while True:
        pbar.update()
        if iter == num_iterations:
            print()
            print((pulse_queue.low_pulses + num_iterations) * pulse_queue.high_pulses)
        if iter == 10:
            break
        iter += 1
        if debug:
            print(f"Iter {iter}:")
        modules["broadcaster"].pulse("", 0, pulse_queue)
        while pulse_queue:
            next, source, pulse = pulse_queue.popleft()
            if next == "rx" and pulse == 0:
                print(f"Num pulses: {iter}")
                break
            if next in modules:
                modules[next].pulse(source, pulse, pulse_queue)
        else:
            continue
        break
