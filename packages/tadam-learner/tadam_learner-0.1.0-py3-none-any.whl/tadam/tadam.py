import copy
import os
import time
from datetime import datetime
from itertools import combinations
from multiprocessing import Pool
import re

import numpy as np

from tadam.options import GuardsFormat, Init
from tadam.edge import EndingEdge
from tadam.mdl import model_cost, data_cost
from tadam.state import EndingState
from tadam.talearner import TALearner
from tadam.ts import TS

import pickle
import io

def dump_to_bytes(obj):
    """Serialize the object to a bytes object using BytesIO."""
    byte_stream = io.BytesIO()  # Create an in-memory bytes buffer
    pickle.dump(obj, byte_stream)  # Serialize the object to the buffer
    return byte_stream.getvalue()  # Return the bytes object from the buffer

def load_from_bytes(bytes_obj):
    """Deserialize the object from a bytes object using BytesIO."""
    byte_stream = io.BytesIO(bytes_obj)  # Create a BytesIO stream from the bytes object
    return pickle.load(byte_stream)  # Deserialize the object from the stream

def exhaustive_search(options, tss_list = None, verbose=False, ta=None, tss_objects=None, logfile=None, cpu_nb=os.cpu_count() - 1, noise_model=None, parallelized=True, on_iter=None):
    """

    :param options: option object
    :param tag_init: True if initialization of the TA with TAG else initialization with prefix tree
    :param verbose: True to print debugging information
    :param ta: In case of reimported TA
    :param tss_objects: In case of reimported TA
    :param logfile
    :param top_k: nb of best solutions to keep
    :return: TALearner object
    """
    use_pickle = True
    l = TALearner(tss_path=os.path.join(options.path, options.filename) if tss_list is None else None,
                  tss_list=tss_list, noise_model=noise_model,
                  data_parser=options.data_parser, donotrun=True)
    if ta is None:
        if verbose:
            print("Building initial DFA")
        if options.init == Init.STATE_SYMBOL:
            l.build_SymbolBasedDFA()
        elif options.init == Init.UNIVERSAL:
            l.build_UniversalFA()
        else: # APTA
            l._TALearner__build_apta()
    else:
        l.ta = ta
        l.tss = ta.tss
        for k, v in tss_objects.items():
            l.tss_objects[k] = TS(k, [options.data_parser(t) for t in ta.tss[k]])
            l.tss_objects[k].edge_sequence = v
    # current_model_cost = model_cost(l.ta, verbose=verbose)
    # current_data_cost = data_cost(l.ta, l.data_parser, l.noise_model, verbose=verbose)
    l.data_cost = data_cost(l.ta, l.data_parser, l.noise_model, verbose=verbose)
    l.model_cost = model_cost(l.ta, verbose=verbose)
    if options.export:
        if options.filename is None:
            folder = "tadam_" + str(int(time.time()))
        else:
            folder = options.filename + "_" + str(int(time.time()))
        os.mkdir(folder)
        l.ta.export_ta(os.path.join(folder, '0.dot'), guard_as_distrib=options.guards == GuardsFormat.DISTRIB)
    best_operation = None
    improvement = True
    i = 0
    if options.export:
        with open(os.path.join(folder, "log.txt"), "a") as f:
            f.write(f"TADAM init phase data cost={l.data_cost}, model cost={l.model_cost}\n")

    if logfile:
        with open(logfile, "r") as f:
            logs = f.readlines()
        logs = logs[1:]
        for line in logs:
            if len(line) == 0: continue
            if line[:5] == "merge":
                pattern = r"merge states (?P<state1>S\d+) & (?P<state2>S\d+), data gain=(?P<data_gain>-?\d+(\.\d+)?), model gain=(?P<model_gain>-?\d+(\.\d+)?)"
                match = re.search(pattern, line)
                best_operation = ('merge', ([s.id for s in l.ta.states if s.name == match.group('state1')][0],
                                            [s.id for s in l.ta.states if s.name == match.group('state2')][0]))
            elif line[:6] == "delete":
                pattern = r"delete edge (?P<state1>S\d+) -> (?P<state2>S(?:\d+|INK)) \((?P<id>\d+)\), data gain=(?P<data_gain>-?\d+(\.\d+)?), model gain=(?P<model_gain>-?\d+(\.\d+)?)"
                match = re.search(pattern, line)
                best_operation = ('delete', int(match.group("id")))
            if line[:5] == "split":
                pattern = r"split state (?P<state1>S\d+), data gain=(?P<data_gain>-?\d+(\.\d+)?), model gain=(?P<model_gain>-?\d+(\.\d+)?)"
                match = re.search(pattern, line)
                best_operation = ('split', [s.id for s in l.ta.states if s.name == match.group('state1')][0])
            model_gain = float(match.group('model_gain'))
            data_gain = float(match.group('data_gain'))
            l, changed = perform_best_operation(best_operation, data_gain, model_gain, l, options, folder, verbose=verbose)
            # current_model_cost = model_cost(l.ta, verbose=verbose)
            # current_data_cost = data_cost(l.ta, l.data_parser, l.noise_model, verbose=verbose)

    learners = {0: {"learner": l, "score": l.model_cost + l.data_cost, "hist":[]}}#, "model_gain": list(), "data_gain": list(), "changed": list(), "improvement": False, "best_operation": list()} for k in range(kbest)} # TODO: logs will be completly messed up
    best_model = learners[0]

    while improvement:
        if verbose: print('Current cost: ' + str(l.data_cost + l.model_cost))
        i += 1
        if verbose: print('Iter ' + str(i))
        improvement = False
        best_operations = []

        for k in learners.keys():
            l = learners[k]["learner"]

            if use_pickle:
                serialized_obj = dump_to_bytes(l)
                original_learner = load_from_bytes(serialized_obj)
            else:
                original_learner = copy.deepcopy(l)

            # SPLITS LOCATION
            if verbose: print('trying splits...')
            beg = datetime.now()
            candidate_states = [s.id for s in original_learner.ta.states if
                                s.edges_out and not isinstance(s, EndingState)]
            if use_pickle:
                candidates = [(s, serialized_obj) for s in candidate_states]
            else:
                candidates = [(s, l) for s in candidate_states]
            if parallelized:
                with Pool(cpu_nb) as p:
                    scores = p.map(try_split, candidates)
            else:
                scores = list()
                for candidate in candidates:
                    scores.append(try_split(candidate))

            best_indices = sorted(range(len(scores)), key=lambda x: sum(scores[x]))[:options.top_k]
            new_operations = list()
            for best_indice in best_indices:
                new_operations.append({'score': np.sum(scores[best_indice]),
                                       'operation': ('split', candidates[best_indice][0]),
                                       'model': original_learner,
                                       'hist': learners[k]['hist']})
            best_operations = update_k_best_operations(best_operations, new_operations, options.top_k)
            if verbose: print(datetime.now() - beg)

            # SPLITS EDGE
            if verbose: print('trying edge splits...')
            beg = datetime.now()
            candidate_edges = [e.id for e in original_learner.ta.edges]
            if use_pickle:
                candidates = [(e, serialized_obj) for e in candidate_edges]
            else:
                candidates = [(e, l) for e in candidate_edges]
            if parallelized:
                with Pool(cpu_nb) as p:
                    scores = p.map(try_edge_split, candidates)
            else:
                scores = list()
                for candidate in candidates:
                    scores.append(try_edge_split(candidate))

            best_indices = sorted(range(len(scores)), key=lambda x: sum(scores[x]))[:options.top_k]
            new_operations = list()
            for best_indice in best_indices:
                new_operations.append({'score': np.sum(scores[best_indice]),
                                       'operation': ('split_edge', candidates[best_indice][0]),
                                       'model': original_learner,
                                       'hist': learners[k]['hist']})
            best_operations = update_k_best_operations(best_operations, new_operations, options.top_k)
            if verbose: print(datetime.now() - beg)


            # STATE MERGING
            if verbose: print('trying merges...')
            beg = datetime.now()
            candidate_states = [s.id for s in original_learner.ta.states if
                                s.edges_out and not isinstance(s, EndingState)]

            if use_pickle:
                candidates = [(s1, s2, serialized_obj) for s1, s2 in combinations(candidate_states, 2)]
            else:
                candidates = [(s1, s2, l) for s1, s2 in combinations(candidate_states, 2)]
            if parallelized:
                with Pool(cpu_nb) as p:
                    scores = p.map(try_merge, candidates)
            else:
                scores = list()
                for candidate in candidates:
                    scores.append(try_merge(candidate))


            best_indices = sorted(range(len(scores)), key=lambda x: sum(scores[x]))[:options.top_k]
            new_operations = list()
            for best_indice in best_indices:
                new_operations.append({'score': np.sum(scores[best_indice]),
                                       'operation': ('merge', candidates[best_indice][:2]),
                                       'model': original_learner,
                                       'hist': learners[k]['hist']})
            best_operations = update_k_best_operations(best_operations, new_operations, options.top_k)

            if verbose: print(datetime.now() - beg)

            # SUBPART DELETION
            if verbose: print('trying del...')
            beg = datetime.now()
            candidate_edges = [e.id for e in original_learner.ta.edges if not (e.source.initial and len(e.source.edges_out) == 1)
                                                           and original_learner.is_del_interesting(e, options.del_freq_max)]  # if unique transition of the initial state
            to_del = list()
            for candidate in candidate_edges:
                if candidate in to_del: continue
                edge = [e for e in original_learner.ta.edges if e.id == candidate][0]
                while len(edge.destination.edges_out) == 1 and len(edge.destination.edges_in) == 1: # do not re-test edges that are deleted by another deletion anyway
                    edge = edge.destination.edges_out[0]
                    to_del.append(edge.id)
            candidate_edges = [c for c in candidate_edges if c not in to_del]

            if use_pickle:
                candidates = [(e, serialized_obj) for e in candidate_edges]
            else:
                candidates = [(e, l) for e in candidate_edges]
            if parallelized:
                with Pool(cpu_nb) as p:
                    scores = p.map(try_del, candidates)
            else:
                scores = list()
                for candidate in candidates:
                    scores.append(try_del(candidate))

            best_indices = sorted(range(len(scores)), key=lambda x: sum(scores[x]))[:options.top_k]
            new_operations = list()
            for best_indice in best_indices:
                new_operations.append({'score': np.sum(scores[best_indice]),
                                       'operation': ('delete', candidates[best_indice][0]),
                                       'model': original_learner,
                                       'hist': learners[k]['hist']})
            best_operations = update_k_best_operations(best_operations, new_operations, options.top_k)
            if verbose: print(datetime.now() - beg)

        for k, operation in enumerate(best_operations):
            l = operation["model"]
            if operation["score"] < l.model_cost + l.data_cost:
                if verbose:
                    print(f"Current cost: {l.model_cost + l.data_cost}")
                    print(f"New cost: {operation['score']}")
                if not options.export: folder = None
                if use_pickle:
                    new_learner, changed = perform_best_operation(operation["operation"], 0, 0, load_from_bytes(serialized_obj), options, folder, verbose=verbose)
                else:
                    new_learner, changed = perform_best_operation(operation["operation"], 0, 0, copy.deepcopy(l), options, folder, verbose=verbose)
                for_hist = operation['operation']
                if for_hist[0] == 'delete':
                    edge = [edge for edge in l.ta.edges if edge.id == operation["operation"][1]][0]
                    for_hist = [f"delete edge {edge.source.name} -> {edge.destination.name} ({operation['operation'][1]})\n"]
                elif for_hist[0] == 'split':
                    state = [state for state in l.ta.states if state.id == operation["operation"][1]][0]
                    for_hist = [f"split state {state.name}\n"]
                elif for_hist[0] == 'split_edge':
                    edge = [edge for edge in l.ta.edges if edge.id == operation["operation"][1]][0] # todo: data gain et model gain
                    for_hist = [f"split edge {edge.source.name} -> {edge.destination.name}\n"]
                elif for_hist[0] == 'merge':
                    state_1 = [state for state in l.ta.states if state.id == operation["operation"][1][0]][0]
                    state_2 = [state for state in l.ta.states if state.id == operation["operation"][1][1]][0]
                    for_hist = [f"merge states {state_1.name} & {state_2.name}\n"]
                learners[k] = {"learner": new_learner,
                               "score": new_learner.model_cost + new_learner.data_cost,
                               "hist": operation['hist'] + for_hist}
                improvement = True
            else:
                if k in learners.keys(): learners.pop(k)

        if verbose and improvement: print(for_hist[-1])
        for model in learners.values():
            if model["score"] < best_model["score"]:
                best_model = model

        if options.export and options.top_k <= 1:
            original_learner.ta.export_ta(os.path.join(folder, str(i) + '.dot'), guard_as_distrib=options.guards == GuardsFormat.DISTRIB)
        # l = copy.deepcopy(original_learner)

        if on_iter:
            on_iter(original_learner.ta)

    original_learner = best_model['learner']

    if options.export:
        if options.top_k > 1:
            with open(os.path.join(folder, "log.txt"), "a") as f:
                f.writelines(best_model['hist'])
        with open(os.path.join(folder, "log.txt"), "a") as f:
            f.write(f"Final data cost={original_learner.data_cost}, model cost={original_learner.model_cost}\n")

    if verbose:
        print("End of learning process.")

    return original_learner

def perform_best_operation(best_operation, data_gain, model_gain, original_learner, options, folder, verbose=False):
    if best_operation[0] == 'delete':
        e = best_operation[1]
        edge = [edge for edge in original_learner.ta.edges if edge.id == e][0]
        changed = original_learner.delete_subpart(edge)
        changed = set(changed)
        if options.export and options.top_k <= 1:
            with open(os.path.join(folder, "log.txt"), "a") as f:
                f.write(
                    f"delete edge {edge.source.name} -> {edge.destination.name} ({e}), data gain={data_gain}, model gain={model_gain}\n")
    elif best_operation[0] == 'merge':
        s1, s2 = best_operation[1]
        state_1 = [state for state in original_learner.ta.states if state.id == s1][0]
        state_2 = [state for state in original_learner.ta.states if state.id == s2][0]
        merge_history = original_learner._TALearner__merge_mdl(state_1, state_2, timed=True)
        merge_history = original_learner._TALearner__solve_undeterminism_mdl(True, merge_history)
        changed = set(list(sum(merge_history, ())))
        if options.export and options.top_k <= 1:
            with open(os.path.join(folder, "log.txt"), "a") as f:
                f.write(
                    f"merge states {state_1.name} & {state_2.name}, data gain={data_gain}, model gain={model_gain}\n")
    elif best_operation[0] == 'split':
        s = best_operation[1]
        state = [state for state in original_learner.ta.states if state.id == s][0]
        partition = original_learner.split_partition(state)
        changed = original_learner.split_mdl(partition, state, merge_mixture=False)
        changed = set([s.id for s in original_learner.ta.states])  # TODO: changed
        if options.export and options.top_k <= 1:
            with open(os.path.join(folder, "log.txt"), "a") as f:
                f.write(
                    f"split state {state.name}, data gain={data_gain}, model gain={model_gain}\n")
    elif best_operation[0] == 'split_edge':
        e = best_operation[1]
        edge = [edge for edge in original_learner.ta.edges if edge.id == e][0]
        changed = original_learner.split_edge(edge)
        changed = set([e.id for e in original_learner.ta.edges])  # TODO: changed
        if options.export and options.top_k <= 1:
            with open(os.path.join(folder, "log.txt"), "a") as f:
                f.write(
                    f"split edge {edge.source.name} -> {edge.destination.name} ({e}), data gain={data_gain}, model gain={model_gain}\n")
    original_learner.data_cost = data_cost(original_learner.ta, original_learner.data_parser, original_learner.noise_model, verbose=verbose)
    original_learner.model_cost = model_cost(original_learner.ta)
    return original_learner, changed

def try_merge(args):
    s1, s2, learner = args
    if isinstance(learner, bytes):
        l = load_from_bytes(learner)
    else:
        l = copy.deepcopy(learner)
    state_1 = [state for state in l.ta.states if state.id == s1][0]
    state_2 = [state for state in l.ta.states if state.id == s2][0]
    if not {e.symbol for e in state_1.edges_out}.intersection(
            {e.symbol for e in state_2.edges_out}): return (np.inf, np.inf) #(s1, s2), np.inf, np.inf, {}  # no shared edge
    merge_history = l._TALearner__merge_mdl(state_1, state_2, timed=False)
    merge_history = l._TALearner__solve_undeterminism_mdl(True, merge_history)
    l.data_cost = data_cost(l.ta, l.data_parser, l.noise_model)
    l.model_cost = model_cost(l.ta)
    return (l.model_cost, l.data_cost) #((s1, s2), ta_model_cost, ta_data_cost, merge_history)

def try_del(args):
    e, learner = args
    if isinstance(learner, bytes):
        l = load_from_bytes(learner)
    else:
        l = copy.deepcopy(learner)
    edge = [edge for edge in l.ta.edges if edge.id == e][0]
    l.delete_subpart(edge)
    if len(l.ta.states) == 0:
        return (np.inf, np.inf)
    l.data_cost = data_cost(l.ta, l.data_parser, l.noise_model)
    l.model_cost = model_cost(l.ta)
    return (l.model_cost, l.data_cost)


def try_split(args):
    s, learner = args
    if isinstance(learner, bytes):
        l = load_from_bytes(learner)
    else:
        l = copy.deepcopy(learner)
    state = [state for state in l.ta.states if state.id == s][0]
    partition = l.split_partition(state)
    if partition is not None:
        l.split_mdl(partition, state, merge_mixture=False)
        l.data_cost = data_cost(l.ta, l.data_parser, l.noise_model)
        l.model_cost = model_cost(l.ta)
        return (l.model_cost, l.data_cost)
    else:
        return (np.inf, np.inf)

def try_edge_split(args):
    e, learner = args
    if isinstance(learner, bytes):
        l = load_from_bytes(learner)
    else:
        l = copy.deepcopy(learner)
    edge = [edge for edge in l.ta.edges if edge.id == e][0]
    l.split_edge(edge)
    l.data_cost = data_cost(l.ta, l.data_parser, l.noise_model)
    l.model_cost = model_cost(l.ta)
    return (l.model_cost, l.data_cost)

def update_k_best_operations(best_operations, new_operations, k):
    """
    Update the k best operations with new operations.

    new_operations: List of dictionaries, each containing 'score', 'operation', and 'model'
    k: The number of best operations to keep
    """
    # Combine the current best operations with the new ones
    combined_operations = best_operations + new_operations
    # Sort the combined operations by score
    combined_operations.sort(key=lambda x: x['score'])
    # Keep only the k best operations
    best_operations = combined_operations[:k]
    return best_operations

def opportunistic_search(options, verbose=True, cpu_nb=os.cpu_count()-1, noise_model=None):
    use_pickle = True
    l = TALearner(tss_path=os.path.join(options.path, options.filename), noise_model=noise_model,
                  data_parser=options.data_parser, donotrun=True)

    folder = options.filename + "_" + str(int(time.time()))
    if options.export:
        folder = options.filename + "_" + str(int(time.time()))
        os.mkdir(folder)

    if verbose:
        print("Building initial DFA")
    if options.init == Init.STATE_SYMBOL:
        l.build_SymbolBasedDFA()
    elif options.init == Init.UNIVERSAL:
        l.build_UniversalFA()
    # else:  # APTA
        # l._TALearner__build_apta()

    l.data_cost = data_cost(l.ta, options.data_parser, l.noise_model)
    l.model_cost = model_cost(l.ta)

    i = 0

    if options.export:
        with open(os.path.join(folder, "log.txt"), "a") as f:
            f.write(f"TAG phase I data cost={l.data_cost}, model cost={l.model_cost}\n")
        l.ta.export_ta(os.path.join(folder, str(i) + '.dot'), guard_as_distrib=options.guards == GuardsFormat.DISTRIB)

    improvement = True

    while improvement:
        i += 1
        if verbose:
            print('Current cost: ' + str(l.data_cost + l.model_cost))
            print('Iter ' + str(i))

        if use_pickle:
            serialized_obj = dump_to_bytes(l)

        # STATE MERGING
        if verbose: print('trying merges...')
        still_candidates = True
        has_merged = False
        while still_candidates:
            candidate_states = [s.id for s in l.ta.states if
                                s.edges_out and not isinstance(s, EndingState)]
            if use_pickle:
                candidates = [(s1, s2, load_from_bytes(serialized_obj)) for s1, s2 in combinations(candidate_states, 2)]
            else:
                candidates = [(s1, s2, copy.deepcopy(l)) for s1, s2 in combinations(candidate_states, 2)]
            if len(candidates) == 0: break
            with Pool(cpu_nb) as p:
                scores = p.map(try_merge, candidates)
            best_index = sorted(range(len(scores)), key=lambda x: sum(scores[x]))[0]
            model_gain = l.model_cost - scores[best_index][0]
            data_gain = l.data_cost - scores[best_index][1]
            if model_gain+data_gain > 0:
                l, _ = perform_best_operation(('merge', candidates[best_index][:2]), data_gain, model_gain, l, options, folder)
                if use_pickle:
                    serialized_obj = dump_to_bytes(l)
                l.data_cost = data_cost(l.ta, options.data_parser, l.noise_model)
                l.model_cost = model_cost(l.ta)
                print(f'Current cost: {l.model_cost + l.data_cost}')
                has_merged = True
            else:
                has_merged = False
                still_candidates = False

        # SPLITS
        if verbose: print('trying splits...')
        still_candidates = True
        while still_candidates:
            has_split = False
            candidate_edges = [s.id for s in l.ta.states if s.edges_out and not isinstance(s, EndingState)]

            for e in candidate_edges:
                if use_pickle:
                    candidate = (e, load_from_bytes(serialized_obj))
                else:
                    candidate = (e, copy.deepcopy(l))
                score = try_split(candidate)

                model_gain = l.model_cost - score[0]
                data_gain = l.data_cost - score[1]
                # if verbose: print(f"Gain: {(data_gain+model_gain):.3f} (data gain: {data_gain:.3f}, model gain: {model_gain:.3f})")
                if model_gain+data_gain > 0:
                    l, _ = perform_best_operation(('split', candidate[0]), data_gain, model_gain, l, options, folder)
                    if use_pickle:
                        serialized_obj = dump_to_bytes(l)
                    l.data_cost = data_cost(l.ta, options.data_parser, l.noise_model)
                    l.model_cost = model_cost(l.ta)
                    print(f'Current cost: {l.model_cost+l.data_cost}')
                    has_split = True
                    break
            if not has_split: still_candidates = False

        # SUBPART DELETION
        if verbose: print('trying del...')
        still_candidates = True
        while still_candidates:
            has_del = False
            candidate_edges = [e.id for e in l.ta.edges if not (e.source.initial and len(e.source.edges_out) == 1)
                                                           and l.is_del_interesting(e)]  # if unique transition of the initial state
            to_del = list()
            for candidate in candidate_edges:
                if candidate in to_del: continue
                edge = [e for e in l.ta.edges if e.id == candidate][0]
                while len(edge.destination.edges_out) == 1 and len(
                        edge.destination.edges_in) == 1:
                    edge = edge.destination.edges_out[0]
                    to_del.append(edge.id)
            candidate_edges = [c for c in candidate_edges if c not in to_del]

            for e in candidate_edges:
                if use_pickle:
                    candidate = (e, load_from_bytes(serialized_obj))
                else:
                    candidate = (e, copy.deepcopy(l))
                score = try_del(candidate)
                model_gain = l.model_cost - score[0]
                data_gain = l.data_cost - score[1]
                #if verbose: print(f"Gain: {(data_gain + model_gain):.3f} (data gain: {data_gain:.3f}, model gain: {model_gain:.3f})")
                if model_gain+data_gain > 0:
                    l, _ = perform_best_operation(('delete', candidate[0]), data_gain, model_gain, l, options, folder)
                    if use_pickle:
                        serialized_obj = dump_to_bytes(l)
                    l.data_cost = data_cost(l.ta, options.data_parser, l.noise_model)
                    l.model_cost = model_cost(l.ta)
                    print(f'Current cost: {l.model_cost + l.data_cost}')
                    has_del = True
                    break
            if not has_del: still_candidates = False

        improvement = has_del or has_split or has_merged

        if options.export:
            l.ta.export_ta(os.path.join(folder, str(i) + '.dot'), guard_as_distrib=options.guards == GuardsFormat.DISTRIB)

    if verbose: print("Model cost: " + str(l.model_cost))
    if verbose: print("Data cost: " + str(l.data_cost))
    if verbose: print("Total cost: " + str(l.data_cost+l.model_cost))

    if options.export:
        with open(os.path.join(folder, "log.txt"), "a") as f:
            f.write(f"Final data cost={l.data_cost}, model cost={l.model_cost}\n")

    return l


