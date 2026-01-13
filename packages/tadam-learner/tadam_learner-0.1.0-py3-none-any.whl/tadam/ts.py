import copy
import numpy as np

class TS:
    def __init__(self, index, sequence):
        self.number_of_values = len(sequence[0][1])
        self.index = index
        self.sequence = sequence # seq of tuples
        self.edge_sequence = list()
        self.recognized = True

    def __deepcopy__(self, memo):
        if id(self) in memo:
            return memo[id(self)]
        sequence_copy = [(item[0], item[1][:]) for item in self.sequence]
        new_ts = TS(self.index, sequence_copy)
        memo[id(self)] = new_ts
        new_ts.number_of_values = self.number_of_values
        new_ts.edge_sequence = copy.deepcopy(self.edge_sequence, memo)
        new_ts.recognized = self.recognized
        return new_ts

    def get_penultimate(self, index):
        if index - 1 < 0: return None
        return self.edge_sequence[index-1].source # TODO: check

    def get_edge(self, index):
        if index - 1 < 0: return None
        return self.edge_sequence[index].id

    def get_symbol(self, index):
        return self.sequence[index][0]

    def get_value(self, index):
        return self.sequence[index][1]

    def get_global_clock_value(self, index):
        _,l = zip(*self.sequence)
        return list(np.array(l)[:index+1].sum(axis=0))

    def get_state(self, index):
        if index == -1: return self.edge_sequence[0].source
        return self.edge_sequence[index].destination
