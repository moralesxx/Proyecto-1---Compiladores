from llvmlite import ir
from llvmlite import binding as llvm
from ExpresionesVisitor import ExpresionesVisitor
from ExpresionesParser import ExpresionesParser


# ─── Tipos LLVM ──────────────────────────────────────────────────────────────

INT_TYPE   = ir.IntType(32)
FLOAT_TYPE = ir.DoubleType()
BOOL_TYPE  = ir.IntType(1)
VOID_TYPE  = ir.VoidType()
STR_TYPE   = ir.IntType(8).as_pointer()   # char*


def llvm_type_from_str(tipo_str):
    mapping = {
        "int":    INT_TYPE,
        "float":  FLOAT_TYPE,
        "bool":   BOOL_TYPE,
        "string": STR_TYPE,
        "void":   VOID_TYPE,
    }
    return mapping.get(tipo_str, INT_TYPE)


class IRGenerator(ExpresionesVisitor):
    def __init__(self):
        # ── FIX: initialize() está deprecated en versiones nuevas de llvmlite.
        # Solo llamamos initialize_native_target y initialize_native_asmprinter
        # de forma segura, ignorando el warning si ya fueron llamados antes.
        try:
            llvm.initialize_native_target()
            llvm.initialize_native_asmprinter()
        except Exception:
            pass  # Ya fueron inicializados en una llamada previa, no es error

        self.module = ir.Module(name="compilador_module")

        # Obtener triple de forma segura
        try:
            self.module.triple = llvm.get_default_triple()
        except Exception:
            pass  # Si falla, llvmlite usa un triple por defecto

        self.builder      = None   # ir.IRBuilder activo
        self.func         = None   # Función LLVM actual
        self.symbol_table = [{}]   # Pila de scopes: lista de dicts {name: alloca}
        self.func_table   = {}     # {nombre: ir.Function}
        self.str_counter  = 0      # Contador de strings / formatos globales
        self.loop_stack   = []     # Pila: (block_break, block_continue)

        # Declarar printf externo para print
        self._declare_printf()

    # ─── printf externo ──────────────────────────────────────────────────────

    def _declare_printf(self):
        printf_ty = ir.FunctionType(INT_TYPE, [STR_TYPE], var_arg=True)
        self.printf = ir.Function(self.module, printf_ty, name="printf")

    def _get_format_str(self, fmt_str):
        """Crea una constante global para un string de formato."""
        fmt_bytes = (fmt_str + "\0").encode("utf8")
        fmt_type  = ir.ArrayType(ir.IntType(8), len(fmt_bytes))
        global_fmt = ir.GlobalVariable(
            self.module, fmt_type, name=f".fmt.{self.str_counter}"
        )
        self.str_counter += 1
        global_fmt.global_constant = True
        global_fmt.initializer = ir.Constant(fmt_type, bytearray(fmt_bytes))
        zero = ir.Constant(INT_TYPE, 0)
        return self.builder.gep(global_fmt, [zero, zero], inbounds=True)

    def _emit_print(self, value, ir_type):
        """Emite una llamada a printf según el tipo del valor."""
        if ir_type == INT_TYPE or ir_type == BOOL_TYPE:
            fmt_ptr = self._get_format_str("%d\n")
            val = value
            if ir_type == BOOL_TYPE:
                val = self.builder.zext(value, INT_TYPE)
            self.builder.call(self.printf, [fmt_ptr, val])
        elif ir_type == FLOAT_TYPE:
            fmt_ptr = self._get_format_str("%f\n")
            self.builder.call(self.printf, [fmt_ptr, value])
        elif ir_type == STR_TYPE:
            fmt_ptr = self._get_format_str("%s\n")
            self.builder.call(self.printf, [fmt_ptr, value])

    # ─── Scope helpers ───────────────────────────────────────────────────────

    def push_scope(self):
        self.symbol_table.append({})

    def pop_scope(self):
        self.symbol_table.pop()

    def declare_var(self, name, alloca):
        self.symbol_table[-1][name] = alloca

    def lookup_var(self, name):
        for scope in reversed(self.symbol_table):
            if name in scope:
                return scope[name]
        raise NameError(f"Variable '{name}' no encontrada en scope.")

    # ─── Obtener IR como string ───────────────────────────────────────────────

    def get_ir(self):
        return str(self.module)

    def write_to_file(self, filename="output.ll"):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.get_ir())
        return filename

    # ─── Raíz ────────────────────────────────────────────────────────────────

    def visitProg(self, ctx):
        # Crear función main() : i32
        main_type = ir.FunctionType(INT_TYPE, [])
        main_func = ir.Function(self.module, main_type, name="main")
        self.func = main_func
        self.func_table["main"] = main_func

        entry_block = main_func.append_basic_block("entry")
        self.builder = ir.IRBuilder(entry_block)

        self.push_scope()

        for instr in ctx.instrucciones():
            if not self.builder.block.is_terminated:
                self.visit(instr)

        self.pop_scope()

        if not self.builder.block.is_terminated:
            self.builder.ret(ir.Constant(INT_TYPE, 0))

        return self.module

    def visitInstrImport(self, ctx):
        return None

    # ─── Instrucciones ───────────────────────────────────────────────────────

    def visitInstrDecl(self, ctx):
        return self.visit(ctx.declaracion())

    def visitInstrDeclArray(self, ctx):
        return self.visit(ctx.declaracionArray())

    def visitInstrAsig(self, ctx):
        return self.visit(ctx.asignacion())

    def visitInstrAsigArray(self, ctx):
        return self.visit(ctx.asignacionArray())

    def visitInstrPrint(self, ctx):
        val, ty = self.visit(ctx.expr())
        self._emit_print(val, ty)
        return None

    def visitInstrReturn(self, ctx):
        if ctx.expr():
            val, ty = self.visit(ctx.expr())
            ret_type = self.func.return_value.type
            if ret_type == INT_TYPE and ty == FLOAT_TYPE:
                val = self.builder.fptosi(val, INT_TYPE)
            elif ret_type == FLOAT_TYPE and ty == INT_TYPE:
                val = self.builder.sitofp(val, FLOAT_TYPE)
            self.builder.ret(val)
        else:
            self.builder.ret_void()
        return None

    def visitInstrLlamada(self, ctx):
        self.visit(ctx.llamada_func())
        return None

    def visitInstrFuncDecl(self, ctx):
        return self.visit(ctx.funcion_decl())

    def visitInstrBreak(self, ctx):
        if self.loop_stack:
            block_break, _ = self.loop_stack[-1]
            self.builder.branch(block_break)
        return None

    def visitInstrContinue(self, ctx):
        if self.loop_stack:
            _, block_continue = self.loop_stack[-1]
            self.builder.branch(block_continue)
        return None

    # ─── Declaraciones ───────────────────────────────────────────────────────

    def visitDeclaracion(self, ctx):
        tipo_str = ctx.TIPO().getText()
        var_name = ctx.ID().getText()
        llvm_t   = llvm_type_from_str(tipo_str)

        alloca = self.builder.alloca(llvm_t, name=var_name)

        if ctx.expr():
            val, val_ty = self.visit(ctx.expr())
            val = self._coerce(val, val_ty, llvm_t)
            self.builder.store(val, alloca)
        else:
            if llvm_t == FLOAT_TYPE:
                self.builder.store(ir.Constant(FLOAT_TYPE, 0.0), alloca)
            elif llvm_t == STR_TYPE:
                null = ir.Constant(STR_TYPE, None)
                self.builder.store(null, alloca)
            else:
                self.builder.store(ir.Constant(llvm_t, 0), alloca)

        self.declare_var(var_name, (alloca, llvm_t))
        return None

    def visitDeclaracionArray(self, ctx):
        tipo_str  = ctx.TIPO().getText()
        arr_name  = ctx.ID().getText()
        elem_type = llvm_type_from_str(tipo_str)

        elements = []
        if ctx.argumentos():
            for expr_ctx in ctx.argumentos().expr():
                val, ty = self.visit(expr_ctx)
                val = self._coerce(val, ty, elem_type)
                elements.append(val)

        arr_type = ir.ArrayType(elem_type, len(elements))
        alloca   = self.builder.alloca(arr_type, name=arr_name)

        for i, elem in enumerate(elements):
            zero = ir.Constant(INT_TYPE, 0)
            idx  = ir.Constant(INT_TYPE, i)
            ptr  = self.builder.gep(alloca, [zero, idx], inbounds=True)
            self.builder.store(elem, ptr)

        self.declare_var(arr_name, (alloca, arr_type))
        return None

    # ─── Asignaciones ────────────────────────────────────────────────────────

    def visitAsignacion(self, ctx):
        var_name         = ctx.ID().getText()
        alloca, llvm_t   = self.lookup_var(var_name)
        val, val_ty      = self.visit(ctx.expr())
        val = self._coerce(val, val_ty, llvm_t)
        self.builder.store(val, alloca)
        return None

    def visitAsignacionArray(self, ctx):
        arr_name         = ctx.ID().getText()
        alloca, arr_type = self.lookup_var(arr_name)
        idx_val, _       = self.visit(ctx.expr(0))
        val, val_ty      = self.visit(ctx.expr(1))

        elem_type = arr_type.element
        val = self._coerce(val, val_ty, elem_type)

        zero = ir.Constant(INT_TYPE, 0)
        ptr  = self.builder.gep(alloca, [zero, idx_val], inbounds=True)
        self.builder.store(val, ptr)
        return None

    # ─── Bloque ──────────────────────────────────────────────────────────────

    def visitBloque(self, ctx):
        self.push_scope()
        for instr in ctx.instrucciones():
            if not self.builder.block.is_terminated:
                self.visit(instr)
        self.pop_scope()
        return None

    # ─── If / Else ───────────────────────────────────────────────────────────

    def visitInstrIf(self, ctx):
        cond_val = self._eval_condition(ctx.condicion())
        has_else = ctx.SINO() is not None

        then_block = self.func.append_basic_block("if.then")
        else_block = self.func.append_basic_block("if.else") if has_else else None
        end_block  = self.func.append_basic_block("if.end")

        if has_else:
            self.builder.cbranch(cond_val, then_block, else_block)
        else:
            self.builder.cbranch(cond_val, then_block, end_block)

        self.builder.position_at_end(then_block)
        self.visit(ctx.bloque(0))
        if not self.builder.block.is_terminated:
            self.builder.branch(end_block)

        if has_else:
            self.builder.position_at_end(else_block)
            self.visit(ctx.bloque(1))
            if not self.builder.block.is_terminated:
                self.builder.branch(end_block)

        self.builder.position_at_end(end_block)
        return None

    # ─── While ───────────────────────────────────────────────────────────────

    def visitInstrWhile(self, ctx):
        check_block = self.func.append_basic_block("while.check")
        body_block  = self.func.append_basic_block("while.body")
        end_block   = self.func.append_basic_block("while.end")

        self.loop_stack.append((end_block, check_block))

        self.builder.branch(check_block)
        self.builder.position_at_end(check_block)
        cond_val = self._eval_condition(ctx.condicion())
        self.builder.cbranch(cond_val, body_block, end_block)

        self.builder.position_at_end(body_block)
        self.visit(ctx.bloque())
        if not self.builder.block.is_terminated:
            self.builder.branch(check_block)

        self.builder.position_at_end(end_block)
        self.loop_stack.pop()
        return None

    # ─── For ─────────────────────────────────────────────────────────────────

    def visitInstrFor(self, ctx):
        self.visit(ctx.asignacion(0))

        check_block  = self.func.append_basic_block("for.check")
        body_block   = self.func.append_basic_block("for.body")
        update_block = self.func.append_basic_block("for.update")
        end_block    = self.func.append_basic_block("for.end")

        self.loop_stack.append((end_block, update_block))

        self.builder.branch(check_block)
        self.builder.position_at_end(check_block)
        cond_val = self._eval_condition(ctx.condicion())
        self.builder.cbranch(cond_val, body_block, end_block)

        self.builder.position_at_end(body_block)
        self.visit(ctx.bloque())
        if not self.builder.block.is_terminated:
            self.builder.branch(update_block)

        self.builder.position_at_end(update_block)
        self.visit(ctx.asignacion(1))
        if not self.builder.block.is_terminated:
            self.builder.branch(check_block)

        self.builder.position_at_end(end_block)
        self.loop_stack.pop()
        return None

    # ─── Funciones ───────────────────────────────────────────────────────────

    def visitFuncion_decl(self, ctx):
        ret_type_str = ctx.getChild(0).getText()
        ret_type     = llvm_type_from_str(ret_type_str)
        func_name    = ctx.ID().getText()

        param_types = []
        param_names = []
        if ctx.parametros():
            for i in range(len(ctx.parametros().ID())):
                p_type_str = ctx.parametros().TIPO(i).getText()
                p_name     = ctx.parametros().ID(i).getText()
                param_types.append(llvm_type_from_str(p_type_str))
                param_names.append(p_name)

        func_type = ir.FunctionType(ret_type, param_types)
        func      = ir.Function(self.module, func_type, name=func_name)
        self.func_table[func_name] = func

        prev_func    = self.func
        prev_builder = self.builder

        self.func  = func
        entry      = func.append_basic_block("entry")
        self.builder = ir.IRBuilder(entry)

        self.push_scope()
        for arg, name, ty in zip(func.args, param_names, param_types):
            arg.name = name
            alloca   = self.builder.alloca(ty, name=name)
            self.builder.store(arg, alloca)
            self.declare_var(name, (alloca, ty))

        self.visit(ctx.bloque())

        if not self.builder.block.is_terminated:
            if ret_type == VOID_TYPE:
                self.builder.ret_void()
            else:
                self.builder.ret(ir.Constant(ret_type, 0))

        self.pop_scope()

        self.func    = prev_func
        self.builder = prev_builder
        return None

    def visitLlamada_func(self, ctx):
        func_name = ctx.ID().getText()
        args_ir   = []
        if ctx.argumentos():
            for expr_ctx in ctx.argumentos().expr():
                val, ty = self.visit(expr_ctx)
                args_ir.append(val)

        if func_name not in self.func_table:
            raise NameError(f"Función '{func_name}' no declarada.")

        func   = self.func_table[func_name]
        result = self.builder.call(func, args_ir)
        ret_type = func.return_value.type
        return result, ret_type

    # ─── Condiciones → i1 ────────────────────────────────────────────────────

    def _eval_condition(self, cond_ctx):
        if isinstance(cond_ctx, ExpresionesParser.RelacionalContext):
            left, l_ty  = self.visit(cond_ctx.expr(0))
            right, r_ty = self.visit(cond_ctx.expr(1))
            op = cond_ctx.op.text

            if l_ty == FLOAT_TYPE or r_ty == FLOAT_TYPE:
                if l_ty != FLOAT_TYPE:
                    left  = self.builder.sitofp(left,  FLOAT_TYPE)
                if r_ty != FLOAT_TYPE:
                    right = self.builder.sitofp(right, FLOAT_TYPE)
                fcmp_map = {
                    ">": "ogt", "<": "olt", "==": "oeq",
                    "!=": "one", "<>": "one", ">=": "oge", "<=": "ole"
                }
                return self.builder.fcmp_ordered(fcmp_map[op], left, right)
            else:
                icmp_map = {
                    ">": ">", "<": "<", "==": "==",
                    "!=": "!=", "<>": "!=", ">=": ">=", "<=": "<="
                }
                return self.builder.icmp_signed(icmp_map[op], left, right)

        elif isinstance(cond_ctx, ExpresionesParser.LogicaContext):
            left_cond  = self._eval_condition(cond_ctx.condicion(0))
            right_cond = self._eval_condition(cond_ctx.condicion(1))
            if cond_ctx.O_LOGICO():
                return self.builder.or_(left_cond, right_cond)
            else:
                return self.builder.and_(left_cond, right_cond)

        elif isinstance(cond_ctx, ExpresionesParser.NotLogicaContext):
            val = self._eval_condition(cond_ctx.condicion())
            return self.builder.not_(val)

        elif isinstance(cond_ctx, ExpresionesParser.ParentesisCondContext):
            return self._eval_condition(cond_ctx.condicion())

        raise ValueError(f"Condición no soportada: {type(cond_ctx)}")

    # ─── Expresiones → (ir_value, ir_type) ───────────────────────────────────

    def visitAritmetica(self, ctx):
        left,  l_ty = self.visit(ctx.expr(0))
        right, r_ty = self.visit(ctx.expr(1))

        use_float = (l_ty == FLOAT_TYPE or r_ty == FLOAT_TYPE)
        if use_float:
            if l_ty != FLOAT_TYPE:
                left  = self.builder.sitofp(left,  FLOAT_TYPE)
            if r_ty != FLOAT_TYPE:
                right = self.builder.sitofp(right, FLOAT_TYPE)

        if ctx.MULT():
            result = self.builder.fmul(left, right) if use_float else self.builder.mul(left, right)
        elif ctx.DIV():
            result = self.builder.fdiv(left, right) if use_float else self.builder.sdiv(left, right)
        elif ctx.MOD():
            result = self.builder.frem(left, right) if use_float else self.builder.srem(left, right)
        elif ctx.SUMA():
            result = self.builder.fadd(left, right) if use_float else self.builder.add(left, right)
        else:  # RESTA
            result = self.builder.fsub(left, right) if use_float else self.builder.sub(left, right)

        return result, (FLOAT_TYPE if use_float else INT_TYPE)

    def visitAccesoArray(self, ctx):
        arr_name         = ctx.ID().getText()
        alloca, arr_type = self.lookup_var(arr_name)
        idx_val, _       = self.visit(ctx.expr())

        zero     = ir.Constant(INT_TYPE, 0)
        ptr      = self.builder.gep(alloca, [zero, idx_val], inbounds=True)
        elem_type = arr_type.element
        val      = self.builder.load(ptr)
        return val, elem_type

    def visitNumero(self, ctx):
        num_str = ctx.NUMERO().getText()
        if "." in num_str:
            return ir.Constant(FLOAT_TYPE, float(num_str)), FLOAT_TYPE
        else:
            return ir.Constant(INT_TYPE, int(num_str)),    INT_TYPE

    def visitCadena(self, ctx):
        raw     = ctx.STRING().getText()[1:-1]
        encoded = (raw + "\0").encode("utf8")
        str_type = ir.ArrayType(ir.IntType(8), len(encoded))
        global_str = ir.GlobalVariable(
            self.module, str_type, name=f".str.{self.str_counter}"
        )
        self.str_counter += 1
        global_str.global_constant = True
        global_str.initializer = ir.Constant(str_type, bytearray(encoded))
        zero = ir.Constant(INT_TYPE, 0)
        ptr  = self.builder.gep(global_str, [zero, zero], inbounds=True)
        return ptr, STR_TYPE

    def visitVariable(self, ctx):
        var_name       = ctx.ID().getText()
        alloca, llvm_t = self.lookup_var(var_name)
        val            = self.builder.load(alloca)
        return val, llvm_t

    def visitLlamadaExpr(self, ctx):
        return self.visit(ctx.llamada_func())

    def visitParentesisExpr(self, ctx):
        return self.visit(ctx.expr())

    # ─── Coerción de tipos ────────────────────────────────────────────────────

    def _coerce(self, val, from_ty, to_ty):
        if from_ty == to_ty:
            return val
        if from_ty == INT_TYPE   and to_ty == FLOAT_TYPE:
            return self.builder.sitofp(val, FLOAT_TYPE)
        if from_ty == FLOAT_TYPE and to_ty == INT_TYPE:
            return self.builder.fptosi(val, INT_TYPE)
        if from_ty == BOOL_TYPE  and to_ty == INT_TYPE:
            return self.builder.zext(val, INT_TYPE)
        return val
