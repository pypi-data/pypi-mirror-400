import copy
import re
from math import floor, log2, pow
from statistics import NormalDist
from typing import Union
# from sklearn.metrics import roc_auc_score, precision_recall_curve
import numpy as np
import random

from tadam.utils import parse_string

try:
    import graphviz
    from IPython.display import Image, display
    import tempfile
    has_graphviz = True
except ImportError:
    has_graphviz = False

from tadam.edge import Edge, EndingEdge
from tadam.state import State, EndingState


class Automaton:
    """
    An instance of the class Automaton is a Timed Automaton
    Attributes:
        states (list[State]): list of states of the automaton
        edges (list[Edge]): list of edges of the automaton
        symbols (list[str]): alphabet if the automaton
    """
    def __init__(self, dot_path:str=None, number_of_values=1):
        """
        Create an automaton with an initial state named 'S0' if no dot path, create an automaton from a dot file otherwise
        Args:
            dot_path (:obj:`str`, optional): Path to an automaton in DOT format
        """
        self.kfutures = {}
        self.states = []
        self.edges = []
        self.symbols = []
        self.unmatched_tss = set()
        self.corrected_tss = {} # dictionary. Index: tss index. Value: list of (letter, value)
        self.generated_words = None
        self.generated_k = None
        self.number_of_values = number_of_values

        if dot_path is None:
            self.add_state('S0', initial=True)
        else:
            self.import_from_dot(dot_path)
        self.tss = []

        self.cost_transition = 0
        self.cost_deletion = 0
        self.cost_reemission = 0
        self.cost_transposition = 0
        self.cost_addition = 0

    def __deepcopy__(self, memo):
        if id(self) in memo:
            return memo[id(self)]
        new_ta = Automaton(number_of_values=self.number_of_values)
        memo[id(self)] = new_ta
        new_ta.states = []
        new_ta.kfutures = {k: v for k, v in self.kfutures.items()} # TODO: check that doesn't contain mutable objects and still useful
        new_ta.states = copy.deepcopy(self.states, memo)
        new_ta.edges = copy.deepcopy(self.edges, memo)
        new_ta.symbols = self.symbols[:]
        new_ta.unmatched_tss = set(self.unmatched_tss)
        new_ta.corrected_tss = copy.deepcopy(self.corrected_tss, memo)
        new_ta.generated_words = self.generated_words # TODO: check that doesn't contain mutable objects
        new_ta.generated_k = self.generated_k # TODO: check that doesn't contain mutable objects
        new_ta.tss = [sublist[:] for sublist in self.tss]
        new_ta.cost_transition = self.cost_transition
        new_ta.cost_deletion = self.cost_deletion
        new_ta.cost_reemission = self.cost_reemission
        new_ta.cost_transposition = self.cost_transposition
        new_ta.cost_addition = self.cost_addition
        return new_ta

    def update_probas(self) -> None:
        """
        Update the edges probability of access
        """
        for state in self.states:
            sum = 0
            for edge in state.edges_out:
                sum += edge.visit_number()
            for edge in state.edges_out:
                if sum != 0:
                    edge.proba = edge.visit_number() / sum
                else:
                    edge.proba = 0
                edge.time_distribution()
            state.proba = len(state.tss) / len(self.tss) # TODO: check and see if we remove the tss not accepted anymore after part deletion

    def add_state(self, name:str, accepting:bool=False, initial:bool=False) -> State:
        """
        Create and add a new state to the state list of the automaton \n
        Args:
            name (str): Name of the new state
            accepting (:obj:`bool`, optional): True if the state is accepting
            initial (:obj:`bool`, optional): True if the state is initial
        Returns:
            State: The added state
        """
        if name == "SINK":
            s = EndingState(id=max([s.id for s in self.states], default=-1)+1)
        else:
            s = State(name, id=max([s.id for s in self.states], default=-1)+1, initial=initial, accepting=accepting)
        self.states.append(s)
        return s

    def add_edge(self, source: str, destination: str, symbol: str, guard: list) -> Edge:
        """
        Create and add a new edge to the edge list of the automaton \n
        Args:
            source (str): State name of the source of the edge
            destination (str): State name of the destination of the edge
            symbol (str): Symbol of the edge
            guard (list[int]): List of possible time values for the edge
        Returns:
            Edge: The added edge
        """
        if source not in [state.name for state in self.states]:
            source = self.add_state(source)
        else:
            i = [state.name for state in self.states].index(source)
            source = self.states[i]
        if destination not in [state.name for state in self.states]:
            destination = self.add_state(destination)
        else:
            i = [state.name for state in self.states].index(destination)
            destination = self.states[i]
        if symbol == "$":
            e = EndingEdge(source, destination, id=max([e.id for e in self.edges], default=-1)+1, guard=guard)
        else:
            e = Edge(source, destination, symbol, guard, id=max([e.id for e in self.edges], default=-1)+1)
        self.edges.append(e)
        return e

    def search_state(self, name: str) -> Union[State, None]:
        """
        Search the state of the automaton having a specific name \n
        Args:
            name (str): Name of the researched state
        Returns:
            Union[State, None]: The state having the specified name, nothing if not found
        """
        d = {s.name: s for s in self.states}
        if name in d.keys(): return d[name]
        else: return None

    def next_edge(self, last: str, symbol: str, time_value: int = None, probabilistic=False, recompute=True) -> Union[Edge, None]:
        """
        Search the edge accessible from a given state, with a given symbol and a given time value (optional) \n
        Args:
            last (str): name of the source state of the researched transition
            symbol (str): symbol of the researched transition
            time_value (:obj:`int`, optional): Optional, the time value acceptable for the researched transition
        Returns:
            Union[Edge, None]: The edge accessible, nothing if none
        """
        source = self.search_state(last)
        if probabilistic:
            candidates = [e for e in source.edges_out if e.symbol == symbol]
            if len(candidates) == 0: return None
            probas = [e.value_probability(time_value, recompute=recompute) for e in candidates]
            return candidates[probas.index(max(probas))]
        for e in source.edges_out:
            if e.symbol == symbol:
                if time_value is not None:
                    for i,t in enumerate(time_value):
                        if not (np.min(e.guard,axis=0)[i] <= t <= np.max(e.guard,axis=0)[i]):
                            return None
                    return e
                else: return e

    def next_state_index(self) -> int:
        """
        Returns:
            int: The smallest state index available
        """
        liste = []
        available = False
        for state in self.states:
            if isinstance(state, EndingState): continue
            liste.append(eval(state.name[1:]))  # pas le 'S'
        i = 0
        while not available:
            i += 1
            if i not in liste: available = True
        return i

    def print(self) -> list:
        """
        Print the transitions of the automaton in the dot syntax
        SOURCE_STATE -> DESTINATION_STATE [label='SYMBOL GUARD p=PROBABILITY'] \n
        Returns:
            list[str]: A list where each element is a line of the dot file
        """
        mem = []
        for state in self.states:
            for e in state.edges_out:
                tmp = e.source.name + ' -> ' + e.destination.name
                tmp += ' [label="' + e.symbol + ' '
                tmp += str(e.time_distribution()) + ' '
                tmp += 'p=' + str(round(e.proba, 5)) + '"]'
                mem.append(tmp)
        print(*mem, sep='\n')
        return mem

    def print_p(self, p_min:float, mem:set=set(), state:str='S0', states:set={'S0'}) -> tuple:
        """
        Recursively build the strings to print the transitions having a minimal probability of access \n
        Args:
            p_min (float): Minimal probability of the printed edges
            mem (:obj:`set`, optional): Memory for the recursive process
            state (:obj:`str`, optional): Current state for recursion
            states (:obj:`str`, optional): Visited states for recursion
        Returns:
            tuple[set[str], set[str]]: The first component is a set of strings of the transitions and the second component is a set of state names to print
        """
        state = self.search_state(state)
        for edge in state.edges_out:
            if edge.proba >= p_min:
                if edge.source.name not in states: states.add(edge.source.name)
                if edge.destination.name not in states: states.add(edge.destination.name)
                tmp = edge.source.name + ' -> ' + edge.destination.name
                tmp += ' [label="' + edge.symbol + ' '
                tmp += str(edge.time_distribution()) + ' '
                tmp += 'p=' + str(round(edge.proba, 2)) + '"]'
                if tmp not in mem:
                    mem.add(tmp)
                    mem, states = self.print_p(p_min, mem, edge.destination.name, states)
                else:
                    return (mem, states)
        return (mem, states)

    def show(self, p_min: float=0, title: str=None) -> None:
        """
        Create a temporary file of the automaton graph \n
        Args:
            p_min (:obj:`float`, optional): minimal probability of access for a path to be printed, 0 by default
            title (:obj:`str`, optional): optional, title of the automaton
        """
        if not has_graphviz: return
        tmp = 'digraph G {\n' + 'START [style=invisible]\n'
        tmp += 'graph [fontname = "helvetica"]\n'
        tmp += 'node [fontname = "helvetica"]\n'
        tmp += 'edge [fontname = "helvetica"]\n'
        if title is not None:
            tmp += 'labelloc="t"\nlabel="' + title + '"\n'
        mem, states = self.print_p(p_min, mem=set(), state='S0', states={'S0'})
        if len(states) > 200:
            print('TA too large. (', str(len(states)), 'states)')
            print(mem)
            return
        for state in states:
            s = self.search_state(state)
            if s.accepting:
                tmp += s.name + ' [shape="doublecircle"]\n'
            else:
                tmp += s.name + ' [shape="circle"]\n'
        tmp += 'START -> S0\n'
        mem = self.print()
        for line in mem:
            tmp += line + '\n'
        tmp += '}'
        s = graphviz.Source(tmp, filename=tempfile.mktemp('.gv'), format="png")
        display(Image(s.view()))

    def export_ta(self, path: str, guard_as_distrib=False, decimal=5) -> None:
        """
        Export the automaton in a dot file
        Args:
            path (str): Path for the automaton dot file
        """
        file = open(path, 'w+')
        file.write("digraph G {" + '\n')
        for state in self.states:
            for e in state.edges_out:
                tmp = e.source.name + ' -> ' + e.destination.name
                tmp += ' [label="' + e.symbol + ' '
                if guard_as_distrib:
                    med, std = e.time_distribution()
                    tmp += 'N(' + re.sub('\n', '', np.array2string(med, separator=', ')) + ', ' + re.sub('\n', '', np.array2string(std, separator=', ')) + ') '
                else:
                    tmp += str(e.reduced_guard()) + ' '
                tmp += 'p=' + str(round(e.proba, decimal)) + '"]'
                file.write(tmp+'\n')
        file.write('}')
        file.close()

    def import_from_dot(self, dot_path: str) -> None:
        """
        Create an Automaton instance from a DOT file
        Args:
            dot_path (str): Path to the automaton DOT file
        """
        dot_file = open(dot_path)
        lines = dot_file.readlines()
        dot_file.close()

        for line in lines:
            if line == "digraph G {\n" or line == "}": continue
            if re.search('^//', line) is not None: continue
            line = re.sub('//.*', '', line)
            if re.search('->', line) is None: continue
            if re.search('label', line) is None: continue
            line = re.sub(r'^\s+', '', line)  # remove space at the beginning
            m = re.search(r'^[\w]+(?=\s*)', line)
            source = str(m.group(0))
            m = re.search(r'(?<=-> )[\w]+', line)
            destination = str(m.group(0))
            m = re.search(r'(?<=")[\w><?!$]+', line)
            symbol = str(m.group(0))
            if symbol not in self.symbols: self.symbols.append(symbol)
            m = re.search(r'N\((\[[\d.\se\+\-,]+\]),\s*(\[(\[[\d.\se\+\-,]+\](,\s)?)+\])\)', line)
            if m is None: # backward support for one-dimension guards
                m = re.search(r'N\(([\d,\.\s]+),\s*([\d.]+)\)', line)
                assert m is not None, "Cannot parse dot line: "+str(line)
                mu = [eval(str(m.group(1)))]
                cov = [[eval(str(m.group(2)))]]
                self.number_of_values = 1
            else:
                mu = np.array(eval(m.group(1)))
                cov = np.array(eval(m.group(2)))
                self.number_of_values = len(mu)
            m = re.search(r'(?<=p=)[\d.]+', line)
            proba = str(m.group(0))

            edge = self.add_edge(source, destination, symbol, [])
            edge.mu = mu
            edge.cov = cov
            edge.proba = eval(proba)

        self.search_state('S0').initial = True

    def __exist_path(self, ts: list, timed: bool, initial: str = 'S0', probabilistic=False, parser=parse_string, recompute=False) -> bool:
        """
        Tests if there is a path in the automaton consistent with the timed string
        Args:
            ts (list[str]): Timed string to test
            timed (bool): True the time values must be taken into consideration
            initial (:obj:`str`, optional): Name of the state where to start the path, S0 by default
            parser (func): Function used to parse the timed strings
        Returns:
            bool: True if there is a path, False otherwise
        """
        seq_edges = []
        last = self.search_state(initial)
        seq_states = [last]
        for pair in ts[:-1]:
            s, d = parser(pair)
            if timed:
                edge = self.next_edge(last.name, s, d, probabilistic=probabilistic, recompute=recompute)
            else:
                edge = self.next_edge(last.name, s, probabilistic=probabilistic, recompute=recompute)
            if edge is None: return False
            last = edge.destination
            seq_edges.append(edge)
            seq_states.append(last)
        s, d = parser(ts[-1])
        if timed:
            edge = self.next_edge(last.name, s, d, probabilistic=probabilistic, recompute=recompute)
        else:
            edge = self.next_edge(last.name, s, probabilistic=probabilistic)
        if edge is None: return False
        last = edge.destination
        seq_edges.append(edge)
        seq_states.append(last)
        return True

    def inconsistency_nb(self, tss: list, timed: bool, show: bool = True, p: bool = True, probabilistic=False, parser=parse_string, recompute=False) -> int:
        """
        Tests if the automaton is consistent with a set of timed strings
        Args:
            tss (list[str]): List of timed strings
            timed (bool): True if time values should be taken into consideration
            show (:obj:`bool`, optional): True if the automaton should be displayed if an inconsistency is found
            p (:obj:`bool`, optional): True if the timed string should be printed if an inconsistency is found
            parser (func): Function used to parse the timed strings
        Returns:
            int: Number of timed strings inconsistent with the automaton
        """
        mem = list()
        for ts in tss:
            exist = self.__exist_path(ts, timed, probabilistic=probabilistic, parser=parser, recompute=recompute)
            if not exist:
                mem.append(tss.index(ts))
        if len(mem) > 0:
            if p:
                for ts in mem:
                    print(tss[ts])
            if show: self.show()
        return len(mem)

    def show_h(self, state: State, text: str = "") -> None:
        """
        Displays the automaton with a state highlighted
        Args:
            state (State): State to highlight
            text (:obj:`str`, optional): A text to add next to the automaton
        """
        tmp = 'digraph G {\n' + 'START [style=invisible]\n'
        tmp += 'graph [fontname = "helvetica"]\n'
        tmp += 'node [fontname = "helvetica"]\n'
        tmp += 'edge [fontname = "helvetica"]\n'
        tmp += state.name + ' [fillcolor=yellow, style=filled]\n'
        tmp += 'text [shape=box, label="' + text + '"]\n'
        mem, states = self.print_p(0, mem=set(), state='S0', states={'S0'})
        if len(states) > 200:
            print('TA too large. (', str(len(states)), 'states)')
            print(mem)
            return
        for state in states:
            s = self.search_state(state)
            if s.accepting:
                tmp += s.name + ' [shape="doublecircle"]\n'
            else:
                tmp += s.name + ' [shape="circle"]\n'
        tmp += 'START -> S0\n'
        mem = self.print()
        for line in mem:
            tmp += line + '\n'
        tmp += '}'
        s = graphviz.Source(tmp, filename=tempfile.mktemp('.gv'), format="png")
        display(Image(s.view()))

    def import_from_dot_and_data(self, dot_path: str, tss_path: str, data_parser) -> None:
        """
        Create an Automaton instance from a DOT file
        Args:
            dot_path (str): Path to the automaton DOT file
        """
        guards_distrib = False
        dot_file = open(dot_path)
        lines = dot_file.readlines()
        dot_file.close()
        tss_file = open(tss_path)
        tss = tss_file.readlines()
        tss_file.close()
        transitions = dict()
        tss_objects = dict()
        for line in lines:
            if line == "digraph G {\n" or line == "}": continue
            if re.search('^//', line) is not None: continue
            line = re.sub('//.*', '', line)
            if re.search('->', line) is None: continue
            if re.search('label', line) is None: continue
            line = re.sub(r'^\s+', '', line)  # remove space at the beginning
            m = re.search(r'^[\w]+(?=\s*)', line)
            source = str(m.group(0))
            m = re.search(r'(?<=-> )[\w]+', line)
            destination = str(m.group(0))
            m = re.search(r'(?<=")[\w?!$]+', line)
            symbol = str(m.group(0))
            if symbol not in self.symbols: self.symbols.append(symbol)
            m = re.search(r'(?<=\[)(([\d]+, )?)+[\d]+(?=\])', line) # TODO: update function as import_from_dot()
            if m is not None:
                res = eval(m.group(0))
                if isinstance(res, int): guard = [res]
                else: guard = list(res)
                guards_distrib = False
                self.number_of_values = 1
            else:
                m = re.search(r'N\(([\d.]+),\s*([\d.]+)\)', line)
                guards_distrib = True
                med = eval(str(m.group(1)))
                std = eval(str(m.group(2)))
                guard = []
                self.number_of_values = len(med)
            m = re.search(r'(?<=p=)[\d.]+', line)
            proba = str(m.group(0))

            e = self.add_edge(source, destination, symbol, guard)
            if guards_distrib:
                transitions.setdefault(source, []).append(((med, std), e))
            else:
                transitions.setdefault(source, []).append((guard, e))

        def value_probability(med, std, value, precision=1e0):
            if std == 0:
                if med == value:
                    return 1
                else:
                    return 0
            dist = NormalDist(med, std)
            # compute the probability of seeing "value" with a limited precision
            p = (dist.cdf(floor(value / precision) * precision + precision / 2) - dist.cdf(
                floor(value / precision) * precision - precision / 2))
            return p

        for i, ts in enumerate(tss):
            tss_objects[i] = list()
            ts = ts.rstrip()  # remove trailing spaces if any
            ts = re.sub('\\n', '', ts)
            ts = ts.split(' ')
            if "$" not in ts[-1]: ts += ["$"]
            self.tss.append(ts)
            last = 'S0'
            gtime = 0
            for index, pair in enumerate(ts):
                s, d = data_parser(pair)
                gtime += d
                candidate_edges = [(guard, e) for (guard, e) in transitions[last] if e.symbol == s]
                if not candidate_edges:
                    self.unmatched_tss.update([i])
                    break
                if guards_distrib:
                    edge = candidate_edges[np.argmax([value_probability(med, std, d) for ((med, std), e) in candidate_edges])][1]
                else:
                    edge = [e for (guard, e) in candidate_edges if guard[0] <= d <= guard[1]]
                    if len(edge) == 0:
                        self.unmatched_tss.update([i])
                        break
                    else:
                        edge = edge[0]
                edge.guard.append(d)
                tss_objects[i].append(edge)
                if i in edge.tss.keys():
                    edge.tss[i].append((index, gtime))
                else:
                    edge.tss[i] = [(index, gtime)]
                if i in edge.destination.tss.keys():
                    edge.destination.tss[i].append((index, gtime))
                else:
                    edge.destination.tss[i] = [(index, gtime)]
                last = edge.destination.name

        for e in self.edges:
            e.guard = e.guard[2:]

        for ts in self.unmatched_tss:
            tss_objects[ts] = list()
            for state in self.states:
                if ts in state.tss:
                    del state.tss[ts]
            for edge in self.edges:
                if ts in edge.tss:
                    for ix, _ in edge.tss[ts]:
                        _, tv = data_parser(self.tss[ts][ix])
                        edge.guard.remove(tv)
                    del edge.tss[ts]

        self.search_state('S0').initial = True

        self.update_probas()

        return tss_objects

    def _generate_exhaustively(self, k):
        if self.generated_words is None or self.generated_k!=k:
            self.generated_words = {}
            self.generated_k = k
            self._generate_exhaustively_rec(self.generated_words, k, self.states[0])
        return self.generated_words

    def _generate_exhaustively_rec(self, output_dict, k, current_node, current_log_proba=0, current_word=""):
        if current_log_proba <= -50:
            return
        if current_node.accepting:
            prev = output_dict.get(current_word)
            if prev:
                output_dict[current_word] = log2(pow(2,prev) + pow(2,current_log_proba))
            else:
                output_dict[current_word] = current_log_proba
        else:
            k -= 1
            if k >= 0:
                for edge in current_node.edges_out:
                    if edge.proba > 0:
                        self._generate_exhaustively_rec(output_dict, k, edge.destination, current_log_proba + log2(edge.proba), current_word + edge.symbol)
            return

    def is_universal(self):
        return len([s for s in self.states if not isinstance(s, EndingState)]) == 1

    def get_log_proba(self, w, timed=False):
        assert self.states[0].initial
        if timed:
            return max(-1000,self.greedy_get_log_proba_rec_time(w, self.states[0]))
        else:
            return max(-50, self.get_log_proba_rec(w, self.states[0]))

    def get_log_proba_rec(self, w, current_node, current_log_proba=0):
        if current_node.accepting and w == "":
            return current_log_proba
        elif w == "":
            return -50
        else:
            max_proba = -50
            for edge in current_node.edges_out:
                if edge.symbol == w[0]:
                    new_proba = self.get_log_proba_rec(w[1:], edge.destination, current_log_proba + log2(edge.proba))
                    if new_proba > max_proba:
                        max_proba = new_proba
            return max_proba

    def greedy_get_log_proba_rec_time(self, w, current_node):
        current_log_proba = 0
        for l in w:
            max_proba = None
            best_edge = None
            for edge in current_node.edges_out:
                if edge.symbol == l[0]:
                    new_proba = max(1e-100, edge.proba * edge.value_probability((l[1]), recompute=False))
                    if max_proba is None or new_proba > max_proba:
                        max_proba = new_proba
                        best_edge = edge
            if max_proba is None:
                return -1000
            current_log_proba += log2(max_proba)
            current_node = best_edge.destination
        if current_node.accepting:
            return current_log_proba
        return -1000

    def get_log_proba_rec_time(self, w, current_node, current_log_proba=0):
        if current_node.accepting and len(w) == 0:
            return current_log_proba
        elif len(w) == 0:
            return -1000
        else:
            max_proba = -1000
            for edge in current_node.edges_out:
                if edge.symbol == w[0][0]:
                    new_proba = self.get_log_proba_rec_time(w[1:], edge.destination, current_log_proba + log2(max(1e-100, edge.proba * edge.value_probability((w[0][1]), recompute=False))))
                    if new_proba > max_proba:
                        max_proba = new_proba
            return max_proba

    def js_divergence(self, other_ta, k=8, verbose=False):
        distrib1 = self._generate_exhaustively(k)
        distrib2 = other_ta._generate_exhaustively(k)
        if verbose:
            print("Distrib of self:", distrib1)
            print("Distrib of the other:", distrib2)
        score = 0
        all_words = set(distrib1.keys()).union(set(distrib2.keys()))
        for w in all_words:
            l1 = distrib1.get(w)
            l2 = distrib2.get(w)
            p1 = pow(2, l1) if l1 else 0
            p2 = pow(2, l2) if l2 else 0
            m = 0.5 * (p1 + p2)
            if p1 > 0:
                score += 0.5 * p1 * log2(p1 / m)
            if p2 > 0:
                score += 0.5 * p2 * log2(p2 / m)
        return score

    def jaccard(self, other_ta, k=8, verbose=False):
        if self.is_universal():
            learned_words = set(other_ta._generate_exhaustively(k).keys())
            q = len(self.symbols)-1
            union = (pow(q,k+1)-1)/(q-1)
            return 1-len(learned_words)/union
        else:
            true_words = set(self._generate_exhaustively(k).keys())
            if other_ta.is_universal():
                q = len(self.symbols)-1
                union = (pow(q,k+1)-1)/(q-1)
                return 1-len(true_words)/union
            else:
                learned_words = set(other_ta._generate_exhaustively(k).keys())
                if verbose:
                    print("Real:",len(true_words),"learned:",len(learned_words),"intersection:",len(true_words.intersection(learned_words)),"union:",len(true_words.union(learned_words)))
                return 1-len(true_words.intersection(learned_words))/len(true_words.union(learned_words))

    #def balanced_roc_auc(self, other_ta, k=10, verbose=False):
    #    groundtruth = self._generate_exhaustively(k)
    #    y_score = []
    #    y_true = []
    #    random.seed(42)
    #    negative_words = []
    #    # generate random word uniformily
    #    tmp_symbols = [s for s in self.symbols if s != "$"]
    #    q = len(tmp_symbols)
    #    assert q > 1
    #    max_val = (pow(q,k+1)-1)/(q-1)
    #    for _ in range(len(groundtruth)):
    #        val = random.randint(0,max_val)
    #        w = ""
    #        while val > 0:
    #            w = w + tmp_symbols[val % q]
    #            val //= q
    #        negative_words.append(w+"$")

    #    all_words = negative_words + list(groundtruth.keys())
    #    y_true = [0]*len(negative_words) + [1]*len(groundtruth)
    #    print("Measure with",len(all_words),"words")
    #    for w in all_words:
    #        y_score.append(other_ta.get_log_proba(w)) # word not recognized: very low score
    #    precision, recall, threshold = precision_recall_curve(y_true, y_score)
    #    best_fscore = 0
    #    tr = 0
    #    for i,p in enumerate(precision):
    #        r = recall[i]
    #        if p+r > 0:
    #            fscore = 2*p*r/(p+r)
    #            if fscore > best_fscore:
    #                best_fscore = fscore
    #                tr = threshold[i]
    #    print("threshold:",pow(2,tr))
    #    return best_fscore, roc_auc_score(y_true, y_score)

    #def roc_auc(self, other_ta, k=10):
    #    all_words = ["$"]
    #    words = [[""]]
    #    for i in range(k):
    #        words.append([s + symbol for symbol in self.symbols if symbol!="$" for s in words[i]])
    #        all_words += [w + "$" for w in words[i+1]]

    #    groundtruth = self._generate_exhaustively(k)
    #    distrib = other_ta._generate_exhaustively(k)
    #    y_score = []
    #    y_true = []
    #    for w in all_words:
    #        y_true.append(0 if groundtruth.get(w) is None else 1)
    #        y_score.append(distrib.get(w, -50)) # word not recognized: very low score
    #    precision, recall, threshold = precision_recall_curve(y_true, y_score)
    #    best_fscore = 0
    #    # tr = 0
    #    for i,p in enumerate(precision):
    #        r = recall[i]
    #        if p+r > 0:
    #            fscore = 2*p*r/(p+r)
    #            if fscore > best_fscore:
    #                best_fscore = fscore
    #                # tr = threshold[i]
    #    # print("threshold:",pow(2,tr))
    #    return best_fscore, roc_auc_score(y_true, y_score)
