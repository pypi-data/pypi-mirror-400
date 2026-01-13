import copy

from tadam.state import State
from math import floor
import numpy as np
import scipy.stats

class Edge:
    """
    An instance of the class Edge is an edge of an automaton.

    Attributes:
        source (State): source state of the edge
        destination (State) : destination state of the edge
        symbol (str) : label of the edge
        guard (list) list of accepted time value for the edge
        tss (Dict[int, list(tuple)])
        proba (float): probability of
    """
    def __init__(self, source: State, destination: State, symbol: str, guard: list, id: int) -> None:
        """
        Args:
            source (State): source State of the edge
            destination (State): destination State of the edge
            symbol (str): label of the edge
            guard (list): list of accepted time value of the edge
        """
        self.source = source
        self.destination = destination
        self.symbol = symbol
        self.last_hash = None
        self.guard = guard
        self.rec_guard = []
        self.tss = dict()
        self.proba = 0
        self.id = id # for the custom deep copy
        self.cache = {}
        source.add_edge(self, 'out')
        destination.add_edge(self, 'in')
        self.mu = None
        self.cov = None
        self.sum_guard = None
        self.last_guard_length = -1
        self.dist = None

    def __deepcopy__(self, memo):
        if id(self) in memo:
            return memo[id(self)]
        guard_copy = [inner_list[:] for inner_list in self.guard]
        new_edge = Edge(copy.deepcopy(self.source, memo), copy.deepcopy(self.destination, memo), self.symbol, guard_copy, self.id)
        new_edge.rec_guard = [inner_list[:] for inner_list in self.rec_guard]
        new_edge.tss = {k: [(x, y[:]) for x, y in v] for k, v in self.tss.items()}
        new_edge.proba = self.proba
        new_edge.mu = self.mu.copy()
        new_edge.cov = self.cov.copy() # TODO: correct once time_distribution is fixed
        new_edge.dist = self.dist.copy()
        new_edge.sum_guard = self.sum_guard
        new_edge.last_guard_length = self.last_guard_length
        new_edge.last_hash = self.last_hash
        new_edge.cache = self.cache
        memo[id(self)] = new_edge
        self.time_distribution() # to compute mu and cov
        return new_edge

    def visit_number(self) -> int:
        """
        Returns:
            int: Number of time this transition has been visited
        """
        return len(self.guard)+len(self.rec_guard)

    def print(self) -> str:
        """
        Print the edge in the following format
        "SOURCE_STATE -> DESTINATION_STATE [label='SYMBOL GUARD']"
        Args:
            reduce_guard (:obj:`bool`, optional): true for a reduced printing of the guard (min and max), false for all the possible time values
        """
        tmp = self.source.name + ' -> ' + self.destination.name + ' [label="' + self.symbol + ' '
        tmp += str(self.time_distribution()) + '"]'
        print(tmp)
        return tmp

    def time_distribution(self, additional_visits=None):
        """
        Return the normal distribution parameters (median, std) corresponding to the guard
        Returns:
            tuple[int, int]: the median and standard deviation
        """

        l = len(self.guard)
        if l != self.last_guard_length:
            self.last_guard_length = l
            self.sum_guard = np.sum(self.guard, axis=0)

        additional_visits = additional_visits or []

        # avoid concatenation because it’s very slow
        mu = (self.sum_guard + np.sum(self.rec_guard, axis=0) + np.sum(additional_visits, axis=0)) / (l + len(self.rec_guard) + len(additional_visits))
        new_hash = sum(mu)
        if new_hash == self.last_hash:
            return (self.mu, self.cov)

        all_guard = self.guard+self.rec_guard+additional_visits
        assert len(all_guard) > 0
        self.last_hash = new_hash
        self.cache = {} # reset the cache

        self.mu = mu
        # self.mu = np.mean(all_guard, axis=0)
        if len(all_guard[0]) == 1:
            var = np.var(all_guard) if len(all_guard) > 1 else 1e-6
            self.cov = np.array([[max(var, 1e-6)]])
        else:
            if len(all_guard) == 1:
                self.cov = 1e-6*np.identity(len(self.mu))
            else:
                self.cov = np.cov(all_guard, rowvar=0) + 1e-6*np.identity(len(self.mu))
        self.dist = scipy.stats.multivariate_normal(self.mu, self.cov, allow_singular=True)
        return (self.mu, self.cov)

    def value_probability(self, value, additional_visits=None, recompute=True):
        """
        Return the normal distribution parameters (median, std) corresponding to the guard
        Args:
            value (int): time value
        Returns:
            float: the probability to observe such value given the guard distribution
        """
        if recompute:
            self.time_distribution(additional_visits) # update the time distribution

        s = str(value)
        p = self.cache.get(s)

        if not p:
            lower = [v - 1/2 for v in value]
            upper = [v + 1 for v in lower]
            if self.dist is None:
                self.dist = scipy.stats.multivariate_normal(self.mu, self.cov, allow_singular=True)
            # compute the probability of seeing "value" with a limited precision
            p = self.dist.cdf(upper) - self.dist.cdf(lower)
            self.cache[s] = p

        return p

    def __repr__(self):
        return self.source.name + ' -> ' + self.destination.name + ' [label="' + self.symbol + ' ' + str((self.mu, self.cov)) + '"]'

class EndingEdge(Edge):
    def __init__(self, source: State, destination: State, id, guard=None) -> None:
        if guard is None: guard = []
        super().__init__(source, destination, symbol="$", guard=guard, id=id)

    def __deepcopy__(self, memo):
        if id(self) in memo:
            return memo[id(self)]
        guard_copy = [inner_list[:] for inner_list in self.guard]
        new_edge = EndingEdge(copy.deepcopy(self.source, memo), copy.deepcopy(self.destination, memo), self.id, guard_copy)
        new_edge.rec_guard = [inner_list[:] for inner_list in self.rec_guard]
        new_edge.tss = {k: [(x, y[:]) for x, y in v] for k, v in self.tss.items()}
        new_edge.proba = self.proba
        new_edge.mu = self.mu.copy()
        new_edge.cov = self.cov.copy() # TODO: correct once time_distribution is fixed
        new_edge.dist = self.dist.copy()
        new_edge.sum_guard = self.sum_guard
        new_edge.last_guard_length = self.last_guard_length
        new_edge.last_hash = self.last_hash
        new_edge.cache = self.cache
        memo[id(self)] = new_edge
        return new_edge
