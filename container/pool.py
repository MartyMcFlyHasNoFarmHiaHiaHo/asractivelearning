__author__ = 'martin'
import itertools

class UnlabeledUtterancePool(list):

    def add_utterances(self, utterances):
        self.extend(utterances)

class UnmarkedWordPool(object):

    def __init__(self, overlap_limit=0.9):
        super(UnmarkedWordPool, self).__init__()
        self.overlap_limit = overlap_limit
        self.pool = []

    def add_utterances(self, utterances):
        self.pool.extend(utterances)

    def __iter__(self):
        return self.line_iterator()

    def __len__(self):
        return sum(len(utterance) for utterance in self.pool)

    def __getitem__(self, item):
        return self.pool[item]

    def __setitem__(self, key, value):
        self.pool[key] = value

    def line_iterator(self):
        for utterance in self.pool:
            for index, line_record in enumerate(utterance):
                yield index, line_record




