import os

from tadam.utils import parse_packet_data_size, parse_packet_data_delay, parse_string
from enum import Enum
from tadam.mdl import NoiseModel

class GuardsFormat(Enum):
    FULL = 1
    REDUCED = 2
    DISTRIB = 3

class Init(Enum):
    TAG = 1
    UNIVERSAL = 2
    STATE_SYMBOL = 3
    APTA = 4

class Search(Enum):
    EXHAUSTIVE = 1
    OPPORTUNISTIC = 2

class Options:
    def __init__(self, filename, k=2, guards=GuardsFormat.REDUCED,
                 export=True, pruning=False,
                 path=None, data_parser=parse_string, top_k=1, init=Init.APTA, search=Search.EXHAUSTIVE,
                 noise_model = None, del_freq_max=1):
        """
        :param filename: name of file containing the data
        :param k: sequence length in k-future, for TAG only
        :param guards: GuardsFormat.REDUCED for strict interval, GuardsFormat.DISTRIB for normal distribution (only relevant for TA display)
        :param export: True to export the TA at each iteration of the greedy search
        :param pruning: True to prune infrequent edges after learning, for TAG only
        :param path: path of the folder containing the data file
        :param data_parser: fonction to parse tss files (default: data_parser for format 'event:delay')
        :param top_k:
        """
        self.filename = filename
        self.k = k
        self.guards = guards
        self.export = export
        self.pruning = pruning
        if path is None:
            self.path = os.path.join('data', 'words')
        else:
            self.path = path
        self.noise_model = noise_model or NoiseModel()
        self.top_k = top_k
        self.data_parser = data_parser
        self.init = init
        self.search = search
        self.del_freq_max = del_freq_max
