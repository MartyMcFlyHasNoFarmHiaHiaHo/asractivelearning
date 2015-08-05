from unittest import TestCase
from asrActiveLearning.reader.ctm import CtmFileReader
from asrActiveLearning.reader.csv_reader import CSVReader

__author__ = 'martin'


class TestCtmFileReader(TestCase):
    def setUp(self):
        csv_reader = CSVReader()
        self.col_types = [str, int, float, float, str, float]
        self.col_names = ["utt_id", "channel", "start_time", "duration", "text", "score"]
        self.ctm_reader = CtmFileReader(csv_reader, self.col_types, self.col_names)
        self.test_ctm_file = "test.ctm"
        self.setup_expected_col_dict()

    def setup_expected_col_dict(self):
        expected_first_utterance_text = "the(1) tide of(1) rebar alike".split()
        self.expected_col_dict = {}
        self.expected_col_dict['utt_id'] = ["ted_id978"] * 5
        self.expected_col_dict['channel'] = [1] * 5
        self.expected_col_dict['start_time'] = [375.45, 375.55, 376.05, 376.14, 376.48]
        self.expected_col_dict['duration'] = [0.10, 0.50, 0.09, 0.34, 0.33]
        self.expected_col_dict['text'] = expected_first_utterance_text
        self.expected_col_dict['score'] = [2.51, -518.15, -126.38, -392.39, -194.80]

    def get_utterance_lines_generator_results(self, filename):
        result_list = []
        for utterance_header, utterance_lines in self.ctm_reader.read(filename):
            result_list.append((utterance_header, utterance_lines))
        return result_list

    def get_nth_item_slice(self, iterable, slize):
        import operator
        ig = operator.itemgetter(slize)
        return map(ig, iterable)

    def check_ctm_text(self, utterance_lines, expected_text):
        utterance_text = self.get_nth_item_slice(utterance_lines, 4)
        self.assertSequenceEqual(utterance_text, expected_text)

    def utterance_header_check(self, first_utterance_header, second_utterance_header):
        expected_first_utterance_header = ["#", "ted_id978_375_43_376_86", "375.43", "-1060.577148"]
        expected_second_utterance_header = ["#", "ted_id978_373_3_374_68", "373.3", "-1130.733765"]
        self.assertSequenceEqual(first_utterance_header, expected_first_utterance_header)
        self.assertSequenceEqual(second_utterance_header, expected_second_utterance_header)

    def utterance_text_check(self, first_utterance_lines, second_utterance_lines):
        expected_first_utterance_text = "the(1) tide of(1) rebar alike".split()
        expected_second_utterance_text = "conveyed Rita ductal type $(<BREATH>)".split()
        self.check_ctm_text(first_utterance_lines, expected_first_utterance_text)
        self.check_ctm_text(second_utterance_lines, expected_second_utterance_text)

    def valid_read_utterances_test_cases(self):
        result_iterator = iter(self.ctm_reader.read_utterances(self.test_ctm_file))
        first_utterance_header, first_utterance_lines = result_iterator.next()
        second_utterance_header, second_utterance_lines = result_iterator.next()
        self.utterance_header_check(first_utterance_header, second_utterance_header)
        self.utterance_text_check(first_utterance_lines, second_utterance_lines)

    def test_read(self):
        ctm_record_iterator = iter(self.ctm_reader.read(self.test_ctm_file))
        first_ctm_record = ctm_record_iterator.next()
        # TODO
        for line_record in first_ctm_record:
            print line_record
        # for key in self.expected_col_dict.iterkeys():
        #    self.assertSequenceEqual(self.expected_col_dict[key], getattr(first_ctm_record, key))

    def test_extract_and_convert_columns(self):
        result_iterator = iter(self.ctm_reader.read_utterances(self.test_ctm_file))
        first_utterance_header, first_utterance_lines = result_iterator.next()
        col_dict = self.ctm_reader.extract_and_convert_columns_types(first_utterance_lines)
        self.assertEqual(col_dict, self.expected_col_dict)

    def test_read_utterances(self):
        self.valid_read_utterances_test_cases()



