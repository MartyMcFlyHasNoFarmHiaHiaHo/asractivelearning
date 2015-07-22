__author__ = 'martin'

class PronounciationDictionary(dict):
    def __init__(self, word_to_phoneme_map, tags):
        super(PronounciationDictionary, self).__init__()
        self.update(word_to_phoneme_map)
        self.tags = tags








