

from ExpresionesVisitor import ExpresionesVisitor
from ExpresionesParser import ExpresionesParser


class TACGenerator(ExpresionesVisitor):
    def __init__(self):
        self.instructions = []   # Lista de instrucciones TAC generadas
        self.temp_count = 0      # Contador de temporales (t1, t2, ...)
        self.label_count = 0     # Contador de etiquetas (L1, L2, ...)
        self.loop_stack = []     # Pila para break/continue: (label_break, label_continue)

    # ─── Helpers ────────────────────────────────────────────────────────────────

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, instruction):
        self.instructions.append(instruction)

    def get_code(self):
        return "\n".join(self.instructions)

    def write_to_file(self, filename="output.tac"):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.get_code())
        return filename

    # ─── Raíz ────────────────────────────────────────────────────────────────────

    def visitProg(self, ctx):
        self.emit("# === TAC Generado ===")
        for child in ctx.instrucciones():
            self.visit(child)
        return None

    def visitInstrImport(self, ctx):
        module_name = ctx.ID().getText()
        self.emit(f"# import {module_name}")
        return None

    # ─── Instrucciones ───────────────────────────────────────────────────────────

    def visitInstrDecl(self, ctx):
        return self.visit(ctx.declaracion())

    def visitInstrDeclArray(self, ctx):
        return self.visit(ctx.declaracionArray())

    def visitInstrAsig(self, ctx):
        return self.visit(ctx.asignacion())

    def visitInstrAsigArray(self, ctx):
        return self.visit(ctx.asignacionArray())

    def visitInstrPrint(self, ctx):
        val = self.visit(ctx.expr())
        self.emit(f"print {val}")
        return None

    def visitInstrReturn(self, ctx):
        if ctx.expr():
            val = self.visit(ctx.expr())
            self.emit(f"return {val}")
        else:
            self.emit("return")
        return None

    def visitInstrLlamada(self, ctx):
        self.visit(ctx.llamada_func())
        return None

    def visitInstrFuncDecl(self, ctx):
        return self.visit(ctx.funcion_decl())

    def visitInstrBreak(self, ctx):
        if self.loop_stack:
            label_break, _ = self.loop_stack[-1]
            self.emit(f"goto {label_break}")
        return None

    def visitInstrContinue(self, ctx):
        if self.loop_stack:
            _, label_continue = self.loop_stack[-1]
            self.emit(f"goto {label_continue}")
        return None

    # ─── Declaraciones ───────────────────────────────────────────────────────────

    def visitDeclaracion(self, ctx):
        var_name = ctx.ID().getText()
        if ctx.expr():
            val = self.visit(ctx.expr())
            self.emit(f"{var_name} = {val}")
        return None

    def visitDeclaracionArray(self, ctx):
        arr_name = ctx.ID().getText()
        elements = []
        if ctx.argumentos():
            for expr_ctx in ctx.argumentos().expr():
                val = self.visit(expr_ctx)
                elements.append(val)
        # Emitir inicialización del array elemento a elemento
        self.emit(f"# array {arr_name}[{len(elements)}]")
        for i, elem in enumerate(elements):
            self.emit(f"{arr_name}[{i}] = {elem}")
        return None

    # ─── Asignaciones ────────────────────────────────────────────────────────────

    def visitAsignacion(self, ctx):
        var_name = ctx.ID().getText()
        val = self.visit(ctx.expr())
        self.emit(f"{var_name} = {val}")
        return None

    def visitAsignacionArray(self, ctx):
        arr_name = ctx.ID().getText()
        idx = self.visit(ctx.expr(0))
        val = self.visit(ctx.expr(1))
        self.emit(f"{arr_name}[{idx}] = {val}")
        return None

    # ─── Bloque ──────────────────────────────────────────────────────────────────

    def visitBloque(self, ctx):
        for instr in ctx.instrucciones():
            self.visit(instr)
        return None

    # ─── If / Else ───────────────────────────────────────────────────────────────

    def visitInstrIf(self, ctx):
        label_true = self.new_label()
        label_end = self.new_label()

        has_else = ctx.SINO() is not None

        if has_else:
            label_false = self.new_label()
            self._emit_condition(ctx.condicion(), label_true, label_false)
        else:
            self._emit_condition(ctx.condicion(), label_true, label_end)

        # Bloque THEN
        self.emit(f"{label_true}:")
        self.visit(ctx.bloque(0))

        if has_else:
            self.emit(f"goto {label_end}")
            self.emit(f"{label_false}:")
            self.visit(ctx.bloque(1))

        self.emit(f"{label_end}:")
        return None

    def _emit_condition(self, cond_ctx, label_true, label_false):
        """Genera saltos condicionales para una condición."""
        if isinstance(cond_ctx, ExpresionesParser.RelacionalContext):
            left = self.visit(cond_ctx.expr(0))
            right = self.visit(cond_ctx.expr(1))
            op = cond_ctx.op.text
            self.emit(f"if {left} {op} {right} goto {label_true}")
            self.emit(f"goto {label_false}")

        elif isinstance(cond_ctx, ExpresionesParser.LogicaContext):
            if cond_ctx.O_LOGICO():
                # OR: si alguna es verdadera, ir al bloque true
                mid = self.new_label()
                self._emit_condition(cond_ctx.condicion(0), label_true, mid)
                self.emit(f"{mid}:")
                self._emit_condition(cond_ctx.condicion(1), label_true, label_false)
            else:
                # AND: ambas deben ser verdaderas
                mid = self.new_label()
                self._emit_condition(cond_ctx.condicion(0), mid, label_false)
                self.emit(f"{mid}:")
                self._emit_condition(cond_ctx.condicion(1), label_true, label_false)

        elif isinstance(cond_ctx, ExpresionesParser.NotLogicaContext):
            # NOT: invertir etiquetas
            self._emit_condition(cond_ctx.condicion(), label_false, label_true)

        elif isinstance(cond_ctx, ExpresionesParser.ParentesisCondContext):
            self._emit_condition(cond_ctx.condicion(), label_true, label_false)

    # ─── While ───────────────────────────────────────────────────────────────────

    def visitInstrWhile(self, ctx):
        label_check = self.new_label()   # inicio de condición
        label_body = self.new_label()    # cuerpo del loop
        label_end = self.new_label()     # salida del loop

        self.loop_stack.append((label_end, label_check))

        self.emit(f"{label_check}:")
        self._emit_condition(ctx.condicion(), label_body, label_end)
        self.emit(f"{label_body}:")
        self.visit(ctx.bloque())
        self.emit(f"goto {label_check}")
        self.emit(f"{label_end}:")

        self.loop_stack.pop()
        return None

    # ─── For ─────────────────────────────────────────────────────────────────────

    def visitInstrFor(self, ctx):
        label_check = self.new_label()
        label_body = self.new_label()
        label_update = self.new_label()
        label_end = self.new_label()

        self.loop_stack.append((label_end, label_update))

        # Init
        self.visit(ctx.asignacion(0))
        self.emit(f"{label_check}:")
        self._emit_condition(ctx.condicion(), label_body, label_end)
        self.emit(f"{label_body}:")
        self.visit(ctx.bloque())
        self.emit(f"{label_update}:")
        self.visit(ctx.asignacion(1))
        self.emit(f"goto {label_check}")
        self.emit(f"{label_end}:")

        self.loop_stack.pop()
        return None

    # ─── Funciones ───────────────────────────────────────────────────────────────

    def visitFuncion_decl(self, ctx):
        func_name = ctx.ID().getText()
        self.emit(f"begin_func {func_name}")

        # Emitir parámetros
        if ctx.parametros():
            for i in range(len(ctx.parametros().ID())):
                param_name = ctx.parametros().ID(i).getText()
                self.emit(f"param {param_name}")

        self.visit(ctx.bloque())
        self.emit(f"end_func {func_name}")
        return None

    def visitLlamada_func(self, ctx):
        func_name = ctx.ID().getText()
        args = []
        if ctx.argumentos():
            for expr_ctx in ctx.argumentos().expr():
                val = self.visit(expr_ctx)
                args.append(val)

        for arg in args:
            self.emit(f"arg {arg}")

        temp = self.new_temp()
        arg_count = len(args)
        self.emit(f"{temp} = call {func_name}, {arg_count}")
        return temp

    # ─── Expresiones ─────────────────────────────────────────────────────────────

    def visitAritmetica(self, ctx):
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))

        # Determinar operador
        if ctx.MULT():
            op = "*"
        elif ctx.DIV():
            op = "/"
        elif ctx.MOD():
            op = "%"
        elif ctx.SUMA():
            op = "+"
        else:
            op = "-"

        temp = self.new_temp()
        self.emit(f"{temp} = {left} {op} {right}")
        return temp

    def visitAccesoArray(self, ctx):
        arr_name = ctx.ID().getText()
        idx = self.visit(ctx.expr())
        temp = self.new_temp()
        self.emit(f"{temp} = {arr_name}[{idx}]")
        return temp

    def visitNumero(self, ctx):
        return ctx.NUMERO().getText()

    def visitCadena(self, ctx):
        return ctx.STRING().getText()

    def visitVariable(self, ctx):
        return ctx.ID().getText()

    def visitLlamadaExpr(self, ctx):
        return self.visit(ctx.llamada_func())

    def visitParentesisExpr(self, ctx):
        return self.visit(ctx.expr())
