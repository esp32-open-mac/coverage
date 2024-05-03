import sys
from dataclasses import dataclass
from pprint import pprint
import json
from collections import defaultdict


@dataclass
class TraceItem:
    is_read: bool
    address: str
    value: str
    stacktrace: list[str]

def find_common_path(first, second):
    result = []
    for f, s in zip(first, second):
        if f == s:
            result.append(f)
        else:
            break
    return result


class OutputNode:
    def __init__(self, name, value, implemented=False):
        self.name = name
        self.value = value
        self.children = []
        self.implemented = implemented
        self.rescaled = None
    
    def compact(self):
        sorted_children = defaultdict(list)
        for child in self.children:
            sorted_children[child.name].append(child)
        new_children = []
        for name, children in sorted_children.items():
            new_value = sum(c.value for c in children)
            new_grandchildren = [
                grandchild
                for child in children
                for grandchild in child.children
            ]
            new_child = OutputNode(name, new_value)
            new_child.children = new_grandchildren
            new_children.append(new_child)
        self.children = new_children
    
    def set_recursive_sum(self):
        # Adds values of each child to own value
        for child in self.children:
            child.set_recursive_sum()
        self.value = self.sum()
    
    def sum(self):
        return self.value + sum(child.value for child in self.children)

    def compact_recursive(self):
        self.compact()
        for child in self.children:
            child.compact_recursive()

    def serialize(self):
        return {
            'name': self.name,
            'value': self.rescaled if self.rescaled is not None else self.value,
            'mem_accesses': self.value,
            'children': [child.serialize() for child in self.children],
            'implemented': self.implemented,
        }

    def print(self):
        pprint(self.serialize())
    
    def set_recursive_implemented(self, implemented: set[str], force=False):
        if force or self.name in implemented:
            self.implemented = True
        for c in self.children:
            c.set_recursive_implemented(implemented, force=self.implemented)
    
    def fill_in_rescaled(self):
        self.rescaled = self.value
        for c in self.children:
            c.fill_in_rescaled()

    def propagate_scale(self, factor):
        self.rescaled *= factor
        for c in self.children:
            c.propagate_scale(factor)

    def recursive_rescale_to_log(self):
        for child in self.children:
            child.recursive_rescale_to_log()
        self.rescale_to_log()

    def rescale_to_log(self):
        if not self.children:
            return
        own_value = self.rescaled - sum(c.rescaled for c in self.children)
        # print(f'{self.name=} {own_value=}')
        scaler = lambda v: v**0.4
        new_scale_total = sum(scaler(v) for v in ([c.rescaled for c in self.children] + [own_value]))
        for c in self.children:
            
            current_proportion = c.rescaled / self.rescaled
            desired_proportion = scaler(c.rescaled) / new_scale_total
            # print(f'rescaling {c.name} {c.rescaled}: {current_proportion=:.3f} {desired_proportion=:.3f}')
            c.propagate_scale(desired_proportion / current_proportion)
        # print("------------")



    @classmethod
    def from_trace(cls, trace):
        root = cls('root', 0)
        prev_stacktrace = []
        for item in trace:
            stacktrace = item.stacktrace
            common_path = find_common_path(prev_stacktrace, stacktrace)
            specific_path = stacktrace[len(common_path):]
            prev_stacktrace = stacktrace

            target = root
            # navigate common path
            for name in common_path:
                if not target.children:
                    target.children.append(cls(name, 0))
                target = target.children[-1]
                assert target.name == name
            # navigate specific path
            for name in specific_path:
                target.children.append(cls(name, 0))
                target = target.children[-1]
                assert target.name == name
            # now, the target should be the deepest item in the stack trace
            target.value += 1
        return root

def parse_to_object(line):
    read_or_write, address, value, *stacktrace = line.strip().split(' ')
    stacktrace.reverse()
    return TraceItem(read_or_write == 'R', address, value, stacktrace)

# ---------------- main

# args: tracefile, output file
# stdin: implemented functions
with open(sys.argv[1]) as infile:
    raw_trace = [parse_to_object(line) for line in infile]

# trace = raw_trace
trace = [item for item in raw_trace if 'wifi_start_process' in item.stacktrace]
print(f'{len(trace)} memory accesses in trace')

root = OutputNode.from_trace(trace)

root.compact_recursive()
root.set_recursive_sum()


# fully_implemented_functions = {
#     'wifi_station_start',
#     '_do_wifi_start',
#     'wifi_clock_enable_wrapper',
#     'wifi_mode_set',
# }
fully_implemented_functions = set(line.strip().removesuffix(":implemented").removesuffix('_openmac') for line in sys.stdin)

root.set_recursive_implemented(fully_implemented_functions)
root.fill_in_rescaled()
root.recursive_rescale_to_log()

with open(sys.argv[2], 'w') as output:
    json.dump(root.serialize(), output)
