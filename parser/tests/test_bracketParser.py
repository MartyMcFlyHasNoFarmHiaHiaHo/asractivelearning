from unittest import TestCase
from asrActiveLearning.parser.brackets import BracketParser
import pyparsing

__author__ = 'martin'


class TestBracketParser(TestCase):
    def setUp(self):
        self.valid_string_1 = "{one {two} {three} four {five} {{six} {seven}}}"
        self.valid_string_1_no_whitespaces = self.valid_string_1.replace(" ", "")
        self.missing_bracket_string_1 = self.valid_string_1[2:]
        self.missing_bracket_string_2 = self.valid_string_1.replace("three}", "three")

    def valid_parses(self):
        expected_valid_string_1 = ['one', ['two'], ['three'], 'four', ['five'], [['six'], ['seven']]]
        parsed_valid_string_1 = BracketParser.parse(self.valid_string_1, "{", "}")
        self.assertSequenceEqual(expected_valid_string_1, parsed_valid_string_1)

        parsed_valid_string_1_no_whitespaces = BracketParser.parse(self.valid_string_1_no_whitespaces, "{", "}")
        self.assertSequenceEqual(expected_valid_string_1, parsed_valid_string_1_no_whitespaces)

    def invalid_parses(self):
        self.assertRaises(pyparsing.ParseException, BracketParser.parse, self.missing_bracket_string_2, "{", "}")
        self.assertRaises(ValueError, BracketParser.parse, self.missing_bracket_string_1, "{", "}")

    def test_parse(self):
        self.valid_parses()
        self.invalid_parses()


