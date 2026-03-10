# Generated from Expresiones.g by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .ExpresionesParser import ExpresionesParser
else:
    from ExpresionesParser import ExpresionesParser

# This class defines a complete generic visitor for a parse tree produced by ExpresionesParser.

class ExpresionesVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by ExpresionesParser#Prog.
    def visitProg(self, ctx:ExpresionesParser.ProgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExpresionesParser#InstrDecl.
    def visitInstrDecl(self, ctx:ExpresionesParser.InstrDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExpresionesParser#InstrAsig.
    def visitInstrAsig(self, ctx:ExpresionesParser.InstrAsigContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExpresionesParser#InstrIf.
    def visitInstrIf(self, ctx:ExpresionesParser.InstrIfContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExpresionesParser#bloque.
    def visitBloque(self, ctx:ExpresionesParser.BloqueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExpresionesParser#declaracion.
    def visitDeclaracion(self, ctx:ExpresionesParser.DeclaracionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExpresionesParser#asignacion.
    def visitAsignacion(self, ctx:ExpresionesParser.AsignacionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExpresionesParser#Numero.
    def visitNumero(self, ctx:ExpresionesParser.NumeroContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExpresionesParser#Variable.
    def visitVariable(self, ctx:ExpresionesParser.VariableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExpresionesParser#Aritmetica.
    def visitAritmetica(self, ctx:ExpresionesParser.AritmeticaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExpresionesParser#Parentesis.
    def visitParentesis(self, ctx:ExpresionesParser.ParentesisContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExpresionesParser#Relacional.
    def visitRelacional(self, ctx:ExpresionesParser.RelacionalContext):
        return self.visitChildren(ctx)



del ExpresionesParser