__author__ = 'martin'

class PronunciationDictionary(dict):
    def __init__(self, word_to_phoneme_map, tags):
        super(PronunciationDictionary, self).__init__()
        self.update(word_to_phoneme_map)
        self.tags = tags








