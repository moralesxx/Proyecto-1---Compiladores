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
            raise  # Propagar para que el bucle o función lo capture
        self.tabla_simbolos.pop_scope()
        return result

    # ─── Instrucciones ───────────────────────────────────────────────────────

    def visitInstrImport(self, ctx):
        return None

    def visitInstrDecl(self, ctx):
        return self.visit(ctx.declaracion())

    def visitInstrDeclArray(self, ctx):
        return self.visit(ctx.declaracionArray())

    def visitInstrAsig(self, ctx):
        return self.visit(ctx.asignacion())

    def visitInstrAsigArray(self, ctx):
        return self.visit(ctx.asignacionArray())

    def visitInstrIf(self, ctx):
        # CAMBIO INTERP: ctx.condicion() -> ctx.expr()
        condicion_verdadera = self.visit(ctx.expr())
        if condicion_verdadera:
            return self.visit(ctx.bloque(0))
        elif ctx.SINO() is not None:
            return self.visit(ctx.bloque(1))
        return None

    def visitInstrWhile(self, ctx):
        # CAMBIO INTERP: ctx.condicion() -> ctx.expr()
        while self.visit(ctx.expr()):
            try:
                self.visit(ctx.bloque())
            except BreakException:
                break
            except ContinueException:
                continue
        return None

    def visitInstrFor(self, ctx):
        # Ejecutar inicialización del ciclo (ej: i = 0)
        self.visit(ctx.asignacion(0))
        
        # CAMBIO INTERP: ctx.condicion() -> ctx.expr()
        while self.visit(ctx.expr()):
            try:
                self.visit(ctx.bloque())
            except BreakException:
                break
            except ContinueException:
                pass  # continua con la actualización de abajo
            
            # Ejecutar actualización del ciclo (ej: i = i + 1)
            self.visit(ctx.asignacion(1))
        return None

    def visitInstrBreak(self, ctx):
        raise BreakException()

    def visitInstrContinue(self, ctx):
        raise ContinueException()

    def visitInstrPrint(self, ctx):
        val = self.visit(ctx.expr())
        print(val)
        return None

    def visitInstrFuncDecl(self, ctx):
        return self.visit(ctx.funcion_decl())

    def visitInstrReturn(self, ctx):
        val = self.visit(ctx.expr()) if ctx.expr() else None
        raise ReturnException(val)

    def visitInstrLlamada(self, ctx):
        self.visit(ctx.llamada_func())
        return None

    # ─── Declaraciones y Asignaciones ──────────────────────────────────────────

    def visitDeclaracion(self, ctx):
        tipo = ctx.TIPO().getText()
        nombre = ctx.ID().getText()
        self.tabla_simbolos.declarar(nombre, tipo)
        if ctx.ASIGNACION():
            val = self.visit(ctx.expr())
            self.tabla_simbolos.asignar(nombre, val)
        return None

    def visitDeclaracionArray(self, ctx):
        tipo = ctx.TIPO().getText()
        nombre = ctx.ID().getText()
        valores = []
        if ctx.argumentos():
            for expr_ctx in ctx.argumentos().expr():
                valores.append(self.visit(expr_ctx))
        self.tabla_simbolos.declarar_array(nombre, tipo, valores)
        return None

    def visitAsignacion(self, ctx):
        nombre = ctx.ID().getText()
        val = self.visit(ctx.expr())
        self.tabla_simbolos.asignar(nombre, val)
        return None

    def visitAsignacionArray(self, ctx):
        nombre = ctx.ID().getText()
        idx = self.visit(ctx.expr(0))
        val = self.visit(ctx.expr(1))
        self.tabla_simbolos.asignar_array(nombre, idx, val)
        return None

    # ─── Estructura de Funciones ─────────────────────────────────────────────────

    def visitFuncion_decl(self, ctx):
        nombre_func = ctx.ID().getText()
        # Guardar la regla entera en memoria para ejecutarla dinámicamente al llamarla
        self.funciones[nombre_func] = ctx
        return None

    def visitLlamada_func(self, ctx):
        nombre_func = ctx.ID().getText()
        if nombre_func not in self.funciones:
            print(f"[Error de Ejecución] Función '{nombre_func}' no definida.")
            return None

        ctx_decl = self.funciones[nombre_func]
        
        # Evaluar argumentos en el contexto actual antes del cambio de ámbito
        valores_argumentos = []
        if ctx.argumentos():
            for expr_ctx in ctx.argumentos().expr():
                valores_argumentos.append(self.visit(expr_ctx))

        # Crear un nuevo ambiente limpio para ejecutar la función (Ámbito local)
        self.tabla_simbolos.push_scope()

        # Enlazar los valores calculados con las variables de los parámetros declarados
        if ctx_decl.parametros():
            for i, param_id in enumerate(ctx_decl.parametros().ID()):
                nombre_param = param_id.getText()
                tipo_param = ctx_decl.parametros().TIPO(i).getText()
                self.tabla_simbolos.declarar(nombre_param, tipo_param)
                self.tabla_simbolos.asignar(nombre_param, valores_argumentos[i])

        # Ejecutar el bloque de código de la función interceptando su retorno
        ret_val = None
        try:
            self.visit(ctx_decl.bloque())
        except ReturnException as e:
            ret_val = e.valor

        self.tabla_simbolos.pop_scope()
        return ret_val

    # ─── Operaciones de Expresiones ───────────────────────────────────────────────

    def visitAritmetica(self, ctx):
        izq = self.visit(ctx.expr(0))
        der = self.visit(ctx.expr(1))
        if ctx.MULT():  return izq * der
        if ctx.DIV():   return izq / der if isinstance(izq, float) or isinstance(der, float) else izq // der
        if ctx.MOD():   return izq % der
        if ctx.SUMA():  return izq + der
        if ctx.RESTA(): return izq - der
        return 0

    def visitRelacional(self, ctx):
        izq = self.visit(ctx.expr(0))
        der = self.visit(ctx.expr(1))
        op = ctx.op.text
        if op == ">":  return izq > der
        if op == "<":  return izq < der
        if op == "==": return izq == der
        if op == "!=" or op == "<>": return izq != der
        if op == ">=": return izq >= der
        if op == "<=": return izq <= der
        return False

    def visitLogica(self, ctx):
        # CAMBIO INTERP: ctx.condicion(idx) -> ctx.expr(idx)
        if ctx.O_LOGICO():
            return self.visit(ctx.expr(0)) or self.visit(ctx.expr(1))
        else:
            return self.visit(ctx.expr(0)) and self.visit(ctx.expr(1))

    def visitNotLogica(self, ctx):
        # CAMBIO INTERP: ctx.condicion() -> ctx.expr()
        return not self.visit(ctx.expr())

    def visitAccesoArray(self, ctx):
        nombre = ctx.ID().getText()
        idx = self.visit(ctx.expr())
        return self.tabla_simbolos.obtener_array(nombre, idx)

    def visitNumero(self, ctx):
        txt = ctx.NUMERO().getText()
        return float(txt) if "." in txt else int(txt)

    def visitCadena(self, ctx):
        # Eliminar las comillas circundantes del string literal
        return ctx.STRING().getText()[1:-1]

    def visitVariable(self, ctx):
        nombre = ctx.ID().getText()
        simbolo = self.tabla_simbolos.obtener(nombre)
        return simbolo.valor if simbolo else None

    def visitLlamadaExpr(self, ctx):
        return self.visit(ctx.llamada_func())

    def visitParentesisExpr(self, ctx):
        return self.visit(ctx.expr())

    # ═════════════════════════════════════════════════════════════════════════════
    # v4 — Nuevas características (agregadas sin modificar nada de lo anterior)
    # ═════════════════════════════════════════════════════════════════════════════

    # ─── v4: Operador Ternario ────────────────────────────────────────────────
    def visitTernario(self, ctx):
        # CAMBIO INTERP: La condición es expr(0), las ramas son expr(1) y expr(2)
        condicion = self.visit(ctx.expr(0))
        if condicion:
            return self.visit(ctx.expr(1))
        else:
            return self.visit(ctx.expr(2))

    # ─── v4: Casting Explícito ────────────────────────────────────────────────
    def visitCastingExpr(self, ctx):
        tipo_destino = ctx.TIPO().getText()
        val = self.visit(ctx.expr())

        if tipo_destino == "int":
            return int(val)
        if tipo_destino == "float":
            return float(val)
        if tipo_destino == "bool":
            return bool(val)
        if tipo_destino == "string":
            return str(val)
        return val

    # ─── v4: Structs ─────────────────────────────────────────────────────────
    def visitInstrStructDecl(self, ctx):
        return self.visit(ctx.struct_decl())

    def visitStruct_decl(self, ctx):
        # Estructura puramente sintáctica en ejecución, la definición la maneja la tabla
        return None

    def visitInstrStructAsig(self, ctx):
        return self.visit(ctx.struct_asig())

    def visitStruct_asig(self, ctx):
        nombre_var = ctx.ID(0).getText()
        campo      = ctx.ID(1).getText()
        valor      = self.visit(ctx.expr())

        ok, msg = self.tabla_simbolos.asignar_campo(nombre_var, campo, valor)
        if not ok:
            print(f"[Error] {msg}")
        return valor

    def visitAccesoCampo(self, ctx):
        nombre_var = ctx.ID(0).getText()
        campo      = ctx.ID(1).getText()
        return self.tabla_simbolos.obtener_campo(nombre_var, campo)

    # ─── v4: Switch / Case ────────────────────────────────────────────────────
    def visitInstrSwitch(self, ctx):
        return self.visit(ctx.switch_stmt())

    def visitSwitch_stmt(self, ctx):
        valor_expr = self.visit(ctx.expr())
        ejecutado  = False
        for case in ctx.case_clause():
            valor_case = self._visit_literal(case.literal_valor())
            if valor_expr == valor_case:
                try:
                    for instr in case.instrucciones():
                        self.visit(instr)
                except BreakException:
                    pass
                ejecutado = True
                break
        if not ejecutado and ctx.default_clause():
            try:
                for instr in ctx.default_clause().instrucciones():
                    self.visit(instr)
            except BreakException:
                pass
        return None

    def _visit_literal(self, ctx):
        if ctx.NUMERO():
            val = ctx.NUMERO().getText()
            return float(val) if '.' in val else int(val)
        if ctx.STRING():
            return ctx.STRING().getText()[1:-1]
        return None