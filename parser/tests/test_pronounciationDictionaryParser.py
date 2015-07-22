from unittest import TestCase
from asrActiveLearning.parser.pron_dictionary import PronounciationDictionaryParser

__author__ = 'martin'


class TestPronounciationDictionaryParser(TestCase):
    def setUp(self):
        self.parser = PronounciationDictionaryParser()
        self.test_dictionary = "dictionary.small"
        self.valid_dict_line = "'Fahrenheit {{F WB} EH R AX N HH AY {T WB}}"
        self.expected_valid_sequence = [("F", "WB"), ("EH",), ("R",), ("AX",), ("N",), ("HH",), ("AY",), ("T", "WB")]

    def test_split_word_and_phone_list(self):
        invalid_no_word_dict_line = "{{F WB} EH R AX N HH AY {T WB}}"
        invalid_two_words_dict_line = "Bla blubb {0}".format(invalid_no_word_dict_line)
        self.assertRaises(ValueError, self.parser.split_word_and_phone_list, invalid_no_word_dict_line)
        self.assertRaises(ValueError, self.parser.split_word_and_phone_list, invalid_two_words_dict_line)
        expected_valid_splitted_list = ("'Fahrenheit", "{{F WB} EH R AX N HH AY {T WB}}")
        splitted_list = self.parser.split_word_and_phone_list(self.valid_dict_line)
        self.assertSequenceEqual(splitted_list, expected_valid_splitted_list)

    def test_convert_and_flatten_parsed_list(self):
        bracket_line = "{{F WB} EH R AX N HH AY {T WB}}"
        parsed_bracket_list = [['F', 'WB'], 'EH', 'R', 'AX', 'N', 'HH', 'AY', ['T', 'WB']]
        converted_and_flatten_parsed_list = self.parser.convert_and_flatten_parsed_list(parsed_bracket_list)
        self.assertSequenceEqual(self.expected_valid_sequence, converted_and_flatten_parsed_list)

    def test_parse_line(self):
        word, flatten_phone_list = self.parser.parse_line(self.valid_dict_line)
        self.assertEqual("'Fahrenheit", word)
        self.assertSequenceEqual(self.expected_valid_sequence, flatten_phone_list)


