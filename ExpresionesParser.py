# Generated from Expresiones.g by ANTLR 4.13.1
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
        4,1,23,82,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,1,0,1,0,1,0,4,0,18,8,0,11,0,12,0,19,1,0,1,0,1,0,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,38,8,1,3,1,40,8,1,1,2,
        1,2,5,2,44,8,2,10,2,12,2,47,9,2,1,2,1,2,1,3,1,3,1,3,1,4,1,4,1,4,
        1,4,1,5,1,5,1,5,1,5,1,5,1,5,1,5,3,5,65,8,5,1,5,1,5,1,5,1,5,1,5,1,
        5,5,5,73,8,5,10,5,12,5,76,9,5,1,6,1,6,1,6,1,6,1,6,0,1,10,7,0,2,4,
        6,8,10,12,0,3,1,0,21,22,1,0,19,20,1,0,11,16,83,0,14,1,0,0,0,2,39,
        1,0,0,0,4,41,1,0,0,0,6,50,1,0,0,0,8,53,1,0,0,0,10,64,1,0,0,0,12,
        77,1,0,0,0,14,15,5,1,0,0,15,17,5,2,0,0,16,18,3,2,1,0,17,16,1,0,0,
        0,18,19,1,0,0,0,19,17,1,0,0,0,19,20,1,0,0,0,20,21,1,0,0,0,21,22,
        5,3,0,0,22,23,5,0,0,1,23,1,1,0,0,0,24,25,3,6,3,0,25,26,5,4,0,0,26,
        40,1,0,0,0,27,28,3,8,4,0,28,29,5,4,0,0,29,40,1,0,0,0,30,31,5,5,0,
        0,31,32,5,6,0,0,32,33,3,12,6,0,33,34,5,7,0,0,34,37,3,4,2,0,35,36,
        5,8,0,0,36,38,3,4,2,0,37,35,1,0,0,0,37,38,1,0,0,0,38,40,1,0,0,0,
        39,24,1,0,0,0,39,27,1,0,0,0,39,30,1,0,0,0,40,3,1,0,0,0,41,45,5,2,
        0,0,42,44,3,2,1,0,43,42,1,0,0,0,44,47,1,0,0,0,45,43,1,0,0,0,45,46,
        1,0,0,0,46,48,1,0,0,0,47,45,1,0,0,0,48,49,5,3,0,0,49,5,1,0,0,0,50,
        51,5,9,0,0,51,52,5,17,0,0,52,7,1,0,0,0,53,54,5,17,0,0,54,55,5,10,
        0,0,55,56,3,10,5,0,56,9,1,0,0,0,57,58,6,5,-1,0,58,65,5,18,0,0,59,
        65,5,17,0,0,60,61,5,6,0,0,61,62,3,10,5,0,62,63,5,7,0,0,63,65,1,0,
        0,0,64,57,1,0,0,0,64,59,1,0,0,0,64,60,1,0,0,0,65,74,1,0,0,0,66,67,
        10,5,0,0,67,68,7,0,0,0,68,73,3,10,5,6,69,70,10,4,0,0,70,71,7,1,0,
        0,71,73,3,10,5,5,72,66,1,0,0,0,72,69,1,0,0,0,73,76,1,0,0,0,74,72,
        1,0,0,0,74,75,1,0,0,0,75,11,1,0,0,0,76,74,1,0,0,0,77,78,3,10,5,0,
        78,79,7,2,0,0,79,80,3,10,5,0,80,13,1,0,0,0,7,19,37,39,45,64,72,74
    ]

class ExpresionesParser ( Parser ):

    grammarFileName = "Expresiones.g"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'program'", "'{'", "'}'", "';'", "'if'", 
                     "'('", "')'", "'else'", "'int'", "'='", "'>'", "'<'", 
                     "'=='", "'>='", "'<='", "'!='", "<INVALID>", "<INVALID>", 
                     "'+'", "'-'", "'*'", "'/'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "ID", "NUM", "SUM", "RES", "MUL", "DIV", 
                      "COMENTARIO" ]

    RULE_root = 0
    RULE_instrucciones = 1
    RULE_bloque = 2
    RULE_declaracion = 3
    RULE_asignacion = 4
    RULE_expr = 5
    RULE_exprRelacional = 6

    ruleNames =  [ "root", "instrucciones", "bloque", "declaracion", "asignacion", 
                   "expr", "exprRelacional" ]

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
    ID=17
    NUM=18
    SUM=19
    RES=20
    MUL=21
    DIV=22
    COMENTARIO=23

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class RootContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return ExpresionesParser.RULE_root

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class ProgContext(RootContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a ExpresionesParser.RootContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def EOF(self):
            return self.getToken(ExpresionesParser.EOF, 0)
        def instrucciones(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ExpresionesParser.InstruccionesContext)
            else:
                return self.getTypedRuleContext(ExpresionesParser.InstruccionesContext,i)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitProg" ):
                return visitor.visitProg(self)
            else:
                return visitor.visitChildren(self)



    def root(self):

        localctx = ExpresionesParser.RootContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_root)
        self._la = 0 # Token type
        try:
            localctx = ExpresionesParser.ProgContext(self, localctx)
            self.enterOuterAlt(localctx, 1)
            self.state = 14
            self.match(ExpresionesParser.T__0)
            self.state = 15
            self.match(ExpresionesParser.T__1)
            self.state = 17 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 16
                self.instrucciones()
                self.state = 19 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 131616) != 0)):
                    break

            self.state = 21
            self.match(ExpresionesParser.T__2)
            self.state = 22
            self.match(ExpresionesParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class InstruccionesContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return ExpresionesParser.RULE_instrucciones

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class InstrAsigContext(InstruccionesContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a ExpresionesParser.InstruccionesContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def asignacion(self):
            return self.getTypedRuleContext(ExpresionesParser.AsignacionContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitInstrAsig" ):
                return visitor.visitInstrAsig(self)
            else:
                return visitor.visitChildren(self)


    class InstrDeclContext(InstruccionesContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a ExpresionesParser.InstruccionesContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def declaracion(self):
            return self.getTypedRuleContext(ExpresionesParser.DeclaracionContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitInstrDecl" ):
                return visitor.visitInstrDecl(self)
            else:
                return visitor.visitChildren(self)


    class InstrIfContext(InstruccionesContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a ExpresionesParser.InstruccionesContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def exprRelacional(self):
            return self.getTypedRuleContext(ExpresionesParser.ExprRelacionalContext,0)

        def bloque(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ExpresionesParser.BloqueContext)
            else:
                return self.getTypedRuleContext(ExpresionesParser.BloqueContext,i)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitInstrIf" ):
                return visitor.visitInstrIf(self)
            else:
                return visitor.visitChildren(self)



    def instrucciones(self):

        localctx = ExpresionesParser.InstruccionesContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_instrucciones)
        self._la = 0 # Token type
        try:
            self.state = 39
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [9]:
                localctx = ExpresionesParser.InstrDeclContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 24
                self.declaracion()
                self.state = 25
                self.match(ExpresionesParser.T__3)
                pass
            elif token in [17]:
                localctx = ExpresionesParser.InstrAsigContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 27
                self.asignacion()
                self.state = 28
                self.match(ExpresionesParser.T__3)
                pass
            elif token in [5]:
                localctx = ExpresionesParser.InstrIfContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 30
                self.match(ExpresionesParser.T__4)
                self.state = 31
                self.match(ExpresionesParser.T__5)
                self.state = 32
                self.exprRelacional()
                self.state = 33
                self.match(ExpresionesParser.T__6)
                self.state = 34
                self.bloque()
                self.state = 37
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==8:
                    self.state = 35
                    self.match(ExpresionesParser.T__7)
                    self.state = 36
                    self.bloque()


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


    class BloqueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def instrucciones(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ExpresionesParser.InstruccionesContext)
            else:
                return self.getTypedRuleContext(ExpresionesParser.InstruccionesContext,i)


        def getRuleIndex(self):
            return ExpresionesParser.RULE_bloque

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBloque" ):
                return visitor.visitBloque(self)
            else:
                return visitor.visitChildren(self)




    def bloque(self):

        localctx = ExpresionesParser.BloqueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_bloque)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 41
            self.match(ExpresionesParser.T__1)
            self.state = 45
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 131616) != 0):
                self.state = 42
                self.instrucciones()
                self.state = 47
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 48
            self.match(ExpresionesParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DeclaracionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(ExpresionesParser.ID, 0)

        def getRuleIndex(self):
            return ExpresionesParser.RULE_declaracion

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDeclaracion" ):
                return visitor.visitDeclaracion(self)
            else:
                return visitor.visitChildren(self)




    def declaracion(self):

        localctx = ExpresionesParser.DeclaracionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_declaracion)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 50
            self.match(ExpresionesParser.T__8)
            self.state = 51
            self.match(ExpresionesParser.ID)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AsignacionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(ExpresionesParser.ID, 0)

        def expr(self):
            return self.getTypedRuleContext(ExpresionesParser.ExprContext,0)


        def getRuleIndex(self):
            return ExpresionesParser.RULE_asignacion

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAsignacion" ):
                return visitor.visitAsignacion(self)
            else:
                return visitor.visitChildren(self)




    def asignacion(self):

        localctx = ExpresionesParser.AsignacionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_asignacion)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 53
            self.match(ExpresionesParser.ID)
            self.state = 54
            self.match(ExpresionesParser.T__9)
            self.state = 55
            self.expr(0)
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
            return ExpresionesParser.RULE_expr

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)


    class NumeroContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a ExpresionesParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUM(self):
            return self.getToken(ExpresionesParser.NUM, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNumero" ):
                return visitor.visitNumero(self)
            else:
                return visitor.visitChildren(self)


    class VariableContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a ExpresionesParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def ID(self):
            return self.getToken(ExpresionesParser.ID, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitVariable" ):
                return visitor.visitVariable(self)
            else:
                return visitor.visitChildren(self)


    class AritmeticaContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a ExpresionesParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ExpresionesParser.ExprContext)
            else:
                return self.getTypedRuleContext(ExpresionesParser.ExprContext,i)

        def MUL(self):
            return self.getToken(ExpresionesParser.MUL, 0)
        def DIV(self):
            return self.getToken(ExpresionesParser.DIV, 0)
        def SUM(self):
            return self.getToken(ExpresionesParser.SUM, 0)
        def RES(self):
            return self.getToken(ExpresionesParser.RES, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAritmetica" ):
                return visitor.visitAritmetica(self)
            else:
                return visitor.visitChildren(self)


    class ParentesisContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a ExpresionesParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expr(self):
            return self.getTypedRuleContext(ExpresionesParser.ExprContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParentesis" ):
                return visitor.visitParentesis(self)
            else:
                return visitor.visitChildren(self)



    def expr(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = ExpresionesParser.ExprContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 10
        self.enterRecursionRule(localctx, 10, self.RULE_expr, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 64
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [18]:
                localctx = ExpresionesParser.NumeroContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx

                self.state = 58
                self.match(ExpresionesParser.NUM)
                pass
            elif token in [17]:
                localctx = ExpresionesParser.VariableContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 59
                self.match(ExpresionesParser.ID)
                pass
            elif token in [6]:
                localctx = ExpresionesParser.ParentesisContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 60
                self.match(ExpresionesParser.T__5)
                self.state = 61
                self.expr(0)
                self.state = 62
                self.match(ExpresionesParser.T__6)
                pass
            else:
                raise NoViableAltException(self)

            self._ctx.stop = self._input.LT(-1)
            self.state = 74
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,6,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 72
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,5,self._ctx)
                    if la_ == 1:
                        localctx = ExpresionesParser.AritmeticaContext(self, ExpresionesParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 66
                        if not self.precpred(self._ctx, 5):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 5)")
                        self.state = 67
                        _la = self._input.LA(1)
                        if not(_la==21 or _la==22):
                            self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 68
                        self.expr(6)
                        pass

                    elif la_ == 2:
                        localctx = ExpresionesParser.AritmeticaContext(self, ExpresionesParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 69
                        if not self.precpred(self._ctx, 4):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 4)")
                        self.state = 70
                        _la = self._input.LA(1)
                        if not(_la==19 or _la==20):
                            self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 71
                        self.expr(5)
                        pass

             
                self.state = 76
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,6,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class ExprRelacionalContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return ExpresionesParser.RULE_exprRelacional

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class RelacionalContext(ExprRelacionalContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a ExpresionesParser.ExprRelacionalContext
            super().__init__(parser)
            self.op = None # Token
            self.copyFrom(ctx)

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ExpresionesParser.ExprContext)
            else:
                return self.getTypedRuleContext(ExpresionesParser.ExprContext,i)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRelacional" ):
                return visitor.visitRelacional(self)
            else:
                return visitor.visitChildren(self)



    def exprRelacional(self):

        localctx = ExpresionesParser.ExprRelacionalContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_exprRelacional)
        self._la = 0 # Token type
        try:
            localctx = ExpresionesParser.RelacionalContext(self, localctx)
            self.enterOuterAlt(localctx, 1)
            self.state = 77
            self.expr(0)
            self.state = 78
            localctx.op = self._input.LT(1)
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 129024) != 0)):
                localctx.op = self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 79
            self.expr(0)
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
        self._predicates[5] = self.expr_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def expr_sempred(self, localctx:ExprContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 5)
         

            if predIndex == 1:
                return self.precpred(self._ctx, 4)
         




