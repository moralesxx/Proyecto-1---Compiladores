from ExpresionesVisitor import ExpresionesVisitor
from ExpresionesParser import ExpresionesParser
from symbol_table import SymbolTable

class InterpreterVisitor(ExpresionesVisitor):
    def __init__(self, tabla=None):
        self.tabla_simbolos = tabla if tabla else SymbolTable()
        self.funciones = {} # Diccionario para guardar el cuerpo de las funciones

    def visitProg(self, ctx):
        return self.visitChildren(ctx)

    def visitBloque(self, ctx):
        self.tabla_simbolos.push_scope()
        result = None
        for instr in ctx.instrucciones():
            result = self.visit(instr)
            if result is not None and ctx.parentCtx and isinstance(ctx.parentCtx, ExpresionesParser.Funcion_declContext):
                break 
        self.tabla_simbolos.pop_scope()
        return result

    def visitInstrPrint(self, ctx):
        valor = self.visit(ctx.expr())
        print(valor.strip('"') if isinstance(valor, str) else valor)
        return None

    def visitInstrDecl(self, ctx):
        tipo = ctx.declaracion().TIPO().getText()
        nombre = ctx.declaracion().ID().getText()
        valor = self.visit(ctx.declaracion().expr()) if ctx.declaracion().ASIGNACION() else None
        self.tabla_simbolos.declarar(nombre, tipo, valor)
        return None

    def visitInstrAsig(self, ctx):
        nombre = ctx.asignacion().ID().getText()
        valor = self.visit(ctx.asignacion().expr())
        self.tabla_simbolos.asignar(nombre, valor)
        return valor

    def visitInstrFuncDecl(self, ctx):
        nombre = ctx.funcion_decl().ID().getText()
        self.funciones[nombre] = ctx.funcion_decl() # Guardamos el AST de la función
        return None

    def visitLlamadaExpr(self, ctx):
        return self.visit(ctx.llamada_func())

    def visitLlamada_func(self, ctx):
        nombre = ctx.ID().getText()
        func_ctx = self.funciones.get(nombre)
        
        # Evaluar argumentos
        args_valores = []
        if ctx.argumentos():
            for arg in ctx.argumentos().expr():
                args_valores.append(self.visit(arg))

        # Ejecutar función en nuevo ámbito
        self.tabla_simbolos.push_scope()
        if func_ctx.parametros():
            for i, val in enumerate(args_valores):
                p_nombre = func_ctx.parametros().ID(i).getText()
                p_tipo = func_ctx.parametros().TIPO(i).getText()
                self.tabla_simbolos.declarar(p_nombre, p_tipo, val)
        
        resultado = self.visit(func_ctx.bloque())
        self.tabla_simbolos.pop_scope()
        return resultado

    def visitInstrReturn(self, ctx):
        return self.visit(ctx.expr()) if ctx.expr() else None

    def visitInstrWhile(self, ctx):
        while self.visit(ctx.condicion()):
            self.visit(ctx.bloque())
        return None

    def visitAritmetica(self, ctx):
        izq = self.visit(ctx.expr(0))
        der = self.visit(ctx.expr(1))
        op = ctx.getChild(1).getText()
        if op == '+': return izq + der
        if op == '-': return izq - der
        if op == '*': return izq * der
        if op == '/': return izq / der if der != 0 else 0

    def visitRelacional(self, ctx):
        izq = self.visit(ctx.expr(0))
        der = self.visit(ctx.expr(1))
        op = ctx.op.text
        if op == '>': return izq > der
        if op == '<': return izq < der
        if op == '<=': return izq <= der
        if op == '>=': return izq >= der
        if op == '==': return izq == der
        if op == '!=': return izq != der
        return False

    def visitVariable(self, ctx):
        simb = self.tabla_simbolos.obtener(ctx.ID().getText())
        return simb.valor if simb else None

    def visitNumero(self, ctx):
        val = ctx.NUMERO().getText()
        return float(val) if '.' in val else int(val)

    def visitCadena(self, ctx): return ctx.STRING().getText()
    def visitInstrIf(self, ctx):
        if self.visit(ctx.condicion()): return self.visit(ctx.bloque(0))
        elif ctx.bloque(1): return self.visit(ctx.bloque(1))
    def visitParentesisExpr(self, ctx): return self.visit(ctx.expr())