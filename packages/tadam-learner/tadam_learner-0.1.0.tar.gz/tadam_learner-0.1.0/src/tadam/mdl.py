import tadam.automaton
import math
import numpy as np
import heapq
from tadam.ts import TS

class NoiseModel:
    def __init__(self, deletion_possible=True, addition_possible=True, transposition_possible=True, reemission_possible=True):
        self.deletion_possible = deletion_possible
        self.addition_possible = addition_possible
        self.transposition_possible = transposition_possible
        self.reemission_possible = reemission_possible

    def __deepcopy__(self, memo):
        new_model = NoiseModel(self.deletion_possible, self.addition_possible, self.transposition_possible, self.reemission_possible)
        return new_model

def integer_cost(n: int) -> float:
    """
        Computes the length of the optimal universal integer encoding
    Reference: Rissanen, 1983
    """
    l = math.log2(2.865064)
    n += 1 # Rissanen code is for n>0, so shift by 1 to be able to encode 0
    while n > 0:
        l += math.log2(n)
        n = math.log2(n)
    return l

def data_cost_new_word(automaton: tadam.automaton, w: list, noise_model, verbose=False) -> float:
    """
        Computes the cost of the data given an automaton.
        This function does _not_ modify the automaton
    """
    dist = {}
    if noise_model.deletion_possible:
        for n in automaton.states:
            dist[n.name] = compute_shortest_paths(n, automaton, {})
    l = levenshtein(dist, w, automaton, {}, noise_model, verbose)

    if l: # corrected
        cost = l[0]
    else: # not corrected
        cost = len(w) * math.log2(len(automaton.symbols)) # explicit encoding of the letters
        for (_,l) in w:
            cost += sum([integer_cost(v) for v in l])

    return cost

def model_cost(automaton: tadam.automaton, proba_precision=1e-2, std_precision=1e-1, verbose=False) -> float:
    """
        Computes the cost of the automaton
    """
    n = len(automaton.states) # number of states
    if n == 0: return 0
    s = len(automaton.symbols) # alphabet size
    cost = integer_cost(n)
    cost += math.log2(n) # accepting state encoding
    cost += math.log2(n) # initial state encoding
    # verbose = True
    # transformations probability encoding (5 transformations, so 4 probabilities to encode)
    cost -= 4 * math.log2(proba_precision)

    # encode all the probabilities. For each state, we only need to memorize k-1 values, hence the last term
    proba_nb = len(automaton.edges) + len([n for n in automaton.states if n.accepting]) - len(automaton.states)
    cost -= proba_nb * math.log2(proba_precision) # use a uniform encoding, not a universal encoding, to not penalize large probabilities

    if verbose: print("#states:",len(automaton.states),", #edges:",len(automaton.edges))

    for e in automaton.edges:
        cost += 2*math.log2(n) # start and end nodes encoding
        cost += math.log2(s) # transition letter
        (mu,cov) = e.time_distribution() # guard (up to some precision)
        cost += sum([integer_cost(int(m)) for m in mu]) # considered to be an integer
        val = list(cov[np.triu_indices_from(cov)])
        cost += sum([integer_cost(int(v/std_precision)) for v in val]) # considered to be a float with finite precision
    if verbose: print(f"Model cost: {cost:.3f}")
    return cost

def data_cost(automaton: tadam.automaton, data_parser, noise_model, verbose=False, max_iter=4) -> float:
    """
        Computes the cost of the data given an automaton.
        This function _modifies_ the automaton
    """

    # Cost of corrected and uncorrected words
    corrected_cost = 0
    uncorrected_cost = 0

    total_number = len(automaton.tss)
    number_of_matching = total_number - len(automaton.unmatched_tss)
    number_of_corrected = 0
    number_of_uncorrected = 0

    # remove previous reconstructed word from edge’s tss and values
    for e in automaton.edges:
        e.rec_guard = []
        for ts in list(e.tss):
            if automaton.corrected_tss.get(ts):
                del e.tss[ts]

    length_matching = 0
    for n in automaton.states:
        length_matching += sum([e.visit_number() for e in n.edges_out])

    new_visits = {}
    rec_tss = {}

    # prior for costs. Will be modified during the EM algorithm
    # assume 10% noise
    automaton.cost_transition = -math.log2(0.9)
    automaton.cost_deletion = -math.log2(0.025)
    automaton.cost_reemission = -math.log2(0.025)
    automaton.cost_transposition = -math.log2(0.025)
    automaton.cost_addition = -math.log2(0.025)

    dist = {}
    again = True
    prev_cost = None
    curr_iter = 0
    while again: # <-- EM HERE
        again = False
        curr_iter += 1
        if curr_iter > max_iter:
            break

        # reset some variables
        rec_tss = {}
        for e in automaton.edges:
            rec_tss[hash(e)] = {}

        next_visits = {}
        number_of_corrected = 0
        number_of_uncorrected = 0

        corrected_cost = 0
        uncorrected_cost = 0

        # small priors
        number_tr = 1 + length_matching
        number_del = 1
        number_repeat = 1
        number_inv = 1
        number_add = 1

        if noise_model.deletion_possible:
            for n in automaton.states:
                dist[n.name] = compute_shortest_paths(n, automaton, new_visits)

        for _,w_index in enumerate(automaton.unmatched_tss):
            w = [data_parser(pair) for pair in automaton.tss[w_index]] # /!\ untimed word
            l = levenshtein(dist, w, automaton, new_visits, noise_model, verbose)

            if l: # corrected
                for s in l[2]:
                    if s.startswith("tr "):
                        number_tr += 1
                    elif s.startswith("del "):
                        number_del += 1
                    elif s.startswith("again"):
                        number_repeat += 1
                    elif s.startswith("inv "):
                        number_inv += 1
                    elif s.startswith("add "):
                        number_add += 1

                corrected_cost += l[0]
                number_of_corrected += 1
                gtime = None
                for (letter_index, (symbol, value)) in enumerate(l[3]): # on parcourt le mot reconstruit
                    if gtime is None:
                        gtime = value
                    else:
                        gtime = [a + b for a, b in zip(gtime, value)]
                    hedge = hash(l[1][letter_index])
                    ts = rec_tss[hedge].get(w_index, [])
                    ts.append((letter_index, gtime))
                    rec_tss[hedge][w_index] = ts
                    visits = next_visits.get(hedge, [])
                    visits.append(value)
                    next_visits[hedge] = visits
                ts = TS(w_index, l[3])
                ts.edge_sequence = l[1]
                automaton.corrected_tss[w_index] = ts
            else: # not corrected
                cost = len(w) * math.log2(len(automaton.symbols)) # explicit encoding of the letters
                for (_,l) in w:
                    cost += sum([integer_cost(v) for v in l])   # explicit encoding of the values
                uncorrected_cost += cost
                number_of_uncorrected += 1
                if w_index in automaton.corrected_tss:
                    automaton.corrected_tss.pop(w_index)
                # length_uncorrected += len(w)

        # compute the cost of matching words. Since this costs depends on the edge probabilities that depends on the reconstruction, we need to compute it at every EM step
        matching_cost = 0

        # Cost of matched words only (not the matched parts of corrected words)
        # Remark: automata determinism is helpful so the encoding of a word is unique so there is no need to find the most probable path
        matching_cost += automaton.cost_transition * sum([e.visit_number() for n in automaton.states for e in n.edges_out])

        for n in automaton.states:
            # transition probabilities encoding
            # don’t use get_edge_visit_number because we do not want to add the cost of reconstructed transitions twice
            matching_cost -= sum([e.visit_number() * math.log2(get_edge_proba(e, new_visits)) for e in n.edges_out])
            # guards probabilities encoding
            for e in n.edges_out:
                if get_edge_visit_number(e, new_visits) > 0:
                    for v in e.guard:
                        prob = max(e.value_probability(v, new_visits.get(hash(e),[])), 1e-3) # fix for p = 0 # big effect of the value # TODO: discuss about it
                        matching_cost -= math.log2(prob)

        new_cost = corrected_cost + uncorrected_cost + matching_cost
        if prev_cost is None or new_cost < prev_cost:
            prev_cost = new_cost
            new_visits = next_visits
            again = True
            number_tr = max(number_tr, 3*(number_del + number_repeat + number_inv + number_add)) # assume at most 25% noise
            number_all = number_tr + number_del + number_repeat + number_inv + number_add
            automaton.cost_transition = -math.log2(number_tr / number_all)
            automaton.cost_deletion = -math.log2(number_del / number_all)
            automaton.cost_reemission = -math.log2(number_repeat / number_all)
            automaton.cost_transposition = -math.log2(number_inv / number_all)
            automaton.cost_addition = -math.log2(number_add / number_all)
            if verbose: print(f"Transition cost: {automaton.cost_transition:.3f}, deletion cost: {automaton.cost_deletion:.3f}, reemission cost: {automaton.cost_reemission:.3f}, transposition cost: {automaton.cost_transposition:.3f}, addition cost: {automaton.cost_addition:.3f}")

    # end of EM

    # encode the status of each word, either uncorrected or corrected
    # this is done outside of EM because it is not affected by how the reconstruction is done
    match_or_correct_proba = (number_of_corrected + number_of_matching) / total_number
    uncorrect_proba = 1 - match_or_correct_proba
    if number_of_matching + number_of_corrected > 0:
        matching_cost += -math.log2(match_or_correct_proba) * number_of_matching
        corrected_cost += -math.log2(match_or_correct_proba) * number_of_corrected
    if number_of_uncorrected > 0:
        uncorrected_cost += -math.log2(uncorrect_proba) * number_of_uncorrected


    if verbose: print(f"Total: {total_number}, matching: {number_of_matching}, corrected: {number_of_corrected}, uncorrected: {number_of_uncorrected}")

    # include rec_tss to edge tss
    for e in automaton.edges:
        for v in automaton.corrected_tss.values():
            for i,(_,val) in enumerate(v.sequence):
                if v.edge_sequence[i] == e:
                    e.rec_guard.append(val)
        if rec_tss.get(hash(e)):
            for k,v in rec_tss[hash(e)].items():
                e.tss[k] = v

    # update state tss
    for s in automaton.states: # first we remove all reconstructed sequences
        s.tss = {k: v for k, v in s.tss.items() if k not in automaton.unmatched_tss}
    for ts_index, ts_obj in automaton.corrected_tss.items():
        ts_obj.edge_sequence[0].source.tss.setdefault(ts_index, []).append((-1, [0] * automaton.number_of_values)) # initial state
        for index, edge in enumerate(ts_obj.edge_sequence):
            v = (index, ts_obj.get_global_clock_value(index))
            edge.destination.tss.setdefault(ts_index, []).append(v)

    states_to_del = [s for s in automaton.states if len(s.tss) == 0]
    edges_to_del = [e for e in automaton.edges if len(e.tss) == 0]
    for e in set(edges_to_del):
        e.source.del_edge(e, "out")
        e.destination.del_edge(e, "in")
        automaton.edges.remove(e)
    for s in set(states_to_del):
        automaton.states.remove(s)

    assert len([s for s in automaton.states if len(s.tss) == 0]) == 0 and len([e for e in automaton.edges if len(e.tss) == 0]) == 0

    automaton.update_probas()

    return matching_cost + corrected_cost + uncorrected_cost

def compute_shortest_paths(startingstate: tadam.state, automaton: tadam.automaton, new_visits) -> dict:
    # dijkstra algorithm
    visited = {}
    openlist = [] # (cost, dummy for sorting, next node, path, edges, word)
    dummy = 0
    heapq.heappush(openlist,(0,dummy,startingstate,[],[],[])) # heapq use the first element of the tuple to order
    while openlist:
        (c,_,n,p,l,w) = heapq.heappop(openlist)
        if visited.get(n.name):
            continue
        visited[n.name] = (c,p,l,w)
        assert c >= 0
        for e in n.edges_out:
            dummy += 1
            # since it’s an addition, we can chose the value. We take the most probable one
            # we need to save the edge that has been selected (to know how to move in the automata), but no need to save the value since it’ll be deleted anyway
            if get_edge_visit_number(e, new_visits) > 0:
                new_val = [round(v) for v in e.time_distribution(new_visits.get(hash(e),[]))[0]]
                heapq.heappush(openlist, (c + automaton.cost_deletion - math.log2(get_edge_proba(e, new_visits)),
                                          dummy,
                                          e.destination,
                                          p + ["del "+e.symbol],
                                          l + [e],
                                          w + [(e.symbol, new_val)]))

    return visited

def get_edge_visit_number(e, new_visits):
    return e.visit_number() + len(new_visits.get(hash(e),[]))

def get_edge_proba(e, new_visits):
    nb_visits = sum([get_edge_visit_number(e2, new_visits) + 0.5 for e2 in e.source.edges_out])
    return (get_edge_visit_number(e, new_visits) + 0.5) / nb_visits

def levenshtein(dist, word, automaton, new_visits, noise_model, verbose=False):
    # word is a List[(str, int)]
    # Optimal string alignment distance has been used here: "Touching from a Distance: Website Fingerprinting Attacks and Defenses", Cai et al., 2012

    matrix = {}
    wlen = len(word)
    inf = 999999 # infinity

    initial_state = [s for s in automaton.states if s.initial][0]
    for n in automaton.states:
        if n == initial_state:
            matrix["0"+n.name] = (0, [], [], []) # (cost: int, path: str list, edges: Edge list, word: (str,float) list)
        elif noise_model.deletion_possible and dist[initial_state.name].get(n.name):
            matrix["0"+n.name] = dist[initial_state.name][n.name]
        else:
            matrix["0"+n.name] = (inf, [], [], [])

    for l in range(wlen):
        curr_letter = word[l][0]
        prev_letter = None
        if l >= 1:
            prev_letter = word[l-1][0]

        tmp_matrix = {}
        for s in automaton.states:
            tmp = [(inf, [], [], [])] # just in case no transformation is possible
            prev_cost = matrix[str(l)+s.name] # for deletion and reemission that use the same previous state

            # skip
            if noise_model.addition_possible:
                # encode explicitely value and letter, just like for unrecognized words
                value_cost = sum([integer_cost(v) for v in word[l][1]])
                tmp.append((prev_cost[0] + automaton.cost_addition + value_cost + math.log2(len(automaton.symbols)),
                            prev_cost[1] + ["add "+curr_letter],
                            prev_cost[2],
                            prev_cost[3]))

            # remove repeated letter
            if noise_model.reemission_possible and curr_letter == prev_letter and prev_cost[1] and prev_cost[1][-1].startswith("tr "): # previous edge was a transition
                guard_proba = prev_cost[2][-1].value_probability(word[l][1], new_visits.get(hash(prev_cost[2][-1]),[])) # reuse the last registered edge
                if guard_proba > 0: # if the probability of the guard is non-zero (should not be…)
                    # we don’t need to encode the letter or the edge (it’s the same as the previous one), only the value
                    tmp.append((prev_cost[0] + automaton.cost_reemission - math.log2(guard_proba),
                                prev_cost[1] + ["again"],
                                prev_cost[2],
                                prev_cost[3]))

            # transition
            for e in s.edges_in:
                if e.symbol == curr_letter and get_edge_visit_number(e, new_visits) > 0:
                    assert e.source.name in [n.name for n in automaton.states]
                    prev_cost = matrix[str(l) + e.source.name]
                    tr_proba = get_edge_proba(e, new_visits)
                    guard_proba = e.value_probability(word[l][1], new_visits.get(hash(e),[]))
                    if guard_proba > 0: # if the probability of the guard is non-zero
                        tmp.append((prev_cost[0] + automaton.cost_transition - math.log2(guard_proba) - math.log2(tr_proba),
                                    prev_cost[1] + ["tr "+e.symbol],
                                    prev_cost[2] + [e],
                                    prev_cost[3] + [(e.symbol, word[l][1])]))  # all is good

            # transposition
            if noise_model.transposition_possible and prev_letter and prev_letter != curr_letter:
                for e in s.edges_in:
                    if get_edge_visit_number(e, new_visits) > 0:
                        # use previous letter with current edge
                        guard_proba = e.value_probability(word[l-1][1], new_visits.get(hash(e),[]))
                        tr_proba = get_edge_proba(e, new_visits)
                        if guard_proba > 0 and e.symbol == prev_letter:
                            for e2 in e.source.edges_in:
                                if get_edge_visit_number(e2, new_visits) > 0:
                                    # use current letter with previous edge
                                    guard_proba2 = e2.value_probability(word[l][1], new_visits.get(hash(e2),[]))
                                    tr_proba2 = get_edge_proba(e2, new_visits)
                                    if guard_proba2 > 0 and e2.symbol == curr_letter:
                                        prev_cost = matrix[str(l-1) + e2.source.name]
                                        tmp.append((prev_cost[0] + automaton.cost_transposition - math.log2(guard_proba) - math.log2(guard_proba2) - math.log2(tr_proba) - math.log2(tr_proba2),
                                                    prev_cost[1] + ["inv " + curr_letter + " " + prev_letter],
                                                    prev_cost[2] + [e2,e],
                                                    prev_cost[3] + [(e2.symbol, word[l][1]), (e.symbol,word[l-1][1])]))

            best = None
            best_word = None
            best_path = None
            best_edges = None
            for (c,p,e,w) in tmp:
                if best is None or c < best:
                    best_word = w
                    best = c
                    best_path = p
                    best_edges = e

            tmp_matrix[str(l+1)+s.name] = (best, best_path, best_edges, best_word)

        # insertion of deleted symbols
        for s in automaton.states:
            if noise_model.deletion_possible:
                best_cost = None
                best_path = None
                best_edges = None
                best_word = None
                for source in automaton.states:
                    (initial_cost, initial_path, initial_edges, initial_word) = tmp_matrix[str(l+1)+source.name]
                    if initial_cost >= inf: # initial state is not reachable
                        continue
                    if dist[source.name].get(s.name): # if we can reach "s" from "source"
                        (cost_dist, path, edges, curr_word) = dist[source.name][s.name]
                        assert cost_dist < inf # we know s is reachable from source
                        cost = initial_cost + cost_dist
                        if best_cost is None or best_cost > cost:
                            best_cost = cost
                            best_path = initial_path + path
                            best_edges = initial_edges + edges
                            best_word = initial_word + curr_word

                if best_cost:
                    matrix[str(l+1)+s.name] = (best_cost, best_path, best_edges, best_word)
                else:
                    matrix[str(l+1)+s.name] = (inf, [], [], [])
            else:
                matrix[str(l+1)+s.name] = tmp_matrix[str(l+1)+s.name]

    for s in automaton.states:
        if s.accepting: # only one accepting state
            best, best_path, best_edges, best_word = matrix[str(wlen)+s.name]
            break

    if best >= inf:
        return None
    return best, best_edges, best_path, best_word
