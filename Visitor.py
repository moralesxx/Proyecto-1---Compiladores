from ExpresionesVisitor import ExpresionesVisitor
from ExpresionesParser import ExpresionesParser

class Visitor(ExpresionesVisitor):
    def __init__(self):
        self.memoria = {}

    def visitProg(self, ctx):
        return self.visitChildren(ctx)

    def visitInstrAsig(self, ctx):
        nombre_var = ctx.asignacion().ID().getText()
        valor = self.visit(ctx.asignacion().expr())
        self.memoria[nombre_var] = valor
        print(f"Asignación: {nombre_var} = {valor}")
        return valor

    def visitAritmetica(self, ctx):
        izq = self.visit(ctx.expr(0))
        der = self.visit(ctx.expr(1))
        op = ctx.getChild(1).getText()
        
        # Validación de seguridad para evitar el error de NoneType
        if izq is None or der is None:
            return 0

        if op == '+': return izq + der
        if op == '-': return izq - der
        if op == '*': return izq * der
        if op == '/': return izq // der # Usamos // para división entera
        return 0

    def visitNumero(self, ctx):
        return int(ctx.NUM().getText())

    def visitVariable(self, ctx):
        nombre = ctx.ID().getText()
        if nombre in self.memoria:
            return self.memoria[nombre]
        print(f"Error: Variable '{nombre}' no definida.")
        return 0

    # ESTA ES LA FUNCIÓN QUE TE FALTABA
    def visitParentesis(self, ctx):
        return self.visit(ctx.expr())

    def visitInstrIf(self, ctx):
        condicion = self.visit(ctx.exprRelacional())
        if condicion:
            return self.visit(ctx.bloque(0))
        elif ctx.bloque(1): 
            return self.visit(ctx.bloque(1))
        return None

    def visitRelacional(self, ctx):
        izq = self.visit(ctx.expr(0))
        der = self.visit(ctx.expr(1))
        op = ctx.op.text
        
        if op == '>': return izq > der
        if op == '<': return izq < der
        if op == '==': return izq == der
        if op == '!=': return izq != der
        if op == '>=': return izq >= der
        if op == '<=': return izq <= der
        return False
    
    # Manejo de bloques para el IF y ELSE
    def visitBloque(self, ctx):
        return self.visitChildren(ctx)