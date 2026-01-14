# Generated from /home/runner/work/evalis/evalis/grammar/Evalis.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .EvalisParser import EvalisParser
else:
    from EvalisParser import EvalisParser

# This class defines a complete generic visitor for a parse tree produced by EvalisParser.

class EvalisVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by EvalisParser#parse.
    def visitParse(self, ctx:EvalisParser.ParseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvalisParser#AndExpr.
    def visitAndExpr(self, ctx:EvalisParser.AndExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvalisParser#MulDivExpr.
    def visitMulDivExpr(self, ctx:EvalisParser.MulDivExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvalisParser#EqualityExpr.
    def visitEqualityExpr(self, ctx:EvalisParser.EqualityExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvalisParser#NotExpr.
    def visitNotExpr(self, ctx:EvalisParser.NotExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvalisParser#RelationalExpr.
    def visitRelationalExpr(self, ctx:EvalisParser.RelationalExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvalisParser#InExpr.
    def visitInExpr(self, ctx:EvalisParser.InExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvalisParser#AtomExpr.
    def visitAtomExpr(self, ctx:EvalisParser.AtomExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvalisParser#AddSubExpr.
    def visitAddSubExpr(self, ctx:EvalisParser.AddSubExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvalisParser#OrExpr.
    def visitOrExpr(self, ctx:EvalisParser.OrExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvalisParser#LiteralAtom.
    def visitLiteralAtom(self, ctx:EvalisParser.LiteralAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvalisParser#IdentifierAtom.
    def visitIdentifierAtom(self, ctx:EvalisParser.IdentifierAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvalisParser#ParenAtom.
    def visitParenAtom(self, ctx:EvalisParser.ParenAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvalisParser#ListComprehension.
    def visitListComprehension(self, ctx:EvalisParser.ListComprehensionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvalisParser#accessSuffix.
    def visitAccessSuffix(self, ctx:EvalisParser.AccessSuffixContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvalisParser#literal.
    def visitLiteral(self, ctx:EvalisParser.LiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvalisParser#number.
    def visitNumber(self, ctx:EvalisParser.NumberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvalisParser#boolean.
    def visitBoolean(self, ctx:EvalisParser.BooleanContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvalisParser#identifier.
    def visitIdentifier(self, ctx:EvalisParser.IdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by EvalisParser#stringLiteral.
    def visitStringLiteral(self, ctx:EvalisParser.StringLiteralContext):
        return self.visitChildren(ctx)



del EvalisParser