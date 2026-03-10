from ExpresionesVisitor import ExpresionesVisitor
from ExpresionesParser import ExpresionesParser

class Simbolo:
    def __init__(self, nombre, tipo, valor=None):
        self.nombre = nombre
        self.tipo = tipo
        self.valor = valor

class Visitor(ExpresionesVisitor):
    def __init__(self):
        self.tabla_simbolos = {}

    def visitProg(self, ctx):
        print("Iniciando ejecución...")
        return self.visitChildren(ctx)

    def visitInstrDecl(self, ctx):
        tipo = ctx.declaracion().TIPO().getText()
        nombre = ctx.declaracion().ID().getText()
        
        valor_inicial = None
        if ctx.declaracion().ASIGNACION():
            valor_inicial = self.visit(ctx.declaracion().expr())
        
        if nombre in self.tabla_simbolos:
            print(f"Error Semántico: Variable '{nombre}' ya declarada.")
        else:
            self.tabla_simbolos[nombre] = Simbolo(nombre, tipo, valor_inicial)
            print(f"Declaración: {nombre} ({tipo}) = {valor_inicial}")
        return None

    def visitInstrAsig(self, ctx):
        nombre = ctx.asignacion().ID().getText()
        valor = self.visit(ctx.asignacion().expr())
        
        if nombre in self.tabla_simbolos:
            self.tabla_simbolos[nombre].valor = valor
            print(f"Asignación: {nombre} = {valor}")
        else:
            print(f"Error: Variable '{nombre}' no declarada.")
        return valor

    def visitAritmetica(self, ctx):
        izq = self.visit(ctx.expr(0))
        der = self.visit(ctx.expr(1))
        op = ctx.getChild(1).getSymbol().type
        
        if op == ExpresionesParser.SUMA: return izq + der
        if op == ExpresionesParser.RESTA: return izq - der
        if op == ExpresionesParser.MULT: return izq * der
        if op == ExpresionesParser.DIV: return izq // der if der != 0 else 0
        return 0

    def visitRelacional(self, ctx):
        izq = self.visit(ctx.expr(0))
        der = self.visit(ctx.expr(1))
        op = ctx.op.type
        
        if op == ExpresionesParser.MAYOR: return izq > der
        if op == ExpresionesParser.MENOR: return izq < der
        if op == ExpresionesParser.IGUAL: return izq == der
        if op == ExpresionesParser.DIFERENTE: return izq != der
        if op == ExpresionesParser.MAYOR_IGUAL: return izq >= der
        if op == ExpresionesParser.MENOR_IGUAL: return izq <= der
        return False

    def visitLogica(self, ctx):
        izq = self.visit(ctx.condicion(0))
        der = self.visit(ctx.condicion(1))
        op = ctx.getChild(1).getSymbol().type
        if op == ExpresionesParser.Y_LOGICO: return bool(izq and der)
        if op == ExpresionesParser.O_LOGICO: return bool(izq or der)
        return False

    def visitNotLogica(self, ctx):
        return not self.visit(ctx.condicion())

    def visitNumero(self, ctx):
        val = ctx.NUMERO().getText()
        return float(val) if '.' in val else int(val)

    def visitVariable(self, ctx):
        nombre = ctx.ID().getText()
        if nombre in self.tabla_simbolos:
            val = self.tabla_simbolos[nombre].valor
            return val if val is not None else 0
        return 0

    def visitInstrIf(self, ctx):
        if self.visit(ctx.condicion()):
            return self.visit(ctx.bloque(0))
        elif ctx.bloque(1):
            return self.visit(ctx.bloque(1))
        return None

    def visitParentesisExpr(self, ctx): return self.visit(ctx.expr())
    def visitParentesisCond(self, ctx): return self.visit(ctx.condicion())