from unittest import TestCase

from asrActiveLearning.reader.csv_reader import CSVReader

__author__ = 'martin'

class TestCSVReader(TestCase):
    def setUp(self):
        self.line_parser = CSVReader()

    def test_parse(self):
        filename = "hypo.ctm"
        parsed_lines = list(self.line_parser.read(filename))
        reference_first_line = ["ted_id269", "1", "754.79", "0.18", "we", "-358.73"]
        reference_second_line = ["ted_id269", "1", "754.98", "0.26", "put", "-470.81"]
        self.assertSequenceEqual(reference_first_line, parsed_lines[0])
        self.assertSequenceEqual(reference_second_line, parsed_lines[1])


