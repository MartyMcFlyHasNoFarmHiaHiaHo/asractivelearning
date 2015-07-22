__author__ = 'martin'
import math
import pyparsing

class BracketParser(object):

    @staticmethod
    def check_for_trailing_brackets(string, opening_bracket, closing_bracket):
        if string[0] != opening_bracket:
            raise ValueError("String does not begin with '{0}'".format(opening_bracket))

        if string[-1] != closing_bracket:
            raise ValueError("String does not end with '{0}'".format(closing_bracket))

    @staticmethod
    def parse(string, opening_bracket, closing_bracket):
        """Generate parenthesized contents in string as pairs (level, contents)."""

        BracketParser.check_for_trailing_brackets(string, opening_bracket, closing_bracket)

        string_cpy = "{0}{1}{2}".format(opening_bracket, string, closing_bracket)
        enclosed = pyparsing.Forward()
        nested_parents = pyparsing.nestedExpr(opening_bracket, closing_bracket, content=enclosed)
        enclosed << (pyparsing.Word(pyparsing.alphas) | ',' | nested_parents)
        return enclosed.parseString(string_cpy).asList()[0][0]

