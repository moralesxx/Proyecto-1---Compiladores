from ExpresionesVisitor import ExpresionesVisitor
from ExpresionesParser import ExpresionesParser
from symbol_table import SymbolTable

class SemanticVisitor(ExpresionesVisitor):
    def __init__(self):
        self.tabla_simbolos = SymbolTable()
        self.errores = []

    def reportar_error(self, ctx, mensaje):
        linea = ctx.start.line
        columna = ctx.start.column
        self.errores.append(f"[Error Semántico] Línea {linea}, Columna {columna}: {mensaje}")

    def visitProg(self, ctx):
        return self.visitChildren(ctx)

    def visitBloque(self, ctx):
        self.tabla_simbolos.push_scope()
        result = self.visitChildren(ctx)
        self.tabla_simbolos.pop_scope()
        return result

    def visitInstrDecl(self, ctx):
        tipo = ctx.declaracion().TIPO().getText()
        nombre = ctx.declaracion().ID().getText()
        exito, msg = self.tabla_simbolos.declarar(nombre, tipo)
        if not exito:
            self.reportar_error(ctx, msg)
        if ctx.declaracion().ASIGNACION():
            tipo_expr = self.visit(ctx.declaracion().expr())
            if tipo_expr != tipo and not (tipo == "float" and tipo_expr == "int"):
                self.reportar_error(ctx, f"Incompatibilidad de tipos. No se puede asignar {tipo_expr} a {tipo}.")
        return tipo

    def visitInstrAsig(self, ctx):
        nombre = ctx.asignacion().ID().getText()
        simbolo = self.tabla_simbolos.obtener(nombre)
        if not simbolo:
            self.reportar_error(ctx, f"Variable '{nombre}' no declarada.")
            return "error"
        tipo_expr = self.visit(ctx.asignacion().expr())
        if simbolo.tipo != tipo_expr and not (simbolo.tipo == "float" and tipo_expr == "int"):
            self.reportar_error(ctx, f"Tipo incorrecto para '{nombre}'. Se esperaba {simbolo.tipo} y se obtuvo {tipo_expr}.")
        return simbolo.tipo

    def visitInstrIf(self, ctx):
        tipo_cond = self.visit(ctx.condicion())
        if tipo_cond != "bool":
            self.reportar_error(ctx, "La condición del 'if' debe ser booleana.")
        return self.visitChildren(ctx)

    def visitInstrWhile(self, ctx):
        tipo_cond = self.visit(ctx.condicion())
        if tipo_cond != "bool":
            self.reportar_error(ctx, "La condición del 'while' debe ser booleana.")
        return self.visit(ctx.bloque())

    def visitInstrPrint(self, ctx):
        return self.visit(ctx.expr())

    def visitAritmetica(self, ctx):
        izq = self.visit(ctx.expr(0))
        der = self.visit(ctx.expr(1))
        if izq in ["string", "bool"] or der in ["string", "bool"]:
            self.reportar_error(ctx, f"Operación aritmética no válida entre {izq} y {der}.")
            return "error"
        return "float" if izq == "float" or der == "float" else "int"

    def visitRelacional(self, ctx):
        self.visit(ctx.expr(0))
        self.visit(ctx.expr(1))
        return "bool"

    def visitLogica(self, ctx):
        izq = self.visit(ctx.condicion(0))
        der = self.visit(ctx.condicion(1))
        if izq != "bool" or der != "bool":
            self.reportar_error(ctx, "Operadores lógicos requieren operandos booleanos.")
        return "bool"

    def visitNumero(self, ctx):
        return "float" if "." in ctx.NUMERO().getText() else "int"

    def visitCadena(self, ctx):
        return "string"

    def visitVariable(self, ctx):
        nombre = ctx.ID().getText()
        simbolo = self.tabla_simbolos.obtener(nombre)
        if not simbolo:
            self.reportar_error(ctx, f"Variable '{nombre}' no declarada.")
            return "error"
        return simbolo.tipo

    # --- CORRECCIÓN PARA FUNCIONES ---
    def visitInstrFuncDecl(self, ctx):
        nombre_func = ctx.funcion_decl().ID().getText()
        tipo_retorno = ctx.funcion_decl().getChild(0).getText()
        
        # Registrar la función en el ámbito actual
        self.tabla_simbolos.declarar(nombre_func, "function", valor=tipo_retorno)

        # Entrar al scope de la función y registrar parámetros
        self.tabla_simbolos.push_scope()
        if ctx.funcion_decl().parametros():
            params = ctx.funcion_decl().parametros()
            for i in range(len(params.ID())):
                self.tabla_simbolos.declarar(params.ID(i).getText(), params.TIPO(i).getText())
        
        self.visit(ctx.funcion_decl().bloque())
        self.tabla_simbolos.pop_scope()
        return tipo_retorno

    def visitLlamadaExpr(self, ctx):
        return self.visit(ctx.llamada_func())

    def visitLlamada_func(self, ctx):
        nombre = ctx.ID().getText()
        simbolo = self.tabla_simbolos.obtener(nombre)
        if not simbolo:
            self.reportar_error(ctx, f"Función '{nombre}' no definida.")
            return "error"
        return simbolo.valor # Retorna el tipo de retorno guardado

    def visitParentesisExpr(self, ctx): return self.visit(ctx.expr())
    def visitParentesisCond(self, ctx): return self.visit(ctx.condicion())