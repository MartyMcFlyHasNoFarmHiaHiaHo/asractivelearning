from unittest import TestCase
from asrActiveLearning.container.utterance import Utterance
from asrActiveLearning.container.utterance import HypothesisRecordStorage
from asrActiveLearning.reader.ctm import CtmRecord
import intervaltree

__author__ = 'martin'


class TestUtterance(TestCase):
    def setUp(self):
        self.utterance = Utterance("utt_id_1", "record_1", None)
        self.setup_hypo_storage()
        self.setup_intervals()

    def setup_hypo_storage(self):
        ctm_record = CtmRecord(["duration", "start_time"], "id1")
        ctm_record.add_rows([[1, 0], [1, 2], [1, 3]])
        self.hypo_storage = HypothesisRecordStorage.storage
        self.hypo_storage["record_1"] = ctm_record

    def setup_intervals(self):
        self.interval1 = intervaltree.Interval(0, 5)
        self.interval2 = intervaltree.Interval(4, 10)

    def test_get_duration(self):
        duration = self.utterance.duration
        self.assertEqual(duration, 4)

    def test_mark_word(self):
        self.utterance.mark_word(1)
        interval = self.utterance.get_word_interval(1)
        interval_in_book = self.utterance.interval_bookkeeper.overlaps_range(interval.begin, interval.end)
        self.assertTrue(interval_in_book)
        # Sanity check
        interval2 = intervaltree.Interval(4, 10)
        interval2_in_book = self.utterance.interval_bookkeeper.overlaps_range(interval2.begin, interval2.end)
        self.assertFalse(interval2_in_book)

    def test_get_word_overlap(self):
        self.utterance.mark_word(0)
        self.utterance.mark_word(2)
        overlap = self.utterance.get_word_overlap(1)
        self.assertEqual(overlap, 0)

        self.utterance.mark_word(1)
        interval = self.utterance.get_word_interval(1)
        overlap = self.utterance.get_word_overlap(1)
        self.assertEqual(interval.length(), overlap)







