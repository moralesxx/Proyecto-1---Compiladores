

import time
import subprocess
import sys
import os
import re

import antlr4
from antlr4 import CommonTokenStream, InputStream

from ExpresionesLexer import ExpresionesLexer
from ExpresionesParser import ExpresionesParser

# ── Importar visitors ────────────────────────────────────────────────────────
try:
    from semantic_visitor import SemanticVisitor
    SEMANTIC_OK = True
except ImportError:
    SEMANTIC_OK = False

try:
    from tac_generator import TACGenerator
    TAC_OK = True
except ImportError:
    TAC_OK = False

try:
    from ir_generator import IRGenerator
    IR_OK = True
except ImportError:
    IR_OK = False

try:
    from interpreter_visitor import InterpreterVisitor
    INTERP_OK = True
except ImportError:
    INTERP_OK = False


# ─── Resultado del pipeline ──────────────────────────────────────────────────

class PipelineResult:
    def __init__(self):
        self.phases = []
        self.tac_code = ""
        self.ir_code = ""
        self.console_output = []
        self.ir_output = ""
        self.success = True
        self.stopped_at = None

    def add_phase(self, name, status, time_ms, errors=None, output=None):
        self.phases.append({
            "name":    name,
            "status":  status,
            "time_ms": round(time_ms, 3),
            "errors":  errors or [],
            "output":  output or ""
        })
        if status == "ERROR":
            self.success = False
            if self.stopped_at is None:
                self.stopped_at = name

    def to_dict(self):
        return {
            "phases":         self.phases,
            "tac_code":       self.tac_code,
            "ir_code":        self.ir_code,
            "console_output": self.console_output,
            "ir_output":      self.ir_output,
            "success":        self.success,
            "stopped_at":     self.stopped_at,
        }


# ─── Colector de errores ANTLR ───────────────────────────────────────────────

class ErrorCollector(antlr4.error.ErrorListener.ErrorListener):
    def __init__(self):
        super().__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append({
            "line":    line,
            "column":  column,
            "message": msg,
        })


# ─── Parsear errores semánticos (vienen como strings) ────────────────────────

def parse_semantic_errors(raw_errors):
    """
    Convierte la lista de strings de errores semánticos al formato dict.
    Tu semantic_visitor genera strings como:
      "[Error Semántico] Línea 5: Variable 'x' no declarada."
    """
    result = []
    for e in raw_errors:
        line = 0
        col  = 0
        msg  = str(e)
        m = re.search(r'[Ll]í?nea\s+(\d+)', msg)
        if m:
            line = int(m.group(1))
        result.append({"line": line, "column": col, "message": msg})
    return result


# ─── Pipeline principal ──────────────────────────────────────────────────────

def run_pipeline(source_code: str,
                 tac_file: str = "output.tac",
                 ll_file:  str = "output.ll") -> PipelineResult:

    result = PipelineResult()

    # ══════════════════════════════════════════════
    # FASE 1 — LÉXICO
    # ══════════════════════════════════════════════
    t0 = time.perf_counter()
    try:
        input_stream = InputStream(source_code)
        lexer = ExpresionesLexer(input_stream)

        lex_err = ErrorCollector()
        lexer.removeErrorListeners()
        lexer.addErrorListener(lex_err)

        token_stream = CommonTokenStream(lexer)
        token_stream.fill()

        elapsed = (time.perf_counter() - t0) * 1000

        if lex_err.errors:
            result.add_phase("Léxico", "ERROR", elapsed, errors=lex_err.errors)
            return result
        result.add_phase("Léxico", "OK", elapsed)

    except Exception as e:
        elapsed = (time.perf_counter() - t0) * 1000
        result.add_phase("Léxico", "ERROR", elapsed,
                         errors=[{"line": 0, "column": 0, "message": str(e)}])
        return result

    # ══════════════════════════════════════════════
    # FASE 2 — SINTÁCTICO
    # ══════════════════════════════════════════════
    t0 = time.perf_counter()
    try:
        parser = ExpresionesParser(token_stream)

        syn_err = ErrorCollector()
        parser.removeErrorListeners()
        parser.addErrorListener(syn_err)

        tree = parser.root()
        elapsed = (time.perf_counter() - t0) * 1000

        if syn_err.errors:
            result.add_phase("Sintáctico", "ERROR", elapsed, errors=syn_err.errors)
            return result
        result.add_phase("Sintáctico", "OK", elapsed)

    except Exception as e:
        elapsed = (time.perf_counter() - t0) * 1000
        result.add_phase("Sintáctico", "ERROR", elapsed,
                         errors=[{"line": 0, "column": 0, "message": str(e)}])
        return result

    # ══════════════════════════════════════════════
    # FASE 3 — SEMÁNTICO
    # ══════════════════════════════════════════════
    t0 = time.perf_counter()
    if not SEMANTIC_OK:
        elapsed = (time.perf_counter() - t0) * 1000
        result.add_phase("Semántico", "SKIP", elapsed,
                         output="semantic_visitor.py no encontrado")
    else:
        try:
            semantic = SemanticVisitor()
            semantic.visit(tree)
            elapsed = (time.perf_counter() - t0) * 1000

            # Tu SemanticVisitor usa self.errores (lista de strings)
            errores_raw = getattr(semantic, "errores", [])

            if errores_raw:
                fmt = parse_semantic_errors(errores_raw)
                result.add_phase("Semántico", "ERROR", elapsed, errors=fmt)
                return result
            else:
                result.add_phase("Semántico", "OK", elapsed)

        except Exception as e:
            elapsed = (time.perf_counter() - t0) * 1000
            result.add_phase("Semántico", "ERROR", elapsed,
                             errors=[{"line": 0, "column": 0, "message": str(e)}])
            return result

    # ══════════════════════════════════════════════
    # FASE 4 — TAC
    # ══════════════════════════════════════════════
    t0 = time.perf_counter()
    if not TAC_OK:
        elapsed = (time.perf_counter() - t0) * 1000
        result.add_phase("TAC", "SKIP", elapsed, output="tac_generator.py no encontrado")
    else:
        try:
            tac_gen = TACGenerator()
            tac_gen.visit(tree)
            tac_code = tac_gen.get_code()
            tac_gen.write_to_file(tac_file)
            elapsed = (time.perf_counter() - t0) * 1000
            result.tac_code = tac_code
            result.add_phase("TAC", "OK", elapsed, output=tac_code)
        except Exception as e:
            elapsed = (time.perf_counter() - t0) * 1000
            result.add_phase("TAC", "ERROR", elapsed,
                             errors=[{"line": 0, "column": 0, "message": str(e)}])

    # ══════════════════════════════════════════════
    # FASE 5 — LLVM IR
    # ══════════════════════════════════════════════
    t0 = time.perf_counter()
    if not IR_OK:
        elapsed = (time.perf_counter() - t0) * 1000
        result.add_phase("LLVM IR", "SKIP", elapsed, output="ir_generator.py no encontrado")
    else:
        try:
            ir_gen = IRGenerator()
            ir_gen.visit(tree)
            ir_code = ir_gen.get_ir()
            ir_gen.write_to_file(ll_file)
            elapsed = (time.perf_counter() - t0) * 1000
            result.ir_code = ir_code
            result.add_phase("LLVM IR", "OK", elapsed, output=ir_code)
        except Exception as e:
            elapsed = (time.perf_counter() - t0) * 1000
            result.add_phase("LLVM IR", "ERROR", elapsed,
                             errors=[{"line": 0, "column": 0, "message": str(e)}])

    # ══════════════════════════════════════════════
    # FASE 6 — EJECUCIÓN
    # ══════════════════════════════════════════════
    t0 = time.perf_counter()
    interp_output = []

    # 6a — Intérprete del AST
    if INTERP_OK:
        try:
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            interp = InterpreterVisitor()
            with redirect_stdout(buf):
                interp.visit(tree)
            interp_output = buf.getvalue().splitlines()
        except Exception as e:
            interp_output = [f"[Error intérprete]: {e}"]

    result.console_output = interp_output

    # 6b — Ejecutar .ll con lli
    ir_exec_output = ""
    if os.path.exists(ll_file):
        try:
            proc = subprocess.run(
                ["lli", ll_file],
                capture_output=True, text=True, timeout=10
            )
            ir_exec_output = proc.stdout + proc.stderr
        except FileNotFoundError:
            ir_exec_output = "[lli no encontrado — instalar LLVM para ejecutar el IR]"
        except subprocess.TimeoutExpired:
            ir_exec_output = "[Timeout: ejecución del IR superó 10 segundos]"
        except Exception as e:
            ir_exec_output = f"[Error ejecutando lli]: {e}"

    elapsed = (time.perf_counter() - t0) * 1000
    result.ir_output = ir_exec_output
    result.add_phase("Ejecución", "OK", elapsed,
                     output="\n".join(interp_output))

    return result


# ─── Modo CLI ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python pipeline.py <archivo.txt>")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        code = f.read()

    res = run_pipeline(code)

    print("\n" + "═" * 55)
    print("  PIPELINE v3 — RESULTADOS")
    print("═" * 55)

    icons = {"OK": "✅", "ERROR": "❌", "SKIP": "⏭️"}
    for phase in res.phases:
        icon = icons.get(phase["status"], "?")
        print(f"  {icon}  {phase['name']:<15} {phase['status']:<6}  {phase['time_ms']:.2f} ms")
        for err in phase.get("errors", []):
            print(f"       └─ Línea {err['line']}, Col {err['column']}: {err['message']}")

    if res.tac_code:
        print("\n── TAC ───────────────────────────────────────────────")
        print(res.tac_code)

    if res.console_output:
        print("\n── Salida del Intérprete ─────────────────────────────")
        for line in res.console_output:
            print(line)

    if res.ir_output:
        print("\n── Salida de lli ─────────────────────────────────────")
        print(res.ir_output)

    print("═" * 55)