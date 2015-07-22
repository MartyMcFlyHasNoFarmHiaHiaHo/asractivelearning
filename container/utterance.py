__author__ = 'martin'

class Utterance(object):
    def __init__(self, hypo_record):
        self.hypo_record = hypo_record

    def __iter__(self):
        pass



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







