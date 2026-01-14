from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener

from evalis.__gen__.EvalisParser import EvalisParser
from evalis.__gen__.EvalisLexer import EvalisLexer

from evalis.error import syntax_error
from evalis.types import SyntaxMessage


class SyntaxErrorCollector(ErrorListener):
    errors: list[SyntaxMessage]

    def __init__(self):
        super(SyntaxErrorCollector, self).__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        # TODO: What other info can we collect from here?
        error = SyntaxMessage(line=line, column=column, message=msg)
        self.errors.append(error)


def parse_expression_tree(expression: str) -> EvalisParser.ParseContext:
    input_stream = InputStream(expression)
    lexer = EvalisLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = EvalisParser(stream)

    error_collector = SyntaxErrorCollector()
    parser.removeErrorListeners()
    parser.addErrorListener(error_collector)
    tree = parser.parse()

    if error_collector.errors:
        raise syntax_error(error_collector.errors)

    return tree
