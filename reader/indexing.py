__author__ = 'martin'
import fileinput

class LineIndexAccessor(object):
    def __init__(self, files, parse_func, index_cols):
        """

        :param files:   list of files to be indexed
        :param parse_func:  line-by-line iterable
        :param index_cols:  list of column numbers which form the total index key
        """
        self.files = files
        self.parse_func = parse_func
        self.index_cols = index_cols
        self.index_dict = {}

    @staticmethod
    def are_lists_equal(self, a, b):
        if len(set(a).intersection(b)) == max(len(a),len(b)):
            return True
        else:
            return False

    def make_indice_and_linenums_generator(self, file_path):
        last_indice = []
        for line_num, parsed_line in enumerate(self.parse_func(file_path)):
            indice_fields = [parsed_line[index] for index in self.index_cols]
            if LineIndexAccessor.are_lists_equal(indice_fields, last_indice):
                continue
            last_indice = indice_fields

            yield indice_fields, line_num

    def add_index_dict_entry(self, indice):
        composed_index = "-".join(indice)
        self.index_dict[composed_index] = []

    def run_indexing(self):
        pass







