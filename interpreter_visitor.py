from ExpresionesVisitor import ExpresionesVisitor
from ExpresionesParser import ExpresionesParser
from symbol_table import SymbolTable


# ─── Excepciones de control de flujo ─────────────────────────────────────────

class BreakException(Exception):
    """Se lanza cuando se ejecuta un 'break' dentro de un ciclo."""
    pass

class ContinueException(Exception):
    """Se lanza cuando se ejecuta un 'continue' dentro de un ciclo."""
    pass

class ReturnException(Exception):
    """Se lanza cuando se ejecuta un 'return' dentro de una función."""
    def __init__(self, valor):
        self.valor = valor


# ─── Intérprete principal ─────────────────────────────────────────────────────

class InterpreterVisitor(ExpresionesVisitor):
    def __init__(self, tabla=None):
        self.tabla_simbolos = tabla if tabla else SymbolTable()
        self.funciones = {}  # Diccionario para guardar el cuerpo de las funciones

    # ─── Raíz ────────────────────────────────────────────────────────────────

    def visitProg(self, ctx):
        return self.visitChildren(ctx)

    # ─── Bloque ──────────────────────────────────────────────────────────────

    def visitBloque(self, ctx):
        self.tabla_simbolos.push_scope()
        result = None
        try:
            for instr in ctx.instrucciones():
                result = self.visit(instr)
        except (BreakException, ContinueException, ReturnException):
            self.tabla_simbolos.pop_scope()
            raise  # Propagar para que el ciclo/función lo maneje
        self.tabla_simbolos.pop_scope()
        return result

    # ─── Import (ignorado en ejecución) ──────────────────────────────────────

    def visitInstrImport(self, ctx):
        return None

    # ─── Print ───────────────────────────────────────────────────────────────

    def visitInstrPrint(self, ctx):
        valor = self.visit(ctx.expr())
        # Quitar comillas si es un string literal
        if isinstance(valor, str):
            if valor.startswith('"') and valor.endswith('"'):
                valor = valor[1:-1]
        print(valor)
        return None

    # ─── Declaración de variable simple ──────────────────────────────────────

    def visitInstrDecl(self, ctx):
        tipo = ctx.declaracion().TIPO().getText()
        nombre = ctx.declaracion().ID().getText()
        valor = self.visit(ctx.declaracion().expr()) if ctx.declaracion().ASIGNACION() else None
        self.tabla_simbolos.declarar(nombre, tipo, valor)
        return None

    # ─── Declaración de arreglo ───────────────────────────────────────────────

    def visitInstrDeclArray(self, ctx):
        arr_ctx = ctx.declaracionArray()
        nombre = arr_ctx.ID().getText()
        elementos = []
        if arr_ctx.argumentos():
            for expr_ctx in arr_ctx.argumentos().expr():
                elementos.append(self.visit(expr_ctx))
        self.tabla_simbolos.declarar(nombre, "array", elementos)
        return None

    # ─── Asignación de variable ───────────────────────────────────────────────

    def visitInstrAsig(self, ctx):
        nombre = ctx.asignacion().ID().getText()
        valor = self.visit(ctx.asignacion().expr())
        self.tabla_simbolos.asignar(nombre, valor)
        return valor

    # ─── Asignación a índice de arreglo ──────────────────────────────────────

    def visitInstrAsigArray(self, ctx):
        asig_ctx = ctx.asignacionArray()
        nombre = asig_ctx.ID().getText()
        indice = self.visit(asig_ctx.expr(0))
        valor = self.visit(asig_ctx.expr(1))
        simb = self.tabla_simbolos.obtener(nombre)
        if simb and isinstance(simb.valor, list):
            simb.valor[int(indice)] = valor
        return valor

    # ─── Acceso a elemento de arreglo ────────────────────────────────────────

    def visitAccesoArray(self, ctx):
        nombre = ctx.ID().getText()
        indice = self.visit(ctx.expr())
        simb = self.tabla_simbolos.obtener(nombre)
        if simb and isinstance(simb.valor, list):
            return simb.valor[int(indice)]
        return None

    # ─── If / Else ────────────────────────────────────────────────────────────

    def visitInstrIf(self, ctx):
        if self.visit(ctx.condicion()):
            return self.visit(ctx.bloque(0))
        elif ctx.bloque(1):
            return self.visit(ctx.bloque(1))
        return None

    # ─── While ───────────────────────────────────────────────────────────────

    def visitInstrWhile(self, ctx):
        while self.visit(ctx.condicion()):
            try:
                self.visit(ctx.bloque())
            except BreakException:
                break
            except ContinueException:
                continue
        return None

    # ─── For ─────────────────────────────────────────────────────────────────

    def visitInstrFor(self, ctx):
        # Inicialización
        self.visit(ctx.asignacion(0))
        # Condición + cuerpo + actualización
        while self.visit(ctx.condicion()):
            try:
                self.visit(ctx.bloque())
            except BreakException:
                break
            except ContinueException:
                pass  # Igual ejecuta la actualización
            # Actualización
            self.visit(ctx.asignacion(1))
        return None

    # ─── Break / Continue ─────────────────────────────────────────────────────

    def visitInstrBreak(self, ctx):
        raise BreakException()

    def visitInstrContinue(self, ctx):
        raise ContinueException()

    # ─── Declaración de función ───────────────────────────────────────────────

    def visitInstrFuncDecl(self, ctx):
        nombre = ctx.funcion_decl().ID().getText()
        self.funciones[nombre] = ctx.funcion_decl()  # Guardamos el nodo AST
        return None

    # ─── Return ───────────────────────────────────────────────────────────────

    def visitInstrReturn(self, ctx):
        valor = self.visit(ctx.expr()) if ctx.expr() else None
        raise ReturnException(valor)

    # ─── Llamada a función como instrucción ───────────────────────────────────

    def visitInstrLlamada(self, ctx):
        self.visit(ctx.llamada_func())
        return None

    # ─── Llamada a función como expresión ────────────────────────────────────

    def visitLlamadaExpr(self, ctx):
        return self.visit(ctx.llamada_func())

    # ─── Ejecutar función ─────────────────────────────────────────────────────

    def visitLlamada_func(self, ctx):
        nombre = ctx.ID().getText()
        func_ctx = self.funciones.get(nombre)

        if func_ctx is None:
            print(f"[Error] Función '{nombre}' no definida.")
            return None

        # Evaluar argumentos ANTES de entrar al nuevo scope
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

        resultado = None
        try:
            self._visit_bloque_func(func_ctx.bloque())
        except ReturnException as ret:
            resultado = ret.valor

        self.tabla_simbolos.pop_scope()
        return resultado

    def _visit_bloque_func(self, bloque_ctx):
        """Visita un bloque dentro de una función, propagando ReturnException."""
        self.tabla_simbolos.push_scope()
        try:
            for instr in bloque_ctx.instrucciones():
                self.visit(instr)
        except ReturnException:
            self.tabla_simbolos.pop_scope()
            raise
        self.tabla_simbolos.pop_scope()

    # ─── Expresiones aritméticas ──────────────────────────────────────────────

    def visitAritmetica(self, ctx):
        izq = self.visit(ctx.expr(0))
        der = self.visit(ctx.expr(1))
        op = ctx.getChild(1).getText()

        # Manejo de concatenación de strings con +
        if op == '+':
            if isinstance(izq, str) or isinstance(der, str):
                izq_s = izq[1:-1] if isinstance(izq, str) and izq.startswith('"') else str(izq)
                der_s = der[1:-1] if isinstance(der, str) and der.startswith('"') else str(der)
                return izq_s + der_s
            return izq + der
        if op == '-': return izq - der
        if op == '*': return izq * der
        if op == '/': return izq / der if der != 0 else 0
        if op == '%': return izq % der if der != 0 else 0
        return None

    # ─── Expresiones relacionales ─────────────────────────────────────────────

    def visitRelacional(self, ctx):
        izq = self.visit(ctx.expr(0))
        der = self.visit(ctx.expr(1))
        op = ctx.op.text
        if op == '>':  return izq > der
        if op == '<':  return izq < der
        if op == '<=': return izq <= der
        if op == '>=': return izq >= der
        if op == '==': return izq == der
        if op == '!=' or op == '<>': return izq != der
        return False

    # ─── Condiciones lógicas ──────────────────────────────────────────────────

    def visitLogica(self, ctx):
        if ctx.O_LOGICO():
            return self.visit(ctx.condicion(0)) or self.visit(ctx.condicion(1))
        else:  # Y_LOGICO
            return self.visit(ctx.condicion(0)) and self.visit(ctx.condicion(1))

    def visitNotLogica(self, ctx):
        return not self.visit(ctx.condicion())

    def visitParentesisCond(self, ctx):
        return self.visit(ctx.condicion())

    # ─── Literales y variables ────────────────────────────────────────────────

    def visitVariable(self, ctx):
        simb = self.tabla_simbolos.obtener(ctx.ID().getText())
        return simb.valor if simb else None

    def visitNumero(self, ctx):
        val = ctx.NUMERO().getText()
        return float(val) if '.' in val else int(val)

    def visitCadena(self, ctx):
        # Devuelve el string sin comillas para uso interno
        raw = ctx.STRING().getText()
        return raw[1:-1]  # Quitar comillas dobles

    def visitParentesisExpr(self, ctx):
        return self.visit(ctx.expr())
