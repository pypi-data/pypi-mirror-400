import itertools
from collections import defaultdict
import random
from statistics import stdev, median, NormalDist
from math import floor
import scipy.stats

from tadam.automaton import Automaton
from tadam.state import State, EndingState
from tadam.edge import Edge, EndingEdge
from typing import Union
import re
from datetime import datetime
from random import shuffle
from sklearn.mixture import GaussianMixture
import copy
import warnings

from tadam.ts import TS
from tadam.utils import parse_string

from tadam.mdl import *

class TALearner:
    def __init__(self, tss_path: str = None, tss_list: list = None, res_path: str = None, display: bool = False, debug: bool = False, noise_model = None, data_parser=None, donotrun=False) -> None:
        """
        Args:
            tss_path (str): path of the file containing the timed strings
            tss_list (list[str]): python list containing the timed strings
            k (:obj:`int`, optional): number of transitions to consider for the merging process, 2 by default
            res_path (:obj:`str`, optional): path to the file where to export the learned automaton
            display (:obj:`bool`, optional): true if the learned automaton should be displayed at the end, False by default
            debug (:obj:`bool`, optional): true if verbose mode needed, False by default
            splits (:obj:`bool`, optional): True if splits are allowed, True by default
            order (:obj:`str`, optional): Ordering method for the operations (breadth-first/depth-first/random/bottom-up), breadth-first by default
            noise_model(:obj:`NoiseModel, optional): Noise model for TADAM
        """
        # t0 = datetime.now()
        self.tss = self.__import_tss(tss_path, tss_list)
        self.data_parser = data_parser or parse_string
        self.tss_objects = self.__import_tss_object()
        self.debug = debug
        self.ta = Automaton(number_of_values = len(self.data_parser(self.tss[0][0])[1]))
        self.ta.tss = self.tss
        self.operations = {"merges": 0, "splits": 0}
        self.data_cost = -1
        self.model_cost = -1
        self.noise_model = noise_model or NoiseModel()

        if donotrun: return

        # print("Model cost: " + str(model_cost(self.ta)))
        # print("Data cost: " + str(data_cost(self.ta, self.data_parser, self.noise_model)))
        # print("Total cost: " + str(data_cost(self.ta, self.data_parser, self.noise_model) + model_cost(self.ta)))
        if self.ta.inconsistency_nb(self.tss, True, parser=self.data_parser) > 0:
            print("Automaton not consistent.") # TODO: use parsing argument in Automaton class
        else:
            if res_path is not None:
                self.ta.export_ta(res_path)
            if display: self.ta.show(title='Final automaton')
        # dur = datetime.now() - t0
        # print('Execution time: ' + str(dur))

        assert len(self.tss) == len([ll for l in [e.tss.keys() for e in self.ta.edges if isinstance(e, EndingEdge)] for ll in l])
        assert len(self.tss) == sum([len(d) for e in self.ta.edges if isinstance(e, EndingEdge) for d in e.tss.values()])

    def __deepcopy__(self, memo=None):
        if memo is None:
            memo = {}
        if id(self) in memo:
            return memo[id(self)]
        new_learner = TALearner(tss_list=[], donotrun=True)
        memo[id(self)] = new_learner
        new_learner.tss = [sublist[:] for sublist in self.tss]
        new_learner.data_parser = self.data_parser
        new_learner.tss_objects = copy.deepcopy(self.tss_objects, memo)
        new_learner.debug = self.debug
        new_learner.ta = copy.deepcopy(self.ta, memo)
        new_learner.ta.tss = new_learner.tss
        new_learner.operations = {k: v for k, v in self.operations.items()}
        new_learner.data_cost = self.data_cost
        new_learner.model_cost = self.model_cost
        new_learner.noise_model = copy.deepcopy(self.noise_model, memo)
        # assert len([e for e in self.ta.edges if e in new_learner.ta.edges]) == 0
        # assert len([s for s in self.ta.states if s in new_learner.ta.states]) == 0
        # assert len([ts for ts in self.tss_objects.values() if ts in new_learner.tss_objects.values()]) == 0
        # assert len([e for ts in new_learner.tss_objects.values() for e in ts.edge_sequence if e not in new_learner.ta.edges]) == 0
        # assert len([e for e in new_learner.ta.edges if e.source not in new_learner.ta.states]) == 0
        # assert len([e for e in new_learner.ta.edges if e.destination not in new_learner.ta.states]) == 0
        return new_learner

    def __import_tss_object(self):
        tss = dict()
        for index, ts in enumerate(self.tss):
            sequence = [self.data_parser(t) for t in ts]
            tss[index] = TS(index, sequence)
        return tss

    def is_del_interesting(self, edge, freq_max):
        return len(set(edge.tss.keys()).difference(set(self.ta.unmatched_tss))) / (len(self.tss) - len(self.ta.unmatched_tss)) <= freq_max

    def get_seq_symbols(self, edge):
        seq_symbols = dict()
        for ts, ixs in edge.tss.items():
            # check reconstructed version first
            seq = self.ta.corrected_tss.get(ts)
            if seq is None:
                seq = self.tss_objects[ts] # no reconstruction? use the base word then
            for ix in ixs:
                penultimate = seq.get_penultimate(ix[0])
                if not penultimate: continue
                seq_symbols.setdefault(penultimate, {}).setdefault((seq.get_symbol(ix[0]-1), seq.get_edge(ix[0])), []).append(seq.get_value(ix[0]-1))

        return seq_symbols

    def __edges_merge(self, edge_1: Edge, edge_2: Edge) -> None:
        """
        Merge two edges
        Args:
            edge_1 (Edge): First edge to merge
            edge_2 (Edge): Second edge to merge
        """
        if edge_2 not in self.ta.edges or edge_1 not in self.ta.edges:
            return
        if self.debug:
            print('Merging following edges:')
            edge_1.print()
            edge_2.print()
        # self.ta.save_img(filename="img" + str(self.cpt), bedge=[edge_1, edge_2], color="firebrick"); self.cpt += 1
        edge_1.guard += edge_2.guard
        edge_1.rec_guard += edge_2.rec_guard
        edge_1.id = max([e.id for e in self.ta.edges]) + 1
        for ts, ixs in edge_2.tss.items():
            if ts in edge_1.tss.keys():
                edge_1.tss[ts] += edge_2.tss[ts]
            else:
                edge_1.tss[ts] = edge_2.tss[ts]
            for ix in ixs:
                if ts in self.ta.unmatched_tss:
                    self.ta.corrected_tss[ts].edge_sequence[ix[0]] = edge_1
                else:
                    self.tss_objects[ts].edge_sequence[ix[0]] = edge_1
        self.ta.edges.remove(edge_2)
        edge_2.destination.del_edge(edge_2, 'in')
        edge_2.source.del_edge(edge_2, 'out')
        self.ta.update_probas()
        # self.ta.save_img(filename="img" + str(self.cpt), bedge=[edge_1], color="firebrick"); self.cpt += 1

    def __determinize_prefix(self, edge: Edge, timed: bool) -> None:  # after each merge
        """
        If merging two states induced a determinism issue in the prefix, solves it
        Args:
            edge (Edge): An incomming edge of a merged state
            timed (bool): True if time values should be taken into consideration
        """
        while True:
            edges = edge.source.search_edges(edge.symbol, 'out').copy()
            if timed:
                for e in edge.source.search_edges(edge.symbol, 'out'):
                    overlaps = False
                    for other in [e for e in edges if e != e]:
                        if self.__overlaps(e.guard, other.guard): overlaps = True
                    if overlaps: edges.remove(e)
            if len(edges) < 2: return
            state_1, state_2 = edges[0].destination, edges[1].destination
            if state_1 == state_2: self.__edges_merging(state_1, timed)
            else: self.__state_merging(state_1, state_2)
            if edge not in self.ta.edges: return

    @staticmethod
    def __overlaps(list_1: list, list_2: list) -> bool:
        """
        Tests if two lists overlap
        Args:
            list_1 (list[int]): First list
            list_2 (list[int]): Second list
        Returns:
            bool: True if the two lists overlap
        """
        return np.any(np.min(np.concatenate((np.max(list_1,axis=0,keepdims=True),np.max(list_2,axis=0,keepdims=True)),axis=0),axis=0) - np.max(np.concatenate((np.min(list_1,axis=0,keepdims=True),np.min(list_2,axis=0,keepdims=True)),axis=0),axis=0) >= 0)

    def __edges_merging(self, state: State, timed) -> None:
        """
        Merge the edges having "state" as destination and with the same source and the same symbol\n
        Args:
            state (State): The destination state of the edges to merge
        """
        for symbol in self.ta.symbols:
            edges = state.search_edges(symbol, 'in')
            if len(edges) > 1:
                edges_per_state = dict()
                for edge in edges: edges_per_state.setdefault(edge.source, []).append(edge)
                edges_per_state = {k: v for k, v in edges_per_state.items() if len(v) > 1}
                for source, edges in edges_per_state.items():
                    while len(edges) > 1:
                        self.__edges_merge(edges[0], edges[1])
                        self.__determinize_prefix(edges[0], timed)
                        edges.remove(edges[1])

    def __state_merging(self, state_1: State, state_2: State, timed:bool=True) -> Union[State, None]:
        """
        Merges two states
        Args:
            state_1 (State): First state to merge
            state_2 (State): Second state to merge
            timed (:obj:`bool`, optional): True if time should be taken into consideration, True by default
        Returns:
            Union[State, None]: The state resultant of the merge, None if no merge
        """
        if state_1 not in self.ta.states or state_2 not in self.ta.states:
            return
        if eval(state_1.name[1:]) < eval(state_2.name[1:]):
            old_state, new_state = state_2, state_1
        else:
            old_state, new_state = state_1, state_2
        # self.ta.save_img(filename="img" + str(self.cpt), bstate=[old_state, new_state], color="firebrick"); self.cpt += 1
        old_state.rank = new_state.rank = min(old_state.rank, new_state.rank)
        for edge in old_state.edges_in:
            edge.destination = new_state
            new_state.add_edge(edge, 'in')
        for edge in old_state.edges_out:
            edge.source = new_state
            new_state.add_edge(edge, 'out')
        for ts in old_state.tss.keys():
            if ts in new_state.tss.keys():
                new_state.tss[ts] += old_state.tss[ts]
            else:
                new_state.tss[ts] = old_state.tss[ts]
        new_state.id = max([e.id for e in self.ta.states]) + 1
        self.ta.states.remove(old_state)
        if old_state.accepting: new_state.accepting = True
        new_state.acc_nb += old_state.acc_nb
        self.ta.update_probas()
        self.operations["merges"] += 1
        # self.ta.save_img(filename="img" + str(self.cpt), bstate=[new_state], color="firebrick"); self.cpt += 1
        return new_state

    def __import_tss(self, tss_path: str, tss: list) -> list:
        """
        Imports the timed strings for the learning process
        Args:
            tss_path (str): Path to the file containing the timed strings
            tss (list[str]): python list containing the timed strings
        Returns:
            list[str]: List of timed strings
        """
        if tss is None:
            tss_file = open(tss_path)
            tss = tss_file.readlines()
            tss_file.close()
        mem = []
        for ts in tss:
            ts = ts.rstrip() # remove trailing spaces if any
            ts = re.sub('\\n', '', ts)
            ts = ts.split(' ')
            if "$" not in ''.join(ts):
                mem.append(ts + ["$"])
            else:
                mem.append(ts)
        return mem

    def delete_subpart(self, current_edge):
        changed = list()
        edges_to_del = [current_edge]
        states_to_del = list()
        tss_to_del = [ts for ts in current_edge.tss.keys()]
        for index in tss_to_del:
            reconstructed = bool(index in self.ta.unmatched_tss)
            ts = self.ta.corrected_tss[index] if reconstructed else self.tss_objects[index]
            for i, edge in enumerate(ts.edge_sequence):
                if index in edge.tss:
                    edge.tss.pop(index)
                if len(edge.tss) == 0:
                    edges_to_del.append(edge)
                if reconstructed: edge.rec_guard.remove(ts.get_value(i))
                else: edge.guard.remove(ts.get_value(i))
                for state in [edge.source, edge.destination]:
                    if index in state.tss:
                        state.tss.pop(index)
                        if len(state.tss) == 0:
                            states_to_del.append(state)
                    changed.append(state.id)
            if not reconstructed:
                ts.recognized = False
            #ts.edge_sequence = list()
        for e in set(edges_to_del):
            e.source.del_edge(e, "out")
            e.destination.del_edge(e, "in")
            self.ta.edges.remove(e)
        for s in set(states_to_del):
            # if s.initial: continue # TODO: add tss to initial state
            self.ta.states.remove(s)
        # final = self.ta.search_state('SINK')
        # if len(final.edges_in) == 0:
        #     self.ta.states.remove(final)
        self.ta.unmatched_tss.update(tss_to_del)
        self.ta.update_probas()
        return changed


    def split_partition(self, state: State) -> list:
        """
        Output a partition of the incoming edges.
        Returns "None" if no partition should be performed.
        Otherwise, returns a list of (str, float, float, str), where the first str is a symbol of the parent, the first float is the mean, the second float is the variance of the normal distribution of the value and the second str is the name of the source state. The first str can be None if it is before the first letter of the word.
        """

        # in that case, we are sure it’s not a good idea to split the node
        # edges_in_nb = 1 if state.initial else 0
        # edges_in_nb += len(state.edges_in)
        edges_in_nb = len(state.edges_in)
        # if len(state.edges_out) <= 1:
        #     return None

        seq_symbols = {}
        for e in state.edges_out:
            for source, d in self.get_seq_symbols(e).items():#e.seq_symbols.items():
                for (y_val,x_val),v in d.items():
                    key = (y_val,x_val,source.name)
                    # print("k,v",key,v)
                    l = seq_symbols.get(key, [])
                    seq_symbols[key] = l + v

        initial_set = []

        marginal_ys = {} # dict. key: (y value, source name). value: (list of values, list of x values)
        for (y_val,x_val,source),v in seq_symbols.items():
            key = (y_val,source)
            if marginal_ys.get(key) is None:
                marginal_ys[key] = [[], []]
            marginal_ys[key][0] += v
            marginal_ys[key][1] += [x_val]*len(v)

        # print("Marginal y:")
        # for k, v in marginal_ys.items():
        #     print(k,v[0],v[1])

        for (y,source),(vl,xl) in marginal_ys.items():
            assert len(vl) > 0
            if len(vl) == 1 or source == state.name: # don’t use Gaussian mixture if there is only one sample OR SELF-LOOP
                if len(vl) == 1:
                    covar = 1e-6*np.identity(len(vl[0]))
                else:
                    covar = np.cov(vl, rowvar=0) + 1e-6*np.identity(len(vl[0]))
                initial_set.append((y, np.mean(vl, axis=0), covar, xl, source))
            else:
                best_bic = None
                best_model = None
                best_labels = None
                random.seed(42)
                matrix_vl = np.asarray([[v+random.random()-0.5 for v in l] for l in vl]) # introduce some uniform noise to simulate floats instead of integers
                for i in range(4): # at most four components
                    if i+1 > len(vl): # at most as many components as the number of points
                        break
                    m = GaussianMixture(n_components=i+1, random_state=42)
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        labels = m.fit_predict(matrix_vl)
                    bic = m.bic(matrix_vl)
                    if best_bic is None or best_bic > bic:
                        best_model = m
                        best_bic = bic
                        best_labels = labels
                for i,m in enumerate(best_model.means_):
                    covar = best_model.covariances_[i]
                    for k,val in enumerate(covar.diagonal()):
                        covar[k,k] = max(1e-6,val-1/12) # remove the noise introduced in the data
                    min_eg = min(np.linalg.eigvals(covar))
                    if min_eg <= 1e-6:
                        covar = covar - (min_eg-1e-6) * np.identity(len(m)) # ensure the matrix is positive definite
                    initial_set.append((y, np.round(m), covar, [xl[j] for (j,v) in enumerate(best_labels) if v == i], source))
                    # Y symbol, mean, variance, values of x associated with this triplet

        mean_edge_cost = model_cost(self.ta) / len(self.ta.edges)
        partition = [initial_set]

        new_edges_in_nb = len(initial_set)
        # assert new_edges_in_nb >= edges_in_nb

        best_score = 0 # the status quo (no split) has a score of 0
        while True:
            if len(partition[0]) == 1: # we don’t want to end up with an empty set
                break
            best_partition = None
            for index,tupl in enumerate(partition[0]):
                # try to remove a tuple from the initial set
                for i in range(len(partition)):
                    cand_partition = copy.deepcopy(partition)
                    cand_partition[0].pop(index)
                    if i == 0: # don’t add to the initial_set but create a new one
                        cand_partition.append([tupl])
                    else:
                        cand_partition[i].append(tupl)
                    score = self.__get_score(cand_partition)
                    score -= (len(cand_partition) * (new_edges_in_nb - edges_in_nb) + (len(cand_partition) - 1) * len(state.edges_out)) * mean_edge_cost # penalty for each new edge
                    # print("Score:",score)
                    if score > best_score:
                        best_score = score
                        best_partition = cand_partition
                        # print("New best score",score)
            if best_partition is None:
                break # seems like we converged
            else:
                partition = best_partition

        filtered_partition = [[(y,m,v,source) for (y,m,v,_,source) in s] for s in partition]
        # print("Proposed partition:",filtered_partition)
        if len([ll for l in filtered_partition for ll in l]) == 1: return None
        return filtered_partition

    def __get_score(self, partition):
        joint_xf = {}
        marginal_f = {}
        marginal_x = {}
        total = 0
        for i,s in enumerate(partition):
            for (_,_,_,xl,_) in s:
                marginal_f[i] = marginal_f.get(i, 0) + len(xl)
                x_vals, counts = np.unique(xl, return_counts=True)
                for j,x in enumerate(x_vals):
                    k = (x, i)
                    joint_xf[k] = joint_xf.get(k, 0) + counts[j]
                    marginal_x[x] = marginal_x.get(x, 0) + counts[j]
                total += len(xl)

        mutual_information = 0
        for (x,i),pxf in joint_xf.items():
            pxf = pxf / total
            px = marginal_x[x] / total
            pf = marginal_f[i] / total
            mutual_information += pxf * math.log2(pxf/(px*pf))

        # print("Mutual information:",mutual_information)

        assert mutual_information >= 0

        return total*mutual_information

    def __merge_mdl(self, state_1:State, state_2:State, timed:bool=True, merge_history=None) -> None:
        """
        Merge two states and determinization process
        Args:
            state_1 (State): First state to merge
            state_2 (State): Second state to merge
            timed (:obj:`bool`, optional): True if time should be taken into consideration, True by default

        Returns:

        """
        if merge_history is None: merge_history = set()
        merge_history.add((state_1.id, state_2.id))
        state = self.__state_merging(state_1, state_2, timed)
        res = state.undeterministic_edge_destination(False)
        deterministic = False if len(res) > 0 else True
        while not deterministic:
            if res[0] == res[1]:
                self.__edges_merging(res[0], timed)
            else:
                merge_history.add((res[0].id, res[1].id))
                merge_history.update(self.__merge_mdl(res[0], res[1], timed, merge_history))
            if state not in self.ta.states: return merge_history # state re-merged during the determinization process
            res = state.undeterministic_edge_destination(False)
            deterministic = False if len(res) > 0 else True
        return merge_history

    def __solve_undeterminism_mdl(self, timed, merge_history):
        complete = False
        while not complete:
            complete = True
            for state in self.ta.states:
                if len(state.undeterministic_edge_destination(timed)) > 0:
                    res = state.undeterministic_edge_destination(timed)
                    if res[0] == res[1]:
                        self.__edges_merging(res[0], timed)
                        complete = False
                    else:
                        merge_history.add((res[0].id, res[1].id))
                        merge_history.update(self.__merge_mdl(res[0], res[1], timed, merge_history))
                        complete = False
        return merge_history

    def split_mdl(self, partition, state, merge_mixture=False):
        # partition est une list de list de tuple (symbol, mu, sigma, source_state) correspondant acutuellement à des transtions arrivant sur un même état
        if all(len(p) == 0 for p in partition): return

        old_transitions = state.edges_in + state.edges_out
        new_states = dict()
        new_transitions = dict()
        tss_partition = {k: {} for k in range(len(partition))}

        # partition the tss
        in_a_self_loop = {}
        starting_sequences = {} # for initial state
        for ts, ixs in state.tss.items(): # TODO: check that comes from somewhere else
            reconstructed = bool(ts in self.ta.unmatched_tss)
            ts_obj = self.ta.corrected_tss[ts] if reconstructed else self.tss_objects[ts]
            for ix in ixs:
                if ix[0] == -1:
                    starting_sequences[ts] = [ix]
                    continue
                if ix[0]-1 in [a[0] for a in ixs]:
                    in_a_self_loop.setdefault(ts, []).append(ix)
                    continue
                s, tv = ts_obj.get_symbol(ix[0]), ts_obj.get_value(ix[0])
                max_prob = [-1, None, None]
                for g_id, group in enumerate(partition):
                    for t_id, (symbol, mu, sigma, source) in enumerate(group):
                        if symbol != s: continue
                        if ts not in self.ta.search_state(source).tss or (ix[0]-1, ts_obj.get_global_clock_value(ix[0]-1)) not in self.ta.search_state(source).tss[ts]: continue
                        dist = scipy.stats.multivariate_normal(mu, sigma, allow_singular=True)
                        precision = 1e-0
                        lower = [floor((value - precision/2) / precision) * precision + precision / 2 for value in tv]
                        upper = [v + precision for v in lower]
                        p = dist.cdf(upper) - dist.cdf(lower)
                        if max_prob[0] < p:
                            max_prob = [p, g_id, t_id]
                tss_partition[max_prob[1]].setdefault(max_prob[2], {}).setdefault(ts, []).append(ix)

        if state.initial:
            new_states['initial'] = state

        for g_id, group in enumerate(partition):
            name = 'S' + str(self.ta.next_state_index())
            new_state = self.ta.add_state(name, state.accepting, False)
            new_states[g_id] = new_state # create the new states
        # won't work if self loop splitted and put in multiple groups
        for self_edge in [e for e in state.edges_out if e.source == e.destination]: # self loop states
            name = 'S' + str(self.ta.next_state_index())
            self_loop_state = self.ta.add_state(name, state.accepting, False)
            new_states[self_edge] = self_loop_state

        for self_edge in [e for e in state.edges_out if e.source == e.destination]:
            self_loop_state = new_states[self_edge]
            for key, new_state in new_states.items():
                # if key == 'initial': continue # TODO: not sure about this
                if new_state == self_loop_state: continue
                if not isinstance(key, Edge): # for self loop states, no need
                    e = self.ta.add_edge(self_loop_state.name, new_state.name, self_edge.symbol, guard=[])
                    new_transitions.setdefault('no_trace', []).append(e)
                e = self.ta.add_edge(new_state.name, self_loop_state.name, self_edge.symbol, guard=[])
                new_transitions.setdefault('no_trace', []).append(e)
                for e in [e for e in state.edges_out if e.source != e.destination and len(e.tss) > 0]:
                    new_e = self.ta.add_edge(self_loop_state.name, e.destination.name, e.symbol, guard=[])
                    new_transitions.setdefault(e, []).append(new_e)

        for g_id, group in enumerate(partition):
            new_state = new_states[g_id]
            for t_id, (symbol, mu, sigma, source) in enumerate(group):
                if source == state.name: # self loop
                    continue
                else:
                    e = self.ta.add_edge(source, new_state.name, symbol, guard=[]) # create the new transitions toward the splitted states
                new_transitions.setdefault('no_trace', []).append(e)

                if t_id not in tss_partition[g_id]: continue # self transition
                for ts, ixs in tss_partition[g_id][t_id].items():
                    reconstructed = bool(ts in self.ta.unmatched_tss)
                    ts_obj = self.ta.corrected_tss[ts] if reconstructed else self.tss_objects[ts]
                    for ix in ixs:
                        s, tv = ts_obj.get_symbol(ix[0]), ts_obj.get_value(ix[0])
                        if reconstructed: e.rec_guard.append(tv)
                        else: e.guard.append(tv)
                        e.tss.setdefault(ts, []).append(ix)
                        old_edge = ts_obj.edge_sequence[ix[0]]
                        old_edge.tss[ts].remove(ix)
                        old_edge.destination.tss[ts].remove(ix)
                        if len(old_edge.tss[ts]) == 0: old_edge.tss.pop(ts)
                        if len(old_edge.destination.tss[ts]) == 0: old_edge.destination.tss.pop(ts)
                        if reconstructed: old_edge.rec_guard.remove(tv)
                        else: old_edge.guard.remove(tv)
                        ts_obj.edge_sequence[ix[0]] = e
                        new_state.tss.setdefault(ts, []).append(ix)

            for e in state.edges_out:
                if e.destination == state:
                    continue #e = self.ta.add_edge(new_state.name, new_state.name, e.symbol, guard=[])
                else:
                    new_e = self.ta.add_edge(new_state.name, e.destination.name, e.symbol, guard=[])  # create the new transitions from the splitted states, some will be removed later
                    new_transitions.setdefault(e, []).append(new_e)
                for ts, ixs in new_state.tss.items():
                    reconstructed = bool(ts in self.ta.unmatched_tss)
                    ts_obj = self.ta.corrected_tss[ts] if reconstructed else self.tss_objects[ts]
                    for ix in ixs:
                        if ts not in e.tss or ix[0]+1 not in [a for (a, b) in e.tss[ts]]: continue # only add to relevant edge
                        s, tv = ts_obj.get_symbol(ix[0]+1), ts_obj.get_value(ix[0]+1)
                        if reconstructed: new_e.rec_guard.append(tv)
                        else: new_e.guard.append(tv)
                        new_e.tss.setdefault(ts, []).append((ix[0]+1, ts_obj.get_global_clock_value(ix[0]+1)))
                        old_edge = ts_obj.edge_sequence[ix[0]+1]
                        old_edge.tss[ts].remove((ix[0]+1, ts_obj.get_global_clock_value(ix[0]+1)))
                        if len(old_edge.tss[ts]) == 0: old_edge.tss.pop(ts)
                        if reconstructed: old_edge.rec_guard.remove(tv)
                        else: old_edge.guard.remove(tv)
                        ts_obj.edge_sequence[ix[0]+1] = new_e

        def intervals_extract(iterable):
            iterable = sorted(set(iterable))
            for key, group in itertools.groupby(enumerate(iterable),
                                                lambda t: t[1] - t[0]):
                group = list(group)
                yield [group[0][1], group[-1][1]]

        for ts, ixs in in_a_self_loop.items():
            for cycles in list(intervals_extract([a for a, b in ixs])):
                for i, occ in (enumerate(range(cycles[0], cycles[1]+1))):
                    ix = [ix for ix in ixs if ix[0] == occ][0]
                    # case 1: impair not from another self loop
                    if i == 0:
                        source_state = [s for s in new_states.values() if ts in s.tss and ix[0]-1 in [a for a, b in s.tss[ts]]][-1]
                        self_edge = [e for e in old_transitions if ts in e.tss and ix[0] in [a for (a, b) in e.tss[ts]]][0]
                        dest_state = new_states[self_edge]
                    # case 2: pair from the same loop
                    else:
                        source_state = [s for s in new_states.values() if ts in s.tss and ix[0] - 1 in [a for a, b in s.tss[ts]]][-1]
                        self_edge = [e for e in old_transitions if ts in e.tss and ix[0] in [a for (a, b) in e.tss[ts]]][0]
                        self_loop_state = new_states[self_edge]
                        if source_state != self_loop_state:
                            dest_state = self_loop_state
                        else:
                            dest_state = [s for s in self.ta.states if ts in s.tss and cycles[0]-1 in [a for (a, b) in s.tss[ts]]][-1] # TODO: check

                    reconstructed = bool(ts in self.ta.unmatched_tss)
                    ts_obj = self.ta.corrected_tss[ts] if reconstructed else self.tss_objects[ts]

                    t = [t for t in [ll for l in new_transitions.values() for ll in l] if t.destination == dest_state and t.source == source_state][0]
                    s, tv = ts_obj.get_symbol(ix[0]), ts_obj.get_value(ix[0])

                    if reconstructed: t.rec_guard.append(tv)
                    else: t.guard.append(tv)
                    t.tss.setdefault(ts, []).append(ix)

                    old_edge = ts_obj.edge_sequence[ix[0]]
                    old_edge.tss[ts].remove(ix)
                    if len(old_edge.tss[ts]) == 0: old_edge.tss.pop(ts)
                    old_edge.destination.tss[ts].remove(ix)
                    if len(old_edge.destination.tss[ts]) == 0: old_edge.destination.tss.pop(ts)
                    if reconstructed: old_edge.rec_guard.remove(tv)
                    else: old_edge.guard.remove(tv)

                    ts_obj.edge_sequence[ix[0]] = t

                    dest_state.tss.setdefault(ts, []).append(ix)  # TODO: check if not already done (seems good)
                # future transition at the end of the cycle
                old_edge = [e for e in old_transitions if ts in e.tss and ix[0]+1 in [a for (a, b) in e.tss[ts]]][0]
                if dest_state != state:
                    reconstructed = bool(ts in self.ta.unmatched_tss)
                    ts_obj = self.ta.corrected_tss[ts] if reconstructed else self.tss_objects[ts]
                    next_edge = [e for e in new_transitions[old_edge] if e.source == dest_state][0]
                    #next_edge = new_transitions[old_edge][0]
                    next_s, next_tv = ts_obj.get_symbol(ix[0]+1), ts_obj.get_value(ix[0]+1)

                    if reconstructed: next_edge.rec_guard.append(next_tv)
                    else: next_edge.guard.append(next_tv)
                    next_edge.tss.setdefault(ts, []).append((ix[0]+1, ts_obj.get_global_clock_value(ix[0]+1)))

                    old_edge = ts_obj.edge_sequence[ix[0]+1]
                    old_edge.tss[ts].remove((ix[0]+1, ts_obj.get_global_clock_value(ix[0]+1)))
                    if len(old_edge.tss[ts]) == 0: old_edge.tss.pop(ts)
                    if reconstructed: old_edge.rec_guard.remove(next_tv)
                    else: old_edge.guard.remove(next_tv)

                    ts_obj.edge_sequence[ix[0] + 1] = next_edge

        if state.initial:
            for ts in starting_sequences.keys():
                reconstructed = bool(ts in self.ta.unmatched_tss)
                ts_obj = self.ta.corrected_tss[ts] if reconstructed else self.tss_objects[ts]
                edge = ts_obj.edge_sequence[0]
                ix_to_remove = [ix for ix in edge.tss[ts] if ts_obj.edge_sequence[ix[0]] != edge]
                for ix in ix_to_remove:
                    if reconstructed: edge.rec_guard.remove(ts_obj.get_value(ix[0]))
                    else: edge.guard.remove(ts_obj.get_value(ix[0]))
                edge.tss[ts] = [ix for ix in edge.tss[ts] if ts_obj.edge_sequence[ix[0]] == edge] #[ix for ix in edge.tss[ts] if ix[0] == 0]

        # delete unused outgoing transitions
        for v in new_transitions.values():
            for e in v:
                if len(e.tss) == 0: old_transitions.append(e)

        # delete state and old transitions
        if not state.initial:
            self.ta.states.remove(state)
        for s in new_states.values():
            if len(s.tss) == 0:
                self.ta.states.remove(s)
        for old_edge in set(old_transitions):
            if not old_edge.source.initial or (old_edge.source.initial and len(old_edge.tss) == 0):
                old_edge.source.del_edge(old_edge, 'out')
                old_edge.destination.del_edge(old_edge, 'in')
                self.ta.edges.remove(old_edge)

        self.ta.update_probas()

        assert len([s for s in self.ta.states if len(s.edges_out) == 0]) == 1

        if merge_mixture:
            for state in new_states.values(): self.edges_merging_mixture(state)

        assert len([s for s in self.ta.states if len(s.edges_out) == 0]) == 1

    def split_edge(self, edge):
        # print("New split edge:", edge.source.name, "->", edge.destination.name)
        nb_out = len(edge.destination.edges_out)
        nb_in = len(edge.source.edges_in)
        # print("Out of {edge.destination.name}:", nb_out)
        # print("In of {edge.source.name}:", nb_in)

        ts_occs_ordered = [(ts, ix) for ts, ixs in edge.tss.items() for ix in ixs] # this way we are sure of the order of the values
        vl = [self.tss_objects[ts].get_value(ix[0]) for ts, ix in ts_occs_ordered] # this way we are sure of the order of the values # vl = edge.guard
        assert len(vl) > 0
        if len(vl) == 1 or edge.source == edge.destination:  # don’t use Gaussian mixture if there is only one sample or self-loop
            return None

        best_bic = None
        best_labels = None
        random.seed(42)
        matrix_vl = np.asarray([[v + random.gauss() for v in l] for l in
                                vl])  #  introduce some noise to simulate floats instead of integers
        for i in range(4):  # at most four components
            if i + 1 > len(vl):  # at most as many components as the number of points
                break
            m = GaussianMixture(covariance_type="diag", n_components=i + 1, random_state=42)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                labels = m.fit_predict(matrix_vl)
            bic = m.aic(matrix_vl)
            if best_bic is None or best_bic > bic:  # we want to minimize the BIC score
                best_bic = bic
                best_labels = labels
        distinct_labels = set(best_labels)
        if len(distinct_labels) == 1:  # the best model puts all the values inside the same Gaussian distribution: abort
            return None
        assert nb_out == len(edge.destination.edges_out)
        assert nb_in == len(edge.source.edges_in)

        # create the new edges
        new_edges = list()
        for l in distinct_labels:
            new_edges.append(self.ta.add_edge(edge.source.name, edge.destination.name, edge.symbol, list()))

        for i, label in enumerate(best_labels):
            e = new_edges[label]
            ts, ix = ts_occs_ordered[i]
            e.guard.append(vl[i]) # add ts to new edge
            e.tss.setdefault(ts, []).append(ix)

            self.tss_objects[ts].edge_sequence[ix[0]] = e # update ts information

        assert nb_out == len(edge.destination.edges_out)
        assert nb_in == len(edge.source.edges_in)
        # remove after adding new edges, so at no point the states have no edges
        edge.source.del_edge(edge, "out")
        edge.destination.del_edge(edge, "in")
        self.ta.edges.remove(edge)
        # print("Remove edge", edge.id)
        self.ta.update_probas()
        assert nb_out == len(edge.destination.edges_out)
        assert nb_in == len(edge.source.edges_in)
        # print("Recommend split!")
        random.seed()
        nb = random.randrange(20)
        # print("Export nb:", nb)
        self.ta.export_ta("out" + str(nb) + ".dot", guard_as_distrib=True)
        # print("Should be empty:", [e for e in self.ta.edges if len(e.tss) == 0])
        return True

    def edges_merging_mixture(self, state):
        transitions = state.edges_in

        # Process each group until no more merges can be performed
        while True:
            merged_any = False

            # Group transitions by symbol and state
            grouped_transitions = defaultdict(list)
            for t in transitions:
                grouped_transitions[(t.symbol, t.source)].append(t)

            # Process each group
            for (symbol, src_state), trans_list in grouped_transitions.items():
                if len(trans_list) == 1:
                    # Only one transition, no need to merge
                    continue

                # Sort transitions by mu
                trans_list.sort(key=lambda t: t.mu)

                # Check if there are transitions with the same symbol going to different states
                i = 0
                while i < len(trans_list) - 1:
                    t1 = trans_list[i]
                    t2 = trans_list[i + 1]

                    # Check for other transitions with the same symbol and mu between t1 and t2
                    has_intermediate = any(
                        t.symbol == symbol and t.mu > t1.mu and t.mu < t2.mu and t.destination != t1.destination
                        for t in state.edges_out
                    )

                    if not has_intermediate:
                        self.__edges_merge(t1, t2)
                        self.ta.update_probas()
                        transitions = state.edges_in
                        merged_any = True
                        break  # Restart processing after merge
                    else:
                        i += 1

                if merged_any:
                    break  # Restart processing after merge

            if not merged_any:
                break  # Exit loop if no merges were performed

    def build_SymbolBasedDFA(self):
        states_symbols = {}
        state_index = 1
        for i in range(0, len(self.tss)):
            last = 'S0'
            self.ta.search_state(last).tss[i] = [(-1, [0]*self.ta.number_of_values)]
            gtime = None
            for index, pair in enumerate(self.tss[i]):
                s, d = self.data_parser(pair)
                if gtime is None:
                    gtime = d
                else:
                    gtime = [a + b for a, b in zip(gtime, d)]
                if s not in self.ta.symbols: self.ta.symbols.append(s)
                res = self.ta.next_edge(last, s)
                if res is None:
                    if s == "$":
                        next = "SINK"
                    else:
                        if s in states_symbols.keys():
                            next = states_symbols[s]
                        else:
                            next = 'S' + str(state_index)
                            states_symbols[s] = next
                            state_index += 1
                    edge = self.ta.add_edge(last, next, s, [d])
                    edge.tss[i] = [(index, gtime)]
                    self.tss_objects[i].edge_sequence.append(edge)
                    self.ta.search_state(next).rank = index
                else:
                    next = res.destination.name
                    res.guard.append(d)
                    self.tss_objects[i].edge_sequence.append(res)
                    if i in res.tss.keys():
                        res.tss[i].append((index, gtime))
                    else:
                        res.tss[i] = [(index, gtime)]
                if i in self.ta.search_state(next).tss.keys():
                    self.ta.search_state(next).tss[i].append((index, gtime))
                else:
                    self.ta.search_state(next).tss[i] = [(index, gtime)]
                if index == len(self.tss[i]) - 1:
                    dest_state = self.ta.search_state(next)
                    dest_state.accepting = True
                    dest_state.acc_nb += 1
                last = next
        self.ta.update_probas()

    def build_UniversalFA(self):
        for i in range(0, len(self.tss)):
            last = 'S0'
            state_obj = self.ta.states[0]
            state_obj.tss[i] = [(-1, [0]*self.ta.number_of_values)]
            gtime = None
            for index, pair in enumerate(self.tss[i]):
                s, d = self.data_parser(pair)
                if gtime is None:
                    gtime = d
                else:
                    gtime = [a + b for a, b in zip(gtime, d)]
                if s not in self.ta.symbols: self.ta.symbols.append(s)
                res = self.ta.next_edge(last, s)
                if res is None:
                    if s == "$":
                        next = "SINK"
                    else:
                        next = 'S0'
                    edge = self.ta.add_edge(last, next, s, [d])
                    edge.tss[i] = [(index, gtime)]
                    self.tss_objects[i].edge_sequence.append(edge)
                    self.ta.search_state(next).rank = index
                else:
                    next = res.destination.name
                    res.guard.append(d)
                    self.tss_objects[i].edge_sequence.append(res)
                    if i in res.tss.keys():
                        res.tss[i].append((index, gtime))
                    else:
                        res.tss[i] = [(index, gtime)]
                if i in self.ta.search_state(next).tss.keys():
                    self.ta.search_state(next).tss[i].append((index, gtime))
                else:
                    self.ta.search_state(next).tss[i] = [(index, gtime)]
                if index == len(self.tss[i]) - 1:
                    dest_state = self.ta.search_state(next)
                    dest_state.accepting = True
                    dest_state.acc_nb += 1
                last = next
        self.ta.update_probas()

    def __build_apta(self) -> None:
        """
        Initialize the automaton with one possible path per word \n
        """
        state_index = 1
        for i in range(0, len(self.tss)):
            last = 'S0'
            self.ta.search_state(last).tss[i] = [(-1,  [0]*self.ta.number_of_values)]
            gtime = None
            for index, pair in enumerate(self.tss[i]):
                s, d = self.data_parser(pair)
                if gtime is None:
                    gtime = d
                else:
                    gtime = [a + b for a, b in zip(gtime, d)]
                if s not in self.ta.symbols: self.ta.symbols.append(s)
                res = self.ta.next_edge(last, s)
                if res is None:
                    if s == "$":
                        next = "SINK"
                    else:
                        next = 'S' + str(state_index)
                        state_index += 1
                    edge = self.ta.add_edge(last, next, s, [d])
                    edge.tss[i] = [(index, gtime)]
                    self.tss_objects[i].edge_sequence.append(edge)
                    self.ta.search_state(next).rank = index
                else:
                    next = res.destination.name
                    res.guard.append(d)
                    self.tss_objects[i].edge_sequence.append(res)
                    if i in res.tss.keys():
                        res.tss[i].append((index, gtime))
                    else:
                        res.tss[i] = [(index, gtime)]
                if i in self.ta.search_state(next).tss.keys():
                    self.ta.search_state(next).tss[i].append((index, gtime))
                else:
                    self.ta.search_state(next).tss[i] = [(index, gtime)]
                if index == len(self.tss[i]) - 1:
                    dest_state = self.ta.search_state(next)
                    dest_state.accepting = True
                    dest_state.acc_nb += 1
                last = next
        self.ta.update_probas()
