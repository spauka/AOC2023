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

    def pulse(self, source, pulse, pulse_queue, iter_count):
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
    def pulse(self, source, pulse, pulse_queue, iter_count):
        if debug:
            print(f"{source} -> {pulse}")

    def cycle_length(self):
        return modules[next(iter(self.inputs))].cycle_length()
    def low_pulses(self):
        return modules[next(iter(self.inputs))].low_pulses()
    def high_pulses(self):
        return modules[next(iter(self.inputs))].high_pulses()

class Inv(Module):
    def pulse(self, source, pulse, pulse_queue, iter_count):
        super().pulse(source, 1-pulse, pulse_queue, iter_count)

    def init(self):
        super().init()
        assert len(self.inputs) == 1

    def cycle_length(self):
        return modules[next(iter(self.inputs))].cycle_length()
    def low_pulses(self):
        return modules[next(iter(self.inputs))].high_pulses()
    def high_pulses(self):
        return modules[next(iter(self.inputs))].low_pulses()

class Conj(Module):
    def __init__(self, name, outputs):
        super().__init__(name, outputs)
        self.states = None
        self.transition_times = None

    def init(self):
        super().init()
        self.states = {x: 0 for x in self.inputs}
        self.transition_times = {x: [] for x in self.inputs}

    def pulse(self, source, pulse, pulse_queue, iter_count):
        if self.states[source] != pulse and len(self.transition_times[source]) != 3:
            self.transition_times[source].append(iter)
        self.states[source] = pulse
        pulse = 1 - int(all(v == 1 for v in self.states.values()))
        super().pulse(source, pulse, pulse_queue, iter_count)

    def cycle_length(self):
        # Handle the special case of an inverter to set the number of output pulses to 1
        loopback_inv = None
        for output in outputs:
            if isinstance(modules[output], Inv) and self.name in modules[output].outputs:
                loopback_inv = output

        return np.lcm.reduce([modules[i].cycle_length() for i in self.inputs if i not in (self.name, loopback_inv)])

    def low_pulses(self):
        # Assume that we only output a single low pulse for each cycle pulse
        return 1

    def high_pulses(self):
        # Handle the special case of an inverter to set the number of output pulses to 1
        loopback_inv = None
        for output in outputs:
            if isinstance(modules[output], Inv) and self.name in modules[output].outputs:
                loopback_inv = output

        cycle_length = self.cycle_length()
        low_pulses = sum(modules[i].low_pulses()*(cycle_length//modules[i].cycle_length()) for i in self.inputs if i != (self.name, loopback_inv))
        high_pulses = sum(modules[i].high_pulses()*(cycle_length//modules[i].cycle_length()) for i in self.inputs if i != (self.name, loopback_inv))
        if self.name in self.inputs: high_pulses += 1
        return low_pulses + high_pulses - 1

    def __hash__(self):
        return self.hash ^ int.from_bytes(sha256(self.states.data).digest(), 'little')

class Flip(Module):
    def __init__(self, name, outputs):
        super().__init__(name, outputs)
        self.state = 0

    def init(self):
        super().init()

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

    def pulse(self, source, pulse, pulse_queue, iter_count):
        if pulse == 0:
            self.state = 1 - self.state
            super().pulse(source, self.state, pulse_queue, iter_count)

    def __hash__(self):
        return self.hash ^ int.from_bytes(sha256(self.state).digest(), 'little')

modules = {"output": Output("output", []), "rx": Output("rx", [])}
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
    if isinstance(module, Conj) and len(module.inputs) == 1:
        new_module = Inv(module.name, module.outputs)
        new_module.add_input(module.inputs.pop())
        module.init()
        modules[module.name] = new_module
        module = new_module

debug = False
pulse_queue = PulseQueue()
num_iterations = 1000
print_iters = []#3733, 4091, 3911, 4093]
iter = 0
output_modules = ["rl", "rd", "qb", "nn"]
with tqdm.tqdm(disable=debug) as pbar:
    while True:
        pbar.update()
        if iter == num_iterations:
            print()
            print((pulse_queue.low_pulses + num_iterations) * pulse_queue.high_pulses)
            print()

        # Check if we've found all transition times
        for module in output_modules:
            module = modules[module]
            if any(len(x) != 3 for x in module.transition_times.values()):
                break # We haven't found the transition times for at least one cuonter
        else:
            break # We're done finding all transition times

        iter += 1
        if (debug or iter in print_iters):
            print(f"Iter {iter}:")
        modules["broadcaster"].pulse("", 0, pulse_queue, iter)

        while pulse_queue:
            next, source, pulse = pulse_queue.popleft()
            if next == "rx" and pulse == 0:
                print(f"Num pulses: {iter}")
                break
            if next in modules:
                module = modules[next]
                if (debug or iter in print_iters) and module.name in output_modules:
                    prev_state = module.states.copy()
                module.pulse(source, pulse, pulse_queue, iter)
                if (debug or iter in print_iters) and module.name in output_modules and prev_state != module.states:
                    prev_state_str = ''.join([str(x) for x in prev_state.values()])
                    new_state_str = ''.join([str(x) for x in module.states.values()])
                    print(f"{module.name}: {prev_state_str} -> {new_state_str}")
        else:
            continue
        break

transition_times = []
for module in output_modules:
    module = modules[module]
    common_transition_time = sum(x[0] for x in module.transition_times.values() if x)
    print(module.name, module.transition_times)
    print(f"All 1 at: {common_transition_time}")
    transition_times.append(common_transition_time)
print()
print(np.lcm.reduce(transition_times, dtype=np.int64))
