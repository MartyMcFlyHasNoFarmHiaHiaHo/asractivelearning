__author__ = 'martin'
from asrActiveLearning.reader.csv_reader import CSVReader
from asrActiveLearning.parser.brackets import BracketParser
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class PronounciationDictionaryParser(object):
    def __init__(self, opening_bracket="{", closing_bracket="}"):
        self.opening_bracket = opening_bracket
        self.closing_bracket = closing_bracket

    @staticmethod
    def check_for_valid_word(substring):
        if len(substring.split()) > 1:
            raise ValueError("More than one word on the left-hand side is invalid")

    def split_word_and_phone_list(self, line):
        split_index = line.find(self.opening_bracket)
        if split_index < 0:
            raise ValueError("Missing opening bracket '{0}' in {1}".format(self.opening_bracket, line))
        if split_index == 0:
            raise ValueError("Opening bracket found but no word on the left-hand side")
        word = line[0:split_index].strip()
        bracket_list = line[split_index:].strip()
        self.check_for_valid_word(word)
        return word, bracket_list

    @staticmethod
    def convert_and_flatten_parsed_list(parsed_phone_list):
        flatten_tuple_list = []
        for element in parsed_phone_list:
            if not isinstance(element, list):
                new_element = tuple([element])
            else:
                new_element = tuple(element)
            flatten_tuple_list.append(new_element)
        return flatten_tuple_list

    def parse_line(self, line):
        word, phone_list = self.split_word_and_phone_list(line)
        parsed_phone_list = BracketParser.parse(phone_list, self.opening_bracket, self.closing_bracket)
        flatten_phone_list = self.convert_and_flatten_parsed_list(parsed_phone_list)
        return word, flatten_phone_list

    def parse(self, filename, line_reader=CSVReader):
        csv_reader = line_reader
        word_to_phone_map = {}
        for line_number, line in enumerate(csv_reader.read(filename)):
            try:
                word, parsed_phone_list = self.parse_line(line)
                word_to_phone_map[word] = parsed_phone_list
            except:
                log.error("Error while parsing in file {0}, line {0}".format(filename, line_number))
                raise

        return word_to_phone_map








