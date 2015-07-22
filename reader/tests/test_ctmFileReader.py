from unittest import TestCase
from asrActiveLearning.reader.ctm import CtmFileReader
from asrActiveLearning.reader.csv_reader import CSVReader

__author__ = 'martin'


class TestCtmFileReader(TestCase):
    def setUp(self):
        csv_reader = CSVReader()
        self.ctm_reader = CtmFileReader(csv_reader)
        self.test_ctm_file = "test.ctm"

    def get_utterance_lines_generator_results(self, filename):
        result_list = []
        for utterance_header, utterance_lines in self.ctm_reader.gather_utterance_lines_generator(filename):
            result_list.append((utterance_header, utterance_lines))
        return result_list

    def valid_test_cases(self):
        result_iterator = iter(self.ctm_reader.gather_utterance_lines_generator(self.test_ctm_file))
        expected_first_utterance_header = ["#", "ted_id978_375_43_376_86", "375.43", "-1060.577148"]
        expected_second_utterance_header = ["#", "ted_id978_373_3_374_68", "373.3", "-1130.733765"]
        expected_first_utterance_line_nums = 5
        expected_second_utterance_line_nums = 5
        first_utterance_header, first_utterance_lines = result_iterator.next()
        second_utterance_header, second_utterance_lines = result_iterator.next()
        print first_utterance_header
        print second_utterance_header
        self.assertSequenceEqual(first_utterance_header, expected_first_utterance_header)
        self.assertSequenceEqual(second_utterance_header, expected_second_utterance_header)

    def test_gather_utterance_lines_generator(self):
        self.valid_test_cases()



