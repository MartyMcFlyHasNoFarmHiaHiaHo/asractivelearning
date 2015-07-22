__author__ = 'martin'

import collections
import operator

class CtmFileReader(object):
    def __init__(self, csv_reader, col_types, col_names, new_utterance_marker="#"):
        self.csv_reader = csv_reader
        self.new_utterance_marker = new_utterance_marker
        self.col_types = col_types
        self.col_names = col_names

    def read(self, filename):
        CtmRecord = collections.namedtuple("CtmRecord", self.col_names)
        for utterance_header, utterance_lines in self.read_utterances(filename):
            col_dict = self.extract_and_convert_columns_types(utterance_lines)
            ctm_record = CtmRecord(*map(lambda col_name: col_dict[col_name], self.col_names))
            yield ctm_record

    def extract_and_convert_columns_types(self, lines):
        num_cols = len(lines[0])
        col_dict = {}
        for col_idx in xrange(num_cols):
            col_name = self.col_names[col_idx]
            col = CtmFileReader.slice_column(lines, col_idx)
            col_dict[col_name] = map(self.col_types[col_idx], col)
        return col_dict

    @staticmethod
    def slice_column(iterable, col_num):
        ig = operator.itemgetter(col_num)
        return map(ig, iterable)

    def read_utterances(self, filename):
        utterance_lines = []
        utterance_header = None
        line_iterator = self.csv_reader.read(filename)
        while True:
            try:
                line = line_iterator.next()
            except Exception:
                yield utterance_header, utterance_lines
                raise StopIteration

            if line[0].startswith(self.new_utterance_marker):
                if utterance_header is not None:
                    yield utterance_header, utterance_lines
                    utterance_lines = []
                    utterance_header = line
                else:
                    utterance_header = line
            else:
                utterance_lines.append(line)





