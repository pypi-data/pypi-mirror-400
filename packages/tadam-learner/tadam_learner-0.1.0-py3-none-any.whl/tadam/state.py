import collections
import copy

class State:
    """
    An instance of the class State is a state of an automaton.

    Attributes:
        name (str): name of the state
        initial (bool): true is the state is initial
        accepting (bool): true is the state is accepting
        edges_in (list[Edge]): set of the incoming edges
        edges_out (list[Edge]): set of the outgoing edges
    """
    def __init__(self, name: str, id: int, initial: bool = False, accepting: bool = False) -> None:
        """
        Args:
            name (str): Name of the state
            initial (:obj:`bool`, optional): True if the state is initial, False by default
            accepting (:obj:`bool`, optional): True if the state is accepting, False by default
        """
        self.name = name
        self.initial = initial
        self.accepting = accepting
        self.acc_nb = 0 # Number of time the state was accepting
        self.edges_in = list()
        self.edges_out = list()
        self._rank = 0
        self.tss = dict()
        self.id = id
        self.proba = 1 # prop of words going through the state (func update_probas to compute)

    def __deepcopy__(self, memo):
        if id(self) in memo:
            return memo[id(self)]
        new_state = State(self.name, self.id, self.initial, self.accepting)
        memo[id(self)] = new_state
        new_state.acc_nb = self.acc_nb
        new_state._rank = self._rank
        new_state.tss = {k: [(x, y[:]) for x, y in v] for k, v in self.tss.items()}
        new_state.proba = self.proba
        # new_state.edges_in = copy.deepcopy(self.edges_in, memo)
        # new_state.edges_out = copy.deepcopy(self.edges_out, memo)
        return new_state

    @property
    def rank(self):
        return self._rank

    @rank.setter
    def rank(self, value):
        self._rank = value

    def visit_number(self) -> int:
        """
        Returns:
            int: Number of time the state was visited
        """
        nb = 0
        # for edge in self.edges_in: # does not work for the initial state
        #     nb += edge.visit_number()
        for ts, visits in self.tss.items():
            nb += len(visits)
        return nb

    def add_edge(self, edge, in_out: str) -> None:
        """
        Add the edge to the set of incoming or outgoing edges of the state
        Args:
            edge (Edge): the edge to add
            in_out (str): "in" for incoming and "out" for outgoing
        """
        if in_out == 'in':
            self.edges_in.append(edge)
        elif in_out == 'out':
            self.edges_out.append(edge)

    def return_edge(self, symbol: str, value: int, prob: bool=False, direction: str="out"):
        """
        Return the outgoing edge for a given symbol and delay
        Args:
            symbol (str): the symbol
            value (int): the time value
            prob (bool): True to use the guard probability distribution, False to use min, max guards
        """
        edges = self.search_edges(symbol, direction)
        if edges is None: return None
        probas = dict.fromkeys(edges)
        if prob:
            for e in edges: probas[e] = e.value_probability(value)
            return max(probas, key=probas.get)
        else:
            for e in edges:
                g = e.reduced_guard()
                if g[0] <= value <= g[1]:
                    return e

    def del_edge(self, edge, in_out: str) -> None:
        """
        Remove the edge of the set of incoming or outgoing edges of the state
        Args:
            edge (Edge): the edge to delete
            in_out (str): "in" for incoming and "out" for outgoing
        """
        if in_out == 'in':
            self.edges_in.remove(edge)
        elif in_out == 'out':
            self.edges_out.remove(edge)

    def search_edges(self, symbol: str, in_out: str) -> list:
        """
        Return the incoming or outgoing edges having a specified symbol
        Args:
            symbol (str): the researched symbol
            in_out (str): "in" for incoming and "out" for outgoing
        Returns:
            list[Union[Edge, None]]: List containing the edges if found
        """
        res = []
        if in_out == 'in':
            for edge in self.edges_in:
                if edge.symbol == symbol: res.append(edge)
        elif in_out == 'out':
            for edge in self.edges_out:
                if edge.symbol == symbol: res.append(edge)
        return res

    def detect_overlap(self, guard1, rec_guard1, guard2, rec_guard2):
        """
        Detects overlap between two sets of guards and rec_guards.

        Parameters:
        - guard1, rec_guard1: Lists of lists representing the guards and rec_guards for the first edge.
        - guard2, rec_guard2: Lists of lists representing the guards and rec_guards for the second edge.

        Returns:
        - True if there is an overlap, False otherwise.
        """
        g1 = [v[:] for v in guard1] + [v[:] for v in rec_guard1]
        g2 = [v[:] for v in guard1] + [v[:] for v in rec_guard1]
        g1 = [v for v in g1 if len(v) != 0]
        g2 = [v for v in g2 if len(v) != 0]
        guards1_by_variable = list(zip(*g1))
        guards2_by_variable = list(zip(*g2))

        for gc1, gc2 in zip(guards1_by_variable, guards2_by_variable):
            min1 = min(gc1)
            max1 = max(gc1)
            min2 = min(gc2)
            max2 = max(gc2)

            if min(max1, max2) - max(min1, min2) >= 0:
                return True

        return False

    def undeterministic_edge_destination(self, timed: bool) -> list:
        """
        Check if the set of outgoing edges of the state is deterministic and returns a list of the destination states of the problematic edges
        Args:
            timed (bool): true if the two outgoing edges can have the same symbols but guards not overlapping, false if there can't be more that one transition for a given symbol
        Returns:
            list[State]: Destination states of the non determinist edges

        """
        symbols = [edge.symbol for edge in self.edges_out]
        res = dict(collections.Counter(symbols))
        for symb, occ in res.items():
            if occ > 1:
                if not timed:
                    return [edge.destination for edge in self.edges_out if edge.symbol == symb]
                rep = [e for e in self.edges_out if e.symbol == symb]
                for e in rep:
                    for other in [edge for edge in rep if edge != e]:
                        #overlaps = (min(max(e.guard+e.rec_guard), max(other.guard+other.rec_guard)) - max(min(e.guard+e.rec_guard), min(other.guard+other.rec_guard)) >= 0)
                        overlaps = self.detect_overlap(e.guard, e.rec_guard, other.guard, other.rec_guard)
                        if e.destination == other.destination: overlaps = True
                        if not e.destination.edges_out and not other.destination.edges_out: overlaps = True
                        if overlaps:
                            return [e.destination, other.destination]
        return list()

    def __repr__(self):
        return self.name

class EndingState(State):
    def __init__(self, id) -> None:
        super().__init__(name="SINK", id=id, initial=False, accepting=True)
        self._rank = 998877665544332211

    def __deepcopy__(self, memo):
        if id(self) in memo:
            return memo[id(self)]
        new_state = EndingState(self.id)
        memo[id(self)] = new_state
        new_state.acc_nb = self.acc_nb
        new_state.tss = {k: [(x, y[:]) for x, y in v] for k, v in self.tss.items()}
        new_state.proba = self.proba
        # new_state.edges_in = copy.deepcopy(self.edges_in, memo)
        # new_state.edges_out = copy.deepcopy(self.edges_out, memo)
        return new_state

    @property
    def rank(self):
        return self._rank

    @rank.setter
    def rank(self, value):
        pass
