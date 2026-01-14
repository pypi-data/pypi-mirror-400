# Generated from /home/runner/work/evalis/evalis/grammar/Evalis.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .EvalisParser import EvalisParser
else:
    from EvalisParser import EvalisParser

# This class defines a complete listener for a parse tree produced by EvalisParser.
class EvalisListener(ParseTreeListener):

    # Enter a parse tree produced by EvalisParser#parse.
    def enterParse(self, ctx:EvalisParser.ParseContext):
        pass

    # Exit a parse tree produced by EvalisParser#parse.
    def exitParse(self, ctx:EvalisParser.ParseContext):
        pass


    # Enter a parse tree produced by EvalisParser#AndExpr.
    def enterAndExpr(self, ctx:EvalisParser.AndExprContext):
        pass

    # Exit a parse tree produced by EvalisParser#AndExpr.
    def exitAndExpr(self, ctx:EvalisParser.AndExprContext):
        pass


    # Enter a parse tree produced by EvalisParser#MulDivExpr.
    def enterMulDivExpr(self, ctx:EvalisParser.MulDivExprContext):
        pass

    # Exit a parse tree produced by EvalisParser#MulDivExpr.
    def exitMulDivExpr(self, ctx:EvalisParser.MulDivExprContext):
        pass


    # Enter a parse tree produced by EvalisParser#EqualityExpr.
    def enterEqualityExpr(self, ctx:EvalisParser.EqualityExprContext):
        pass

    # Exit a parse tree produced by EvalisParser#EqualityExpr.
    def exitEqualityExpr(self, ctx:EvalisParser.EqualityExprContext):
        pass


    # Enter a parse tree produced by EvalisParser#NotExpr.
    def enterNotExpr(self, ctx:EvalisParser.NotExprContext):
        pass

    # Exit a parse tree produced by EvalisParser#NotExpr.
    def exitNotExpr(self, ctx:EvalisParser.NotExprContext):
        pass


    # Enter a parse tree produced by EvalisParser#RelationalExpr.
    def enterRelationalExpr(self, ctx:EvalisParser.RelationalExprContext):
        pass

    # Exit a parse tree produced by EvalisParser#RelationalExpr.
    def exitRelationalExpr(self, ctx:EvalisParser.RelationalExprContext):
        pass


    # Enter a parse tree produced by EvalisParser#InExpr.
    def enterInExpr(self, ctx:EvalisParser.InExprContext):
        pass

    # Exit a parse tree produced by EvalisParser#InExpr.
    def exitInExpr(self, ctx:EvalisParser.InExprContext):
        pass


    # Enter a parse tree produced by EvalisParser#AtomExpr.
    def enterAtomExpr(self, ctx:EvalisParser.AtomExprContext):
        pass

    # Exit a parse tree produced by EvalisParser#AtomExpr.
    def exitAtomExpr(self, ctx:EvalisParser.AtomExprContext):
        pass


    # Enter a parse tree produced by EvalisParser#AddSubExpr.
    def enterAddSubExpr(self, ctx:EvalisParser.AddSubExprContext):
        pass

    # Exit a parse tree produced by EvalisParser#AddSubExpr.
    def exitAddSubExpr(self, ctx:EvalisParser.AddSubExprContext):
        pass


    # Enter a parse tree produced by EvalisParser#OrExpr.
    def enterOrExpr(self, ctx:EvalisParser.OrExprContext):
        pass

    # Exit a parse tree produced by EvalisParser#OrExpr.
    def exitOrExpr(self, ctx:EvalisParser.OrExprContext):
        pass


    # Enter a parse tree produced by EvalisParser#LiteralAtom.
    def enterLiteralAtom(self, ctx:EvalisParser.LiteralAtomContext):
        pass

    # Exit a parse tree produced by EvalisParser#LiteralAtom.
    def exitLiteralAtom(self, ctx:EvalisParser.LiteralAtomContext):
        pass


    # Enter a parse tree produced by EvalisParser#IdentifierAtom.
    def enterIdentifierAtom(self, ctx:EvalisParser.IdentifierAtomContext):
        pass

    # Exit a parse tree produced by EvalisParser#IdentifierAtom.
    def exitIdentifierAtom(self, ctx:EvalisParser.IdentifierAtomContext):
        pass


    # Enter a parse tree produced by EvalisParser#ParenAtom.
    def enterParenAtom(self, ctx:EvalisParser.ParenAtomContext):
        pass

    # Exit a parse tree produced by EvalisParser#ParenAtom.
    def exitParenAtom(self, ctx:EvalisParser.ParenAtomContext):
        pass


    # Enter a parse tree produced by EvalisParser#ListComprehension.
    def enterListComprehension(self, ctx:EvalisParser.ListComprehensionContext):
        pass

    # Exit a parse tree produced by EvalisParser#ListComprehension.
    def exitListComprehension(self, ctx:EvalisParser.ListComprehensionContext):
        pass


    # Enter a parse tree produced by EvalisParser#accessSuffix.
    def enterAccessSuffix(self, ctx:EvalisParser.AccessSuffixContext):
        pass

    # Exit a parse tree produced by EvalisParser#accessSuffix.
    def exitAccessSuffix(self, ctx:EvalisParser.AccessSuffixContext):
        pass


    # Enter a parse tree produced by EvalisParser#literal.
    def enterLiteral(self, ctx:EvalisParser.LiteralContext):
        pass

    # Exit a parse tree produced by EvalisParser#literal.
    def exitLiteral(self, ctx:EvalisParser.LiteralContext):
        pass


    # Enter a parse tree produced by EvalisParser#number.
    def enterNumber(self, ctx:EvalisParser.NumberContext):
        pass

    # Exit a parse tree produced by EvalisParser#number.
    def exitNumber(self, ctx:EvalisParser.NumberContext):
        pass


    # Enter a parse tree produced by EvalisParser#boolean.
    def enterBoolean(self, ctx:EvalisParser.BooleanContext):
        pass

    # Exit a parse tree produced by EvalisParser#boolean.
    def exitBoolean(self, ctx:EvalisParser.BooleanContext):
        pass


    # Enter a parse tree produced by EvalisParser#identifier.
    def enterIdentifier(self, ctx:EvalisParser.IdentifierContext):
        pass

    # Exit a parse tree produced by EvalisParser#identifier.
    def exitIdentifier(self, ctx:EvalisParser.IdentifierContext):
        pass


    # Enter a parse tree produced by EvalisParser#stringLiteral.
    def enterStringLiteral(self, ctx:EvalisParser.StringLiteralContext):
        pass

    # Exit a parse tree produced by EvalisParser#stringLiteral.
    def exitStringLiteral(self, ctx:EvalisParser.StringLiteralContext):
        pass



del EvalisParser