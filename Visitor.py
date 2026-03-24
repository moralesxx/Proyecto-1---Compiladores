from ExpresionesVisitor import ExpresionesVisitor
from ExpresionesParser import ExpresionesParser

class Simbolo:
    def __init__(self, nombre, tipo, valor=None):
        self.nombre = nombre
        self.tipo = tipo
        self.valor = valor

class Visitor(ExpresionesVisitor):
    def __init__(self):
        # Memoria del intérprete
        self.tabla_simbolos = {}

    def visitProg(self, ctx):
        print("Iniciando ejecución...")
        return self.visitChildren(ctx)

    def visitInstrDecl(self, ctx):
        # Obtenemos metadatos de la declaración
        tipo = ctx.declaracion().TIPO().getText()
        nombre = ctx.declaracion().ID().getText()
        
        valor_inicial = None
        # Si la declaración tiene una asignación (ej: int x = 5)
        if ctx.declaracion().ASIGNACION():
            valor_inicial = self.visit(ctx.declaracion().expr())
        
        if nombre in self.tabla_simbolos:
            print(f"Error Semántico: Variable '{nombre}' ya declarada.")
        else:
            # Guardamos en la tabla de símbolos
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
        # Obtenemos el tipo de token del operador (+, -, *, /)
        op = ctx.getChild(1).getSymbol().type
        
        if op == ExpresionesParser.SUMA: return izq + der
        if op == ExpresionesParser.RESTA: return izq - der
        if op == ExpresionesParser.MULT: return izq * der
        
        # CORRECCIÓN: Usamos '/' para división flotante (7.83 en lugar de 7.0)
        if op == ExpresionesParser.DIV: 
            if der == 0:
                print("Error: División por cero.")
                return 0
            return izq / der
            
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
        # Si contiene un punto, es float; si no, es int
        return float(val) if '.' in val else int(val)

    def visitVariable(self, ctx):
        nombre = ctx.ID().getText()
        if nombre in self.tabla_simbolos:
            val = self.tabla_simbolos[nombre].valor
            # Si la variable no tiene valor, devolvemos 0 por defecto
            return val if val is not None else 0
        
        print(f"Error: Variable '{nombre}' no definida.")
        return 0

    def visitInstrIf(self, ctx):
        # Evaluamos la condición
        condicion = self.visit(ctx.condicion())
        
        if condicion:
            # Ejecuta el bloque del 'if'
            return self.visit(ctx.bloque(0))
        elif ctx.bloque(1):
            # Si hay un 'else', ejecuta el bloque(1)
            return self.visit(ctx.bloque(1))
        return None

    def visitParentesisExpr(self, ctx): 
        return self.visit(ctx.expr())

    def visitParentesisCond(self, ctx): 
        return self.visit(ctx.condicion())