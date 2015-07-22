__author__ = 'martin'
import csv
from dialects import JanusCtmDialect

class CSVReader(object):
    def __init__(self, dialect=JanusCtmDialect):
        """

        :param dialect: subclass of csv.Dialect
        """
        self.dialect = dialect

    def read(self, filename):
        """

        :param filename: .ctm file
        """
        with open(filename, 'r') as fp:
            reader = csv.reader(fp, dialect=self.dialect)
            for line in reader:
                yield line


