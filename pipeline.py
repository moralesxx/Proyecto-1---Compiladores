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

# ── Importar módulos nuevos (Fase 7 y 8) ────────────────────────────────────
try:
    from optimizer import optimize_ir
    OPTIMIZER_OK = True
except ImportError:
    OPTIMIZER_OK = False

try:
    from ir_manual import apply_manual_passes, get_available_passes
    IR_MANUAL_OK = True
except ImportError:
    IR_MANUAL_OK = False


# ─── Resultado del pipeline ──────────────────────────────────────────────────

class PipelineResult:
    def __init__(self):
        self.phases = []
        self.tac_code = ""
        self.ir_code = ""
        self.ir_optimized = ""
        self.console_output = []
        self.ir_output = ""
        self.success = True
        self.stopped_at = None
        # Fase 7
        self.opt_metrics_before  = {}
        self.opt_metrics_after   = {}
        self.opt_transformations = []
        self.opt_reduction_pct   = 0.0
        # Fase 8
        self.binary_linux          = ""
        self.binary_windows        = ""
        self.binary_linux_output   = ""
        self.binary_windows_output = ""

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
            "phases":               self.phases,
            "tac_code":             self.tac_code,
            "ir_code":              self.ir_code,
            "ir_optimized":         self.ir_optimized,
            "console_output":       self.console_output,
            "ir_output":            self.ir_output,
            "success":              self.success,
            "stopped_at":           self.stopped_at,
            "opt_metrics_before":   self.opt_metrics_before,
            "opt_metrics_after":    self.opt_metrics_after,
            "opt_transformations":  self.opt_transformations,
            "opt_reduction_pct":    self.opt_reduction_pct,
            "binary_linux":         self.binary_linux,
            "binary_windows":       self.binary_windows,
            "binary_linux_output":  self.binary_linux_output,
            "binary_windows_output":self.binary_windows_output,
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


# ─── Parsear errores semánticos ───────────────────────────────────────────────

def parse_semantic_errors(raw_errors):
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


# ─── Fase 8: compilación a binarios nativos ──────────────────────────────────

def _compile_linux_binary(ll_file, out_bin="output_linux"):
    t0 = time.perf_counter()
    obj_file = ll_file.replace(".ll", ".o")
    res = {"success": False, "path": "", "time_ms": 0.0, "output": ""}
    try:
        proc = subprocess.run(
            ["clang", "-O2", ll_file, "-o", out_bin],
            capture_output=True, text=True, timeout=30
        )
        elapsed = (time.perf_counter() - t0) * 1000
        res["time_ms"] = round(elapsed, 3)
        if proc.returncode == 0 and os.path.exists(out_bin):
            res["success"] = True
            res["path"]    = os.path.abspath(out_bin)
            res["output"]  = f"Binario Linux generado: {out_bin}"
        else:
            # Fallback llc + gcc
            llc = subprocess.run(
                ["llc", "-filetype=obj", ll_file, "-o", obj_file],
                capture_output=True, text=True, timeout=30
            )
            if llc.returncode == 0:
                lnk = subprocess.run(
                    ["gcc", obj_file, "-o", out_bin],
                    capture_output=True, text=True, timeout=30
                )
                elapsed2 = (time.perf_counter() - t0) * 1000
                res["time_ms"] = round(elapsed2, 3)
                if lnk.returncode == 0 and os.path.exists(out_bin):
                    res["success"] = True
                    res["path"]    = os.path.abspath(out_bin)
                    res["output"]  = f"Binario Linux generado (llc+gcc): {out_bin}"
                else:
                    res["output"] = lnk.stderr or proc.stderr or "[Error enlazando binario Linux]"
            else:
                res["output"] = llc.stderr or proc.stderr or "[clang/llc no disponibles]"
    except FileNotFoundError:
        elapsed = (time.perf_counter() - t0) * 1000
        res["time_ms"] = round(elapsed, 3)
        res["output"]  = "[clang no encontrado. Instalar: sudo apt install clang]"
    except subprocess.TimeoutExpired:
        res["time_ms"] = round((time.perf_counter() - t0) * 1000, 3)
        res["output"]  = "[Timeout compilando binario Linux]"
    except Exception as exc:
        res["time_ms"] = round((time.perf_counter() - t0) * 1000, 3)
        res["output"]  = f"[Error]: {exc}"
    if os.path.exists(obj_file):
        try: os.unlink(obj_file)
        except Exception: pass
    return res


def _compile_windows_binary(ll_file, out_exe="output_windows.exe"):
    t0 = time.perf_counter()
    obj_file = ll_file.replace(".ll", "_win.o")
    res = {"success": False, "path": "", "time_ms": 0.0, "output": ""}
    win_triple = "x86_64-w64-mingw32"
    cross_gcc  = f"{win_triple}-gcc"
    try:
        llc = subprocess.run(
            ["llc", "-mtriple", win_triple, "-filetype=obj", ll_file, "-o", obj_file],
            capture_output=True, text=True, timeout=30
        )
        if llc.returncode != 0:
            res["time_ms"] = round((time.perf_counter() - t0) * 1000, 3)
            res["output"]  = llc.stderr or "[Error llc para Windows]"
            return res
        lnk = subprocess.run(
            [cross_gcc, obj_file, "-o", out_exe, "-static"],
            capture_output=True, text=True, timeout=30
        )
        elapsed = (time.perf_counter() - t0) * 1000
        res["time_ms"] = round(elapsed, 3)
        if lnk.returncode == 0 and os.path.exists(out_exe):
            res["success"] = True
            res["path"]    = os.path.abspath(out_exe)
            res["output"]  = (f"Ejecutable Windows (.exe): {out_exe}\n"
                              f"Triple: {win_triple} | Enlazador: {cross_gcc}")
        else:
            res["output"] = (lnk.stderr or
                             f"[{cross_gcc} no encontrado. Instalar: sudo apt install mingw-w64]")
    except FileNotFoundError:
        res["time_ms"] = round((time.perf_counter() - t0) * 1000, 3)
        res["output"]  = "[Herramientas cross no encontradas. Instalar: sudo apt install llvm clang mingw-w64]"
    except subprocess.TimeoutExpired:
        res["time_ms"] = round((time.perf_counter() - t0) * 1000, 3)
        res["output"]  = "[Timeout compilando .exe]"
    except Exception as exc:
        res["time_ms"] = round((time.perf_counter() - t0) * 1000, 3)
        res["output"]  = f"[Error]: {exc}"
    if os.path.exists(obj_file):
        try: os.unlink(obj_file)
        except Exception: pass
    return res


def _run_binary(binary_path, timeout=10):
    if not os.path.exists(binary_path):
        return "[Binario no encontrado]"
    try:
        proc = subprocess.run([binary_path], capture_output=True, text=True, timeout=timeout)
        return (proc.stdout + proc.stderr).strip()
    except subprocess.TimeoutExpired:
        return "[Timeout ejecutando binario]"
    except Exception as exc:
        return f"[Error ejecutando binario]: {exc}"


# ─── Pipeline principal ──────────────────────────────────────────────────────

def run_pipeline(
    source_code,
    tac_file        = "output.tac",
    ll_file         = "output.ll",
    opt_ll_file     = "output.opt.ll",
    linux_bin       = "output_linux",
    windows_exe     = "output_windows.exe",
    compile_linux   = True,
    compile_windows = True,
):

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
    ir_generated = False
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
            ir_generated = True
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
    result.add_phase("Ejecución", "OK", elapsed, output="\n".join(interp_output))

    # ══════════════════════════════════════════════
    # FASE 7 — OPTIMIZACIÓN O3 ★
    # ══════════════════════════════════════════════
    t0 = time.perf_counter()
    if not ir_generated:
        elapsed = (time.perf_counter() - t0) * 1000
        result.add_phase("Optimización O3", "SKIP", elapsed,
                         output="Se requiere IR generado (Fase 5) para optimizar.")
    elif not OPTIMIZER_OK:
        elapsed = (time.perf_counter() - t0) * 1000
        result.add_phase("Optimización O3", "SKIP", elapsed,
                         output="optimizer.py no encontrado")
    else:
        try:
            opt_result = optimize_ir(result.ir_code, opt_level=3,
                                     output_file=opt_ll_file)
            elapsed = (time.perf_counter() - t0) * 1000
            result.ir_optimized        = opt_result.ir_after
            result.opt_metrics_before  = opt_result.metrics_before
            result.opt_metrics_after   = opt_result.metrics_after
            result.opt_transformations = opt_result.transformations
            result.opt_reduction_pct   = opt_result.reduction_pct
            if opt_result.success:
                metrics_summary = (
                    f"Instrucciones: {opt_result.metrics_before.get('instructions',0)} → "
                    f"{opt_result.metrics_after.get('instructions',0)} "
                    f"({opt_result.reduction_pct}% reducción)"
                )
                result.add_phase("Optimización O3", "OK", elapsed, output=metrics_summary)
            else:
                result.add_phase("Optimización O3", "ERROR", elapsed,
                                 errors=[{"line": 0, "column": 0,
                                          "message": opt_result.error}])
        except Exception as e:
            elapsed = (time.perf_counter() - t0) * 1000
            result.add_phase("Optimización O3", "ERROR", elapsed,
                             errors=[{"line": 0, "column": 0, "message": str(e)}])

    # ══════════════════════════════════════════════
    # FASE 8 — BINARIOS NATIVOS ★
    # ══════════════════════════════════════════════
    t0 = time.perf_counter()
    source_ll = opt_ll_file if os.path.exists(opt_ll_file) else ll_file

    if not ir_generated:
        elapsed = (time.perf_counter() - t0) * 1000
        result.add_phase("Binarios Nativos", "SKIP", elapsed,
                         output="Se requiere IR generado (Fase 5) para compilar binarios.")
    else:
        parts  = []
        # Linux
        if compile_linux:
            lr = _compile_linux_binary(source_ll, linux_bin)
            result.binary_linux        = lr["path"]
            result.binary_linux_output = lr["output"]
            if lr["success"]:
                parts.append(f"✅ Linux: {lr['path']} ({lr['time_ms']} ms)")
                bout = _run_binary(lr["path"])
                if bout:
                    result.binary_linux_output += f"\n--- Salida ---\n{bout}"
            else:
                parts.append(f"⚠ Linux: {lr['output']}")

        # Windows
        if compile_windows:
            wr = _compile_windows_binary(source_ll, windows_exe)
            result.binary_windows        = wr["path"]
            result.binary_windows_output = wr["output"]
            if wr["success"]:
                parts.append(f"✅ Windows (.exe): {wr['path']} ({wr['time_ms']} ms)")
            else:
                parts.append(f"⚠ Windows: {wr['output']}")

        elapsed = (time.perf_counter() - t0) * 1000
        any_ok  = (
            (compile_linux   and result.binary_linux   != "") or
            (compile_windows and result.binary_windows != "")
        )
        result.add_phase("Binarios Nativos", "OK" if any_ok else "SKIP",
                         elapsed, output="\n".join(parts))

    return result


# ─── Modo CLI ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python pipeline.py <archivo.txt>")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        code = f.read()

    res = run_pipeline(code)

    print("\n" + "═" * 60)
    print("  PIPELINE v4 — RESULTADOS")
    print("═" * 60)

    icons = {"OK": "✅", "ERROR": "❌", "SKIP": "⏭️"}
    for phase in res.phases:
        icon = icons.get(phase["status"], "?")
        print(f"  {icon}  {phase['name']:<22} {phase['status']:<6}  {phase['time_ms']:.2f} ms")
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

    if res.opt_reduction_pct:
        print(f"\n── Optimización O3: {res.opt_reduction_pct}% de reducción ─")
        for t in res.opt_transformations:
            print(f"   • {t['name']}")

    if res.binary_linux:
        print(f"\n── Binario Linux: {res.binary_linux}")
    if res.binary_windows:
        print(f"\n── Ejecutable Windows: {res.binary_windows}")

    print("═" * 60)