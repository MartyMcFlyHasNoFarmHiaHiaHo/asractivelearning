__author__ = 'martin'

import collections
import operator

class CtmRecord(object):
    def __init__(self, col_names, header):
        super(CtmRecord, self).__init__()
        self.col_names = col_names
        self.ctm_line_namedtuple_def = collections.namedtuple("UtteranceWord", col_names)
        self.ctm_lines = []
        self.header = header

    def add_rows(self, rows):
        for row in rows:
            row_record = self.ctm_line_namedtuple_def(*row)
            self.ctm_lines.append(row_record)

    def __getitem__(self, item):
        return self.ctm_lines[item]

    def __setitem__(self, key, value):
        self.ctm_lines[key] = value

    def __iter__(self):
        return iter(self.ctm_lines)

    def __len__(self):
        return len(self.ctm_lines)

class CtmFileReader(object):
    def __init__(self, csv_reader, col_types, col_names, new_utterance_marker="#"):
        self.csv_reader = csv_reader
        self.new_utterance_marker = new_utterance_marker
        self.col_types = col_types
        self.col_names = col_names

    def read(self, filename):
        for utterance_header, utterance_lines in self.read_utterances(filename):
            conv_utterance_lines = self.convert_types(utterance_lines)
            ctm_record = CtmRecord(self.col_names, utterance_header[1])
            ctm_record.add_rows(utterance_lines)
            yield ctm_record

    def convert_types(self, lines):
        conv_lines = []
        for line in lines:
            conv_line = map(lambda (val, col_type): col_type(val), zip(line, self.col_types))
            conv_lines.append(conv_line)
        return conv_lines

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





