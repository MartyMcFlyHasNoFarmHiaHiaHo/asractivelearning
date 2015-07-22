__author__ = 'martin'

class CtmFileReader(object):
    def __init__(self, csv_reader, new_utterance_marker="#"):
        self.csv_reader = csv_reader
        self.new_utterance_marker = new_utterance_marker

    def gather_utterance_lines_generator(self, filename):
        utterance_lines = []
        utterance_header = None
        first_marker_found = False
        for line_number, line in enumerate(self.csv_reader.read(filename)):
            if line[0].startswith(self.new_utterance_marker):
                if utterance_header is not None:
                    yield utterance_header, utterance_lines
                    utterance_lines = []
                else:
                    utterance_header = line
            else:
                utterance_lines.append(line)

        yield utterance_header, utterance_lines

    def gather_utterances(self, filename):
        lines_buffer = list(self.csv_reader.read(filename))
         





    def read(self, filename):
        for utterance_header, utterance_lines in self.gather_utterance_lines_generator(filename):
            yield utterance_header, utterance_lines




