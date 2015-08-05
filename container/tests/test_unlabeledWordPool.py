from unittest import TestCase
from asrActiveLearning.container.pool import UnmarkedWordPool
from asrActiveLearning.container.utterance import Utterance
from asrActiveLearning.reader.ctm import CtmRecord
from asrActiveLearning.container.utterance import HypothesisRecordStorage

__author__ = 'martin'

class UtteranceStub(object):
    def __init__(self):
        pass

class TestUnlabeledWordPool(TestCase):

    def setUp(self):
        self.utterance = Utterance("utt_id_1", "record_1", None)
        self.ctm_record = CtmRecord(["duration", "start_time"], "id1")
        self.ctm_record.add_rows([[1, 0], [1, 2], [1, 3]])
        self.hypo_storage = HypothesisRecordStorage.storage
        self.hypo_storage["record_1"] = self.ctm_record
        self.pool = UnmarkedWordPool()

    def test_add_utterances(self):
        self.pool.add_utterances([self.utterance])
        self.assertEqual(self.pool[0], self.utterance)

    def test_iter(self):
        self.pool.add_utterances([self.utterance])
        expected_seq = [(i, line_record) for (i, line_record) in enumerate(self.ctm_record)]
        pool_sequence = [x for x in self.pool]
        self.assertSequenceEqual(pool_sequence, expected_seq)






