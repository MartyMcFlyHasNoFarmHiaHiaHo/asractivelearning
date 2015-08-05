from asrActiveLearning.datastructures.interval import IntervalBookKeeper

__author__ = 'martin'
from collections import Counter
import intervaltree

class HypothesisRecordStorage(dict):
    storage = {}

class Utterance(object):
    def __init__(self, utt_id, hypo_record_id, config):
        self.utt_id = utt_id
        self.hypo_record_id = hypo_record_id
        self.interval_bookkeeper = IntervalBookKeeper()
        self.config = config

    def get_word_overlap(self, index):
        interval = self.get_word_interval(index)
        overlap = self.interval_bookkeeper.get_interval_overlap(interval)
        return overlap

    def get_word_interval(self, index):
        word = self[index]
        begin = word.start_time
        end = word.start_time + word.duration
        interval = intervaltree.Interval(begin, end)
        return interval

    def mark_word(self, index):
        interval = self.get_word_interval(index)
        self.interval_bookkeeper.add(interval)

    @property
    def hypo_record(self):
        return HypothesisRecordStorage.storage[self.hypo_record_id]

    def __getitem__(self, item):
        return self.hypo_record[item]

    def __iter__(self):
        return iter(self.hypo_record)

    def __len__(self):
        return len(self.hypo_record)

    @property
    def duration(self):
        first_utt_word = self.hypo_record[0]
        last_utt_word = self.hypo_record[-1]
        return (last_utt_word.start_time + last_utt_word.duration) - first_utt_word.start_time


class Word(object):
    pool = dict()

    def __new__(cls, word_string, **kwargs):
        try:
            obj = cls.pool[word_string]
        except KeyError:
            obj = object.__new__(cls)
            cls.pool[word_string] = obj
        return obj

    def __init__(self, word_string, dictionary):
        self.word_string = word_string
        self.phonemes = dictionary[word_string]
        self.tf_idf = Counter()







