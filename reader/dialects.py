__author__ = 'martin'
import csv

class JanusCtmDialect(csv.Dialect):
    """Describe the usual properties of Excel-generated CSV files."""
    delimiter = ' '
    quotechar = '^'
    doublequote = True
    skipinitialspace = True
    lineterminator = '\r\n'
    quoting = csv.QUOTE_MINIMAL

class JanusHypoDialect(JanusCtmDialect):
    pass
