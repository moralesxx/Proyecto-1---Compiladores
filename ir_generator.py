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
        try:
            llvm.initialize_native_target()
            llvm.initialize_native_asmprinter()
        except Exception:
            pass

        self.module = ir.Module(name="compilador_module")

        try:
            self.module.triple = llvm.get_default_triple()
        except Exception:
            pass

        self.builder      = None   
        self.func         = None   
        self.symbol_table = [{}]   
        self.func_table   = {}     
        self.str_counter  = 0      
        self.loop_stack   = []     

        self.struct_types  = {}    
        self.struct_fields = {}    

        self._declare_printf()

    # ─── printf externo ──────────────────────────────────────────────────────

    def _declare_printf(self):
        printf_ty = ir.FunctionType(INT_TYPE, [STR_TYPE], var_arg=True)
        self.printf = ir.Function(self.module, printf_ty, name="printf")

    def _get_format_str(self, fmt_str):
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
        # CAMBIO: ctx.condicion() -> ctx.expr()
        cond_val = self._eval_condition(ctx.expr())
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
        # CAMBIO: ctx.condicion() -> ctx.expr()
        cond_val = self._eval_condition(ctx.expr())
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
        # CAMBIO: ctx.condicion() -> ctx.expr()
        cond_val = self._eval_condition(ctx.expr())
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
            # CAMBIO: cond_ctx.condicion(idx) -> cond_ctx.expr(idx)
            left_cond  = self._eval_condition(cond_ctx.expr(0))
            right_cond = self._eval_condition(cond_ctx.expr(1))
            if cond_ctx.O_LOGICO():
                return self.builder.or_(left_cond, right_cond)
            else:
                return self.builder.and_(left_cond, right_cond)

        elif isinstance(cond_ctx, ExpresionesParser.NotLogicaContext):
            # CAMBIO: cond_ctx.condicion() -> cond_ctx.expr()
            val = self._eval_condition(cond_ctx.expr())
            return self.builder.not_(val)

        elif isinstance(cond_ctx, ExpresionesParser.ParentesisExprContext):
            # CAMBIO: ParentesisCondContext migró a ParentesisExprContext
            return self._eval_condition(cond_ctx.expr())

        else:
            # Fallback por si llega un nodo variable/literal booleano crudo de 'expr'
            val, ty = self.visit(cond_ctx)
            if ty == BOOL_TYPE:
                return val
            return self.builder.icmp_signed("!=", val, ir.Constant(ty, 0))

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

    # ═════════════════════════════════════════════════════════════════════════════
    # v4 — Nuevas características (agregadas sin modificar nada de lo anterior)
    # ═════════════════════════════════════════════════════════════════════════════

    # ─── v4: Operador Ternario ────────────────────────────────────────────────
    def visitTernario(self, ctx):
        # CAMBIO: La condición es expr(0), las ramas se evalúan en expr(1) y expr(2)
        cond_val = self._eval_condition(ctx.expr(0))

        true_block  = self.func.append_basic_block("ternary.true")
        false_block = self.func.append_basic_block("ternary.false")
        end_block   = self.func.append_basic_block("ternary.end")

        self.builder.cbranch(cond_val, true_block, false_block)

        # Rama verdadera
        self.builder.position_at_end(true_block)
        val_true, ty_true = self.visit(ctx.expr(1))
        true_exit = self.builder.block
        self.builder.branch(end_block)

        # Rama falsa
        self.builder.position_at_end(false_block)
        val_false, ty_false = self.visit(ctx.expr(2))
        false_exit = self.builder.block
        self.builder.branch(end_block)

        # Phi node en el bloque de unificación
        self.builder.position_at_end(end_block)

        result_type = ty_true
        if ty_true != ty_false:
            if FLOAT_TYPE in (ty_true, ty_false):
                result_type = FLOAT_TYPE

        phi = self.builder.phi(result_type, name="ternary.result")
        phi.add_incoming(self._coerce(val_true,  ty_true,  result_type), true_exit)
        phi.add_incoming(self._coerce(val_false, ty_false, result_type), false_exit)

        return phi, result_type

    # ─── v4: Casting Explícito ────────────────────────────────────────────────
    def visitCastingExpr(self, ctx):
        tipo_destino = ctx.TIPO().getText()
        val, from_ty = self.visit(ctx.expr())
        to_ty        = llvm_type_from_str(tipo_destino)

        if from_ty == to_ty:
            return val, to_ty
        if from_ty == INT_TYPE   and to_ty == FLOAT_TYPE:
            return self.builder.sitofp(val, FLOAT_TYPE), FLOAT_TYPE
        if from_ty == FLOAT_TYPE and to_ty == INT_TYPE:
            return self.builder.fptosi(val, INT_TYPE),   INT_TYPE
        if from_ty == BOOL_TYPE  and to_ty == INT_TYPE:
            return self.builder.zext(val, INT_TYPE),     INT_TYPE
        if from_ty == INT_TYPE   and to_ty == BOOL_TYPE:
            zero = ir.Constant(INT_TYPE, 0)
            return self.builder.icmp_signed("!=", val, zero), BOOL_TYPE
        if from_ty == FLOAT_TYPE and to_ty == BOOL_TYPE:
            zero = ir.Constant(FLOAT_TYPE, 0.0)
            return self.builder.fcmp_ordered("one", val, zero), BOOL_TYPE
        return val, from_ty

    # ─── v4: Structs ─────────────────────────────────────────────────────────
    def visitInstrStructDecl(self, ctx):
        return self.visit(ctx.struct_decl())

    def visitStruct_decl(self, ctx):
        nombre_tipo = ctx.ID().getText()
        campos = []
        for campo in ctx.campo_struct():
            t = campo.TIPO().getText()
            n = campo.ID().getText()
            campos.append((n, t))

        field_types = [llvm_type_from_str(t) for _, t in campos]
        struct_ir   = ir.LiteralStructType(field_types)

        self.struct_types[nombre_tipo]  = struct_ir
        self.struct_fields[nombre_tipo] = campos   
        return None

    def visitInstrStructAsig(self, ctx):
        return self.visit(ctx.struct_asig())

    def visitStruct_asig(self, ctx):
        nombre_var = ctx.ID(0).getText()
        campo      = ctx.ID(1).getText()
        val, val_ty = self.visit(ctx.expr())

        alloca, struct_ir = self.lookup_var(nombre_var)

        nombre_tipo = None
        for k, v in self.struct_types.items():
            if v == struct_ir:
                nombre_tipo = k
                break

        if nombre_tipo is None:
            return None

        campos = self.struct_fields[nombre_tipo]
        idx    = next((i for i, (n, _) in enumerate(campos) if n == campo), None)
        if idx is None:
            return None

        field_ty = llvm_type_from_str(campos[idx][1])
        val = self._coerce(val, val_ty, field_ty)

        zero    = ir.Constant(INT_TYPE, 0)
        idx_ir  = ir.Constant(INT_TYPE, idx)
        ptr     = self.builder.gep(alloca, [zero, idx_ir], inbounds=True)
        self.builder.store(val, ptr)
        return None

    def visitAccesoCampo(self, ctx):
        nombre_var = ctx.ID(0).getText()
        campo      = ctx.ID(1).getText()

        alloca, struct_ir = self.lookup_var(nombre_var)

        nombre_tipo = None
        for k, v in self.struct_types.items():
            if v == struct_ir:
                nombre_tipo = k
                break

        if nombre_tipo is None:
            return ir.Constant(INT_TYPE, 0), INT_TYPE

        campos = self.struct_fields[nombre_tipo]
        idx    = next((i for i, (n, _) in enumerate(campos) if n == campo), 0)
        field_ty = llvm_type_from_str(campos[idx][1])

        zero   = ir.Constant(INT_TYPE, 0)
        idx_ir = ir.Constant(INT_TYPE, idx)
        ptr    = self.builder.gep(alloca, [zero, idx_ir], inbounds=True)
        val    = self.builder.load(ptr)
        return val, field_ty

    # ─── v4: Switch / Case ────────────────────────────────────────────────────
    def visitInstrSwitch(self, ctx):
        return self.visit(ctx.switch_stmt())

    def visitSwitch_stmt(self, ctx):
        val_expr, val_ty = self.visit(ctx.expr())

        if val_ty == FLOAT_TYPE:
            val_expr = self.builder.fptosi(val_expr, INT_TYPE)
            val_ty   = INT_TYPE

        cases       = ctx.case_clause()
        has_default = ctx.default_clause() is not None
        end_block   = self.func.append_basic_block("switch.end")

        case_blocks    = [self.func.append_basic_block(f"switch.case.{i}")
                          for i in range(len(cases))]
        default_block  = (self.func.append_basic_block("switch.default")
                          if has_default else end_block)

        sw = self.builder.switch(val_expr, default_block)
        for i, case in enumerate(cases):
            case_val = self._literal_ir_value(case.literal_valor(), val_ty)
            sw.add_case(case_val, case_blocks[i])

        for i, case in enumerate(cases):
            self.builder.position_at_end(case_blocks[i])
            self.loop_stack.append((end_block, end_block))
            self.push_scope()
            for instr in case.instrucciones():
                if not self.builder.block.is_terminated:
                    self.visit(instr)
            self.pop_scope()
            self.loop_stack.pop()
            if not self.builder.block.is_terminated:
                self.builder.branch(end_block)

        if has_default:
            self.builder.position_at_end(default_block)
            self.loop_stack.append((end_block, end_block))
            self.push_scope()
            for instr in ctx.default_clause().instrucciones():
                if not self.builder.block.is_terminated:
                    self.visit(instr)
            self.pop_scope()
            self.loop_stack.pop()
            if not self.builder.block.is_terminated:
                self.builder.branch(end_block)

        self.builder.position_at_end(end_block)
        return None

    def _literal_ir_value(self, ctx, expected_type=INT_TYPE):
        if ctx.NUMERO():
            txt = ctx.NUMERO().getText()
            if "." in txt:
                val = ir.Constant(FLOAT_TYPE, float(txt))
                if expected_type == INT_TYPE:
                    return ir.Constant(INT_TYPE, int(float(txt)))
                return val
            return ir.Constant(INT_TYPE, int(txt))
        if ctx.STRING():
            return ir.Constant(INT_TYPE, 0)
        return ir.Constant(INT_TYPE, 0)

    def _try_declare_struct_instance(self, tipo_str, var_name):
        if tipo_str not in self.struct_types:
            return False
        struct_ir = self.struct_types[tipo_str]
        alloca    = self.builder.alloca(struct_ir, name=var_name)
        self.declare_var(var_name, (alloca, struct_ir))
        return True



    # Copiar y pegar dentro de ir_generator.py (Clase IRGenerator)
    def visitTernario(self, ctx):
        """
        Visita la expresión del operador ternario (cond ? expr_true : expr_false).
        Utiliza la instrucción nativa 'select' de LLVM para mantener el flujo SSA lineal.
        """
        # 1. Evaluar la condición
        cond = self.visit(ctx.expr(0))
        
        # Asegurar que la condición sea de tipo i1 (Booleano de LLVM)
        if cond.type != BOOL_TYPE:
            cond = self.builder.icmp_signed("!=", cond, ir.Constant(cond.type, 0))
            
        # 2. Evaluar ambas ramas de manera segura
        val_true = self.visit(ctx.expr(1))
        val_false = self.visit(ctx.expr(2))
        
        # 3. Unificar tipos en caso de promoción implícita (int a float) si fuera necesario
        if val_true.type == FLOAT_TYPE and val_false.type == INT_TYPE:
            val_false = self.builder.sitofp(val_false, FLOAT_TYPE)
        elif val_true.type == INT_TYPE and val_false.type == FLOAT_TYPE:
            val_true = self.builder.sitofp(val_true, FLOAT_TYPE)
            
        # 4. Emitir la instrucción select nativa de LLVM
        return self.builder.select(cond, val_true, val_false)


    # Copiar y pegar dentro de ir_generator.py (Clase IRGenerator)
    def visitCast(self, ctx):
        """
        Soporte de casting explícito de tipos (e.g., (int)mi_float o (float)mi_int).
        Genera instrucciones de conversión nativas reales de LLVM.
        """
        # Obtener el nombre del tipo destino (int, float, etc.)
        tipo_destino_str = ctx.TIPO().getText()
        
        # Visitar la expresión interna para obtener su registro virtual actual
        valor_original = self.visit(ctx.expr())
        
        # Conversión de Entero a Flotante (int -> float)
        if tipo_destino_str == "float" and valor_original.type == INT_TYPE:
            return self.builder.sitofp(valor_original, FLOAT_TYPE)
            
        # Conversión de Flotante a Entero (float -> int)
        elif tipo_destino_str == "int" and valor_original.type == FLOAT_TYPE:
            return self.builder.fptosi(valor_original, INT_TYPE)
            
        # Si ya coinciden los tipos, se retorna el valor intacto sin alterar nada
        return valor_original



    # Copiar y pegar dentro de ir_generator.py (Clase IRGenerator)
    def visitStruct_decl(self, ctx):
        """
        Registra la estructura como un tipo agregado estructurado nativo en LLVM.
        """
        nombre_struct = ctx.ID().getText()
        
        # Recopilar y mapear los tipos de los campos declarados
        campos_ctx = ctx.campo_struct()
        lista_tipos_llvm = []
        self.struct_fields_map = getattr(self, 'struct_fields_map', {})
        
        # Mapear nombres de campos a sus índices físicos relativos
        mapa_campos = {}
        for idx, campo in enumerate(campos_ctx):
            nombre_campo = campo.ID().getText()
            tipo_campo_str = campo.TIPO().getText()
            lista_tipos_llvm.append(llvm_type_from_str(tipo_campo_str))
            mapa_campos[nombre_campo] = idx
            
        # Guardar el mapa de índices físicos sin alterar el diccionario global
        self.struct_fields_map[nombre_struct] = mapa_campos
        
        # Crear e identificar el tipo estructurado en el contexto del módulo LLVM
        st_type = self.module.context.get_identified_type(f"struct.{nombre_struct}")
        st_type.set_body(*lista_tipos_llvm)
        
        # Registrar el tipo para que las Fases 7 y 8 lo reconozcan
        self.struct_types[nombre_struct] = st_type
        return None

    def visitAccesoCampo(self, ctx):
        """
        Calcula el desplazamiento exacto del campo usando la instrucción GEP (getelementptr)
        y extrae el valor mediante una instrucción de carga (load).
        """
        nombre_var = ctx.ID(0).getText()
        nombre_campo = ctx.ID(1).getText()
        
        # Buscar la dirección física del puntero de la variable en la tabla de símbolos
        ptr_instancia = self.lookup_symbol(nombre_var)
        
        # Extraer el nombre del tipo estructurado a partir del tipo del puntero de LLVM
        struct_type_llvm = ptr_instancia.type.element
        nombre_struct = struct_type_llvm.name.replace("struct.", "")
        
        # Obtener el índice físico secuencial del campo solicitado
        mapa_campos = self.struct_fields_map.get(nombre_struct, {})
        indice_campo = mapa_campos.get(nombre_campo, 0)
        
        # Calcular el puntero absoluto hacia el miembro del struct usando instrucciones GEP nativas
        ptr_campo = self.builder.gep(
            ptr_instancia, 
            [ir.Constant(INT_TYPE, 0), ir.Constant(INT_TYPE, indice_campo)],
            name=f"{nombre_var}.{nombre_campo}.ptr"
        )
        
        # Retornar la carga del valor almacenado en ese campo
        return self.builder.load(ptr_campo, name=f"{nombre_var}.{nombre_campo}")