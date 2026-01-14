# Generated from /home/runner/work/evalis/evalis/grammar/Evalis.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,28,98,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,1,0,1,0,1,0,1,1,1,1,1,1,1,1,3,1,26,8,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,5,1,49,8,1,10,1,12,1,52,9,1,1,2,1,2,1,2,5,2,57,8,2,10,
        2,12,2,60,9,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,3,
        2,74,8,2,1,3,1,3,1,3,1,3,1,3,1,3,3,3,82,8,3,1,4,1,4,1,4,1,4,3,4,
        88,8,4,1,5,1,5,1,6,1,6,1,7,1,7,1,8,1,8,1,8,0,1,2,9,0,2,4,6,8,10,
        12,14,16,0,6,1,0,2,3,1,0,4,5,1,0,6,9,1,0,10,11,1,0,25,26,1,0,22,
        23,104,0,18,1,0,0,0,2,25,1,0,0,0,4,73,1,0,0,0,6,81,1,0,0,0,8,87,
        1,0,0,0,10,89,1,0,0,0,12,91,1,0,0,0,14,93,1,0,0,0,16,95,1,0,0,0,
        18,19,3,2,1,0,19,20,5,0,0,1,20,1,1,0,0,0,21,22,6,1,-1,0,22,23,5,
        1,0,0,23,26,3,2,1,9,24,26,3,4,2,0,25,21,1,0,0,0,25,24,1,0,0,0,26,
        50,1,0,0,0,27,28,10,8,0,0,28,29,7,0,0,0,29,49,3,2,1,9,30,31,10,7,
        0,0,31,32,7,1,0,0,32,49,3,2,1,8,33,34,10,6,0,0,34,35,7,2,0,0,35,
        49,3,2,1,7,36,37,10,5,0,0,37,38,7,3,0,0,38,49,3,2,1,6,39,40,10,4,
        0,0,40,41,5,12,0,0,41,49,3,2,1,5,42,43,10,3,0,0,43,44,5,13,0,0,44,
        49,3,2,1,4,45,46,10,2,0,0,46,47,5,14,0,0,47,49,3,2,1,3,48,27,1,0,
        0,0,48,30,1,0,0,0,48,33,1,0,0,0,48,36,1,0,0,0,48,39,1,0,0,0,48,42,
        1,0,0,0,48,45,1,0,0,0,49,52,1,0,0,0,50,48,1,0,0,0,50,51,1,0,0,0,
        51,3,1,0,0,0,52,50,1,0,0,0,53,74,3,8,4,0,54,58,3,14,7,0,55,57,3,
        6,3,0,56,55,1,0,0,0,57,60,1,0,0,0,58,56,1,0,0,0,58,59,1,0,0,0,59,
        74,1,0,0,0,60,58,1,0,0,0,61,62,5,15,0,0,62,63,3,2,1,0,63,64,5,16,
        0,0,64,74,1,0,0,0,65,66,5,17,0,0,66,67,3,2,1,0,67,68,5,18,0,0,68,
        69,3,14,7,0,69,70,5,12,0,0,70,71,3,2,1,0,71,72,5,19,0,0,72,74,1,
        0,0,0,73,53,1,0,0,0,73,54,1,0,0,0,73,61,1,0,0,0,73,65,1,0,0,0,74,
        5,1,0,0,0,75,76,5,20,0,0,76,82,3,14,7,0,77,78,5,17,0,0,78,79,3,2,
        1,0,79,80,5,19,0,0,80,82,1,0,0,0,81,75,1,0,0,0,81,77,1,0,0,0,82,
        7,1,0,0,0,83,88,3,10,5,0,84,88,3,16,8,0,85,88,3,12,6,0,86,88,5,21,
        0,0,87,83,1,0,0,0,87,84,1,0,0,0,87,85,1,0,0,0,87,86,1,0,0,0,88,9,
        1,0,0,0,89,90,7,4,0,0,90,11,1,0,0,0,91,92,7,5,0,0,92,13,1,0,0,0,
        93,94,5,24,0,0,94,15,1,0,0,0,95,96,5,27,0,0,96,17,1,0,0,0,7,25,48,
        50,58,73,81,87
    ]

class EvalisParser ( Parser ):

    grammarFileName = "Evalis.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'not'", "'*'", "'/'", "'+'", "'-'", "'<'", 
                     "'<='", "'>'", "'>='", "'=='", "'!='", "'in'", "'and'", 
                     "'or'", "'('", "')'", "'['", "'for'", "']'", "'.'", 
                     "'null'", "'true'", "'false'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "IDENTIFIER", "INT", "FLOAT", "STRING", "WS" ]

    RULE_parse = 0
    RULE_expr = 1
    RULE_atom = 2
    RULE_accessSuffix = 3
    RULE_literal = 4
    RULE_number = 5
    RULE_boolean = 6
    RULE_identifier = 7
    RULE_stringLiteral = 8

    ruleNames =  [ "parse", "expr", "atom", "accessSuffix", "literal", "number", 
                   "boolean", "identifier", "stringLiteral" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    T__9=10
    T__10=11
    T__11=12
    T__12=13
    T__13=14
    T__14=15
    T__15=16
    T__16=17
    T__17=18
    T__18=19
    T__19=20
    T__20=21
    T__21=22
    T__22=23
    IDENTIFIER=24
    INT=25
    FLOAT=26
    STRING=27
    WS=28

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ParseContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expr(self):
            return self.getTypedRuleContext(EvalisParser.ExprContext,0)


        def EOF(self):
            return self.getToken(EvalisParser.EOF, 0)

        def getRuleIndex(self):
            return EvalisParser.RULE_parse

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParse" ):
                listener.enterParse(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParse" ):
                listener.exitParse(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParse" ):
                return visitor.visitParse(self)
            else:
                return visitor.visitChildren(self)




    def parse(self):

        localctx = EvalisParser.ParseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_parse)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 18
            self.expr(0)
            self.state = 19
            self.match(EvalisParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return EvalisParser.RULE_expr

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)


    class AndExprContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvalisParser.ExprContext
            super().__init__(parser)
            self.op = None # Token
            self.copyFrom(ctx)

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvalisParser.ExprContext)
            else:
                return self.getTypedRuleContext(EvalisParser.ExprContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAndExpr" ):
                listener.enterAndExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAndExpr" ):
                listener.exitAndExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAndExpr" ):
                return visitor.visitAndExpr(self)
            else:
                return visitor.visitChildren(self)


    class MulDivExprContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvalisParser.ExprContext
            super().__init__(parser)
            self.op = None # Token
            self.copyFrom(ctx)

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvalisParser.ExprContext)
            else:
                return self.getTypedRuleContext(EvalisParser.ExprContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMulDivExpr" ):
                listener.enterMulDivExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMulDivExpr" ):
                listener.exitMulDivExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMulDivExpr" ):
                return visitor.visitMulDivExpr(self)
            else:
                return visitor.visitChildren(self)


    class EqualityExprContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvalisParser.ExprContext
            super().__init__(parser)
            self.op = None # Token
            self.copyFrom(ctx)

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvalisParser.ExprContext)
            else:
                return self.getTypedRuleContext(EvalisParser.ExprContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterEqualityExpr" ):
                listener.enterEqualityExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitEqualityExpr" ):
                listener.exitEqualityExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEqualityExpr" ):
                return visitor.visitEqualityExpr(self)
            else:
                return visitor.visitChildren(self)


    class NotExprContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvalisParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expr(self):
            return self.getTypedRuleContext(EvalisParser.ExprContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNotExpr" ):
                listener.enterNotExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNotExpr" ):
                listener.exitNotExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNotExpr" ):
                return visitor.visitNotExpr(self)
            else:
                return visitor.visitChildren(self)


    class RelationalExprContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvalisParser.ExprContext
            super().__init__(parser)
            self.op = None # Token
            self.copyFrom(ctx)

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvalisParser.ExprContext)
            else:
                return self.getTypedRuleContext(EvalisParser.ExprContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRelationalExpr" ):
                listener.enterRelationalExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRelationalExpr" ):
                listener.exitRelationalExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRelationalExpr" ):
                return visitor.visitRelationalExpr(self)
            else:
                return visitor.visitChildren(self)


    class InExprContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvalisParser.ExprContext
            super().__init__(parser)
            self.op = None # Token
            self.copyFrom(ctx)

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvalisParser.ExprContext)
            else:
                return self.getTypedRuleContext(EvalisParser.ExprContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterInExpr" ):
                listener.enterInExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitInExpr" ):
                listener.exitInExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitInExpr" ):
                return visitor.visitInExpr(self)
            else:
                return visitor.visitChildren(self)


    class AtomExprContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvalisParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def atom(self):
            return self.getTypedRuleContext(EvalisParser.AtomContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAtomExpr" ):
                listener.enterAtomExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAtomExpr" ):
                listener.exitAtomExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAtomExpr" ):
                return visitor.visitAtomExpr(self)
            else:
                return visitor.visitChildren(self)


    class AddSubExprContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvalisParser.ExprContext
            super().__init__(parser)
            self.op = None # Token
            self.copyFrom(ctx)

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvalisParser.ExprContext)
            else:
                return self.getTypedRuleContext(EvalisParser.ExprContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAddSubExpr" ):
                listener.enterAddSubExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAddSubExpr" ):
                listener.exitAddSubExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAddSubExpr" ):
                return visitor.visitAddSubExpr(self)
            else:
                return visitor.visitChildren(self)


    class OrExprContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvalisParser.ExprContext
            super().__init__(parser)
            self.op = None # Token
            self.copyFrom(ctx)

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvalisParser.ExprContext)
            else:
                return self.getTypedRuleContext(EvalisParser.ExprContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOrExpr" ):
                listener.enterOrExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOrExpr" ):
                listener.exitOrExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOrExpr" ):
                return visitor.visitOrExpr(self)
            else:
                return visitor.visitChildren(self)



    def expr(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = EvalisParser.ExprContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 2
        self.enterRecursionRule(localctx, 2, self.RULE_expr, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 25
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [1]:
                localctx = EvalisParser.NotExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx

                self.state = 22
                self.match(EvalisParser.T__0)
                self.state = 23
                self.expr(9)
                pass
            elif token in [15, 17, 21, 22, 23, 24, 25, 26, 27]:
                localctx = EvalisParser.AtomExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 24
                self.atom()
                pass
            else:
                raise NoViableAltException(self)

            self._ctx.stop = self._input.LT(-1)
            self.state = 50
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,2,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 48
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
                    if la_ == 1:
                        localctx = EvalisParser.MulDivExprContext(self, EvalisParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 27
                        if not self.precpred(self._ctx, 8):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 8)")
                        self.state = 28
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not(_la==2 or _la==3):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 29
                        self.expr(9)
                        pass

                    elif la_ == 2:
                        localctx = EvalisParser.AddSubExprContext(self, EvalisParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 30
                        if not self.precpred(self._ctx, 7):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 7)")
                        self.state = 31
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not(_la==4 or _la==5):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 32
                        self.expr(8)
                        pass

                    elif la_ == 3:
                        localctx = EvalisParser.RelationalExprContext(self, EvalisParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 33
                        if not self.precpred(self._ctx, 6):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 6)")
                        self.state = 34
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 960) != 0)):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 35
                        self.expr(7)
                        pass

                    elif la_ == 4:
                        localctx = EvalisParser.EqualityExprContext(self, EvalisParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 36
                        if not self.precpred(self._ctx, 5):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 5)")
                        self.state = 37
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not(_la==10 or _la==11):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 38
                        self.expr(6)
                        pass

                    elif la_ == 5:
                        localctx = EvalisParser.InExprContext(self, EvalisParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 39
                        if not self.precpred(self._ctx, 4):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 4)")
                        self.state = 40
                        localctx.op = self.match(EvalisParser.T__11)
                        self.state = 41
                        self.expr(5)
                        pass

                    elif la_ == 6:
                        localctx = EvalisParser.AndExprContext(self, EvalisParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 42
                        if not self.precpred(self._ctx, 3):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                        self.state = 43
                        localctx.op = self.match(EvalisParser.T__12)
                        self.state = 44
                        self.expr(4)
                        pass

                    elif la_ == 7:
                        localctx = EvalisParser.OrExprContext(self, EvalisParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 45
                        if not self.precpred(self._ctx, 2):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                        self.state = 46
                        localctx.op = self.match(EvalisParser.T__13)
                        self.state = 47
                        self.expr(3)
                        pass

             
                self.state = 52
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,2,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class AtomContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return EvalisParser.RULE_atom

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class ParenAtomContext(AtomContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvalisParser.AtomContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expr(self):
            return self.getTypedRuleContext(EvalisParser.ExprContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParenAtom" ):
                listener.enterParenAtom(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParenAtom" ):
                listener.exitParenAtom(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParenAtom" ):
                return visitor.visitParenAtom(self)
            else:
                return visitor.visitChildren(self)


    class LiteralAtomContext(AtomContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvalisParser.AtomContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def literal(self):
            return self.getTypedRuleContext(EvalisParser.LiteralContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLiteralAtom" ):
                listener.enterLiteralAtom(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLiteralAtom" ):
                listener.exitLiteralAtom(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLiteralAtom" ):
                return visitor.visitLiteralAtom(self)
            else:
                return visitor.visitChildren(self)


    class IdentifierAtomContext(AtomContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvalisParser.AtomContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def identifier(self):
            return self.getTypedRuleContext(EvalisParser.IdentifierContext,0)

        def accessSuffix(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvalisParser.AccessSuffixContext)
            else:
                return self.getTypedRuleContext(EvalisParser.AccessSuffixContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIdentifierAtom" ):
                listener.enterIdentifierAtom(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIdentifierAtom" ):
                listener.exitIdentifierAtom(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIdentifierAtom" ):
                return visitor.visitIdentifierAtom(self)
            else:
                return visitor.visitChildren(self)


    class ListComprehensionContext(AtomContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a EvalisParser.AtomContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(EvalisParser.ExprContext)
            else:
                return self.getTypedRuleContext(EvalisParser.ExprContext,i)

        def identifier(self):
            return self.getTypedRuleContext(EvalisParser.IdentifierContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterListComprehension" ):
                listener.enterListComprehension(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitListComprehension" ):
                listener.exitListComprehension(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitListComprehension" ):
                return visitor.visitListComprehension(self)
            else:
                return visitor.visitChildren(self)



    def atom(self):

        localctx = EvalisParser.AtomContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_atom)
        try:
            self.state = 73
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [21, 22, 23, 25, 26, 27]:
                localctx = EvalisParser.LiteralAtomContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 53
                self.literal()
                pass
            elif token in [24]:
                localctx = EvalisParser.IdentifierAtomContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 54
                self.identifier()
                self.state = 58
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,3,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 55
                        self.accessSuffix() 
                    self.state = 60
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,3,self._ctx)

                pass
            elif token in [15]:
                localctx = EvalisParser.ParenAtomContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 61
                self.match(EvalisParser.T__14)
                self.state = 62
                self.expr(0)
                self.state = 63
                self.match(EvalisParser.T__15)
                pass
            elif token in [17]:
                localctx = EvalisParser.ListComprehensionContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 65
                self.match(EvalisParser.T__16)
                self.state = 66
                self.expr(0)
                self.state = 67
                self.match(EvalisParser.T__17)
                self.state = 68
                self.identifier()
                self.state = 69
                self.match(EvalisParser.T__11)
                self.state = 70
                self.expr(0)
                self.state = 71
                self.match(EvalisParser.T__18)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AccessSuffixContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def identifier(self):
            return self.getTypedRuleContext(EvalisParser.IdentifierContext,0)


        def expr(self):
            return self.getTypedRuleContext(EvalisParser.ExprContext,0)


        def getRuleIndex(self):
            return EvalisParser.RULE_accessSuffix

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAccessSuffix" ):
                listener.enterAccessSuffix(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAccessSuffix" ):
                listener.exitAccessSuffix(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAccessSuffix" ):
                return visitor.visitAccessSuffix(self)
            else:
                return visitor.visitChildren(self)




    def accessSuffix(self):

        localctx = EvalisParser.AccessSuffixContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_accessSuffix)
        try:
            self.state = 81
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [20]:
                self.enterOuterAlt(localctx, 1)
                self.state = 75
                self.match(EvalisParser.T__19)
                self.state = 76
                self.identifier()
                pass
            elif token in [17]:
                self.enterOuterAlt(localctx, 2)
                self.state = 77
                self.match(EvalisParser.T__16)
                self.state = 78
                self.expr(0)
                self.state = 79
                self.match(EvalisParser.T__18)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LiteralContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def number(self):
            return self.getTypedRuleContext(EvalisParser.NumberContext,0)


        def stringLiteral(self):
            return self.getTypedRuleContext(EvalisParser.StringLiteralContext,0)


        def boolean(self):
            return self.getTypedRuleContext(EvalisParser.BooleanContext,0)


        def getRuleIndex(self):
            return EvalisParser.RULE_literal

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLiteral" ):
                listener.enterLiteral(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLiteral" ):
                listener.exitLiteral(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLiteral" ):
                return visitor.visitLiteral(self)
            else:
                return visitor.visitChildren(self)




    def literal(self):

        localctx = EvalisParser.LiteralContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_literal)
        try:
            self.state = 87
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [25, 26]:
                self.enterOuterAlt(localctx, 1)
                self.state = 83
                self.number()
                pass
            elif token in [27]:
                self.enterOuterAlt(localctx, 2)
                self.state = 84
                self.stringLiteral()
                pass
            elif token in [22, 23]:
                self.enterOuterAlt(localctx, 3)
                self.state = 85
                self.boolean()
                pass
            elif token in [21]:
                self.enterOuterAlt(localctx, 4)
                self.state = 86
                self.match(EvalisParser.T__20)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NumberContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INT(self):
            return self.getToken(EvalisParser.INT, 0)

        def FLOAT(self):
            return self.getToken(EvalisParser.FLOAT, 0)

        def getRuleIndex(self):
            return EvalisParser.RULE_number

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNumber" ):
                listener.enterNumber(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNumber" ):
                listener.exitNumber(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNumber" ):
                return visitor.visitNumber(self)
            else:
                return visitor.visitChildren(self)




    def number(self):

        localctx = EvalisParser.NumberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_number)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 89
            _la = self._input.LA(1)
            if not(_la==25 or _la==26):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class BooleanContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return EvalisParser.RULE_boolean

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBoolean" ):
                listener.enterBoolean(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBoolean" ):
                listener.exitBoolean(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBoolean" ):
                return visitor.visitBoolean(self)
            else:
                return visitor.visitChildren(self)




    def boolean(self):

        localctx = EvalisParser.BooleanContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_boolean)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 91
            _la = self._input.LA(1)
            if not(_la==22 or _la==23):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IdentifierContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(EvalisParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return EvalisParser.RULE_identifier

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIdentifier" ):
                listener.enterIdentifier(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIdentifier" ):
                listener.exitIdentifier(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIdentifier" ):
                return visitor.visitIdentifier(self)
            else:
                return visitor.visitChildren(self)




    def identifier(self):

        localctx = EvalisParser.IdentifierContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_identifier)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 93
            self.match(EvalisParser.IDENTIFIER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StringLiteralContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(EvalisParser.STRING, 0)

        def getRuleIndex(self):
            return EvalisParser.RULE_stringLiteral

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStringLiteral" ):
                listener.enterStringLiteral(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStringLiteral" ):
                listener.exitStringLiteral(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStringLiteral" ):
                return visitor.visitStringLiteral(self)
            else:
                return visitor.visitChildren(self)




    def stringLiteral(self):

        localctx = EvalisParser.StringLiteralContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_stringLiteral)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 95
            self.match(EvalisParser.STRING)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[1] = self.expr_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def expr_sempred(self, localctx:ExprContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 8)
         

            if predIndex == 1:
                return self.precpred(self._ctx, 7)
         

            if predIndex == 2:
                return self.precpred(self._ctx, 6)
         

            if predIndex == 3:
                return self.precpred(self._ctx, 5)
         

            if predIndex == 4:
                return self.precpred(self._ctx, 4)
         

            if predIndex == 5:
                return self.precpred(self._ctx, 3)
         

            if predIndex == 6:
                return self.precpred(self._ctx, 2)
         




