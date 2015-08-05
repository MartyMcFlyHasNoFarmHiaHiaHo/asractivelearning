__author__ = 'martin'
from asrActiveLearning.container.utterance import Utterance

class CtmUtteranceFactory(object):

    @staticmethod
    def create_utterance(hypo_record, config):
        return Utterance(hypo_record, config)
