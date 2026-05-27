"""
optimizer.py — Optimización Automática del IR mediante LLVM Pass Manager (Nivel O3)

Fase 7 del Pipeline v4.  Aplica las transformaciones O3 sobre el módulo IR
generado por ir_generator.py y devuelve métricas de reducción comparativas.
"""

import re
from llvmlite import binding as llvm

# ─── Inicialización de LLVM (solo una vez por proceso) ───────────────────────

def _init_llvm():
    try:
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()
        # Inicializar targets adicionales para cross-compilation
        llvm.initialize_all_targets()
        llvm.initialize_all_asmprinters()
    except Exception:
        pass  # Ya inicializados en una llamada previa

_init_llvm()


# ─── Métricas de IR ──────────────────────────────────────────────────────────

def _count_instructions(ir_str: str) -> int:
    """Cuenta instrucciones reales (líneas que no son etiquetas, comentarios
    ni directivas de módulo)."""
    count = 0
    for line in ir_str.splitlines():
        s = line.strip()
        if not s:
            continue
        # Saltamos encabezados de módulo, atributos, comentarios y llaves
        if s.startswith((";", "source_filename", "target", "attributes",
                          "define ", "declare ", "@", "}", "!")):
            continue
        if s.endswith(":") and not "=" in s:
            continue          # etiqueta de bloque básico
        count += 1
    return count


def _count_functions(ir_str: str) -> int:
    return len(re.findall(r"^define ", ir_str, re.MULTILINE))


def _count_basic_blocks(ir_str: str) -> int:
    return len(re.findall(r"^\w[\w.]+:", ir_str, re.MULTILINE))


def _collect_metrics(ir_str: str) -> dict:
    return {
        "instructions": _count_instructions(ir_str),
        "functions":    _count_functions(ir_str),
        "basic_blocks": _count_basic_blocks(ir_str),
        "lines":        len([l for l in ir_str.splitlines() if l.strip()]),
    }


# ─── Detección de transformaciones aplicadas ─────────────────────────────────

def _detect_transformations(before: str, after: str) -> list[dict]:
    """Heurísticas para detectar qué tipo de optimizaciones se aplicaron."""
    transformations = []

    # Constant Folding / Constant Propagation
    # Si hay menos operaciones aritméticas y hay 'ret i32 <constante>'
    arith_before = len(re.findall(r"\b(add|mul|sub|sdiv|fadd|fmul)\b", before))
    arith_after  = len(re.findall(r"\b(add|mul|sub|sdiv|fadd|fmul)\b", after))
    const_rets   = len(re.findall(r"ret i\d+ \d+", after))
    if arith_before > arith_after or const_rets > 0:
        transformations.append({
            "name": "Constant Folding / Constant Propagation",
            "description": (
                "Expresiones evaluables en tiempo de compilación fueron "
                "calculadas directamente. El resultado se embebe como "
                "constante eliminando instrucciones de cómputo."
            ),
            "reduction": arith_before - arith_after,
        })

    # Dead Code Elimination
    instr_before = _count_instructions(before)
    instr_after  = _count_instructions(after)
    if instr_before > instr_after:
        transformations.append({
            "name": "Dead Code Elimination (DCE)",
            "description": (
                "Instrucciones cuyo resultado no era utilizado por ninguna "
                "instrucción posterior fueron eliminadas, reduciendo el "
                "número total de instrucciones del módulo."
            ),
            "reduction": instr_before - instr_after,
        })

    # Function Inlining
    calls_before = len(re.findall(r"\bcall\b", before))
    calls_after  = len(re.findall(r"\bcall\b", after))
    if calls_before > calls_after:
        transformations.append({
            "name": "Function Inlining",
            "description": (
                "Llamadas a funciones pequeñas fueron sustituidas por el "
                "cuerpo de la función directamente en el sitio de llamada, "
                "eliminando el overhead de la convención de llamada."
            ),
            "reduction": calls_before - calls_after,
        })

    # Loop Unrolling
    loops_before = len(re.findall(r"br i1.+loop|\.check:", before))
    loops_after  = len(re.findall(r"br i1.+loop|\.check:", after))
    if loops_before > loops_after:
        transformations.append({
            "name": "Loop Unrolling",
            "description": (
                "Ciclos con número de iteraciones conocido en tiempo de "
                "compilación fueron expandidos, eliminando las instrucciones "
                "de control (verificación de condición y actualización del "
                "contador)."
            ),
            "reduction": loops_before - loops_after,
        })

    # SROA / mem2reg
    alloca_before = before.count("alloca")
    alloca_after  = after.count("alloca")
    load_before   = before.count("load")
    load_after    = after.count("load")
    if alloca_before > alloca_after or load_before > load_after:
        transformations.append({
            "name": "SROA / mem2reg (Promotion to Registers)",
            "description": (
                "Variables locales (allocas) fueron promovidas a registros "
                "virtuales SSA, eliminando instrucciones load/store "
                "innecesarias y habilitando otras optimizaciones."
            ),
            "reduction": (alloca_before - alloca_after) + (load_before - load_after),
        })

    if not transformations:
        transformations.append({
            "name": "Sin optimizaciones aplicables",
            "description": (
                "El programa de entrada no ofrece oportunidades de "
                "optimización detectables con O3. El IR resultante es "
                "idéntico al original, lo cual es el resultado correcto "
                "cuando el código ya es óptimo."
            ),
            "reduction": 0,
        })

    return transformations


# ─── Optimizador principal ───────────────────────────────────────────────────

class OptimizationResult:
    """Contenedor de resultados de la optimización O3."""
    def __init__(self):
        self.ir_before:        str  = ""
        self.ir_after:         str  = ""
        self.metrics_before:   dict = {}
        self.metrics_after:    dict = {}
        self.transformations:  list = []
        self.reduction_pct:    float = 0.0
        self.success:          bool = False
        self.error:            str  = ""

    def to_dict(self) -> dict:
        reduction = 0
        if self.metrics_before.get("instructions", 0) > 0:
            red = (self.metrics_before["instructions"] -
                   self.metrics_after.get("instructions", 0))
            self.reduction_pct = round(
                (red / self.metrics_before["instructions"]) * 100, 2
            )
        return {
            "ir_before":       self.ir_before,
            "ir_after":        self.ir_after,
            "metrics_before":  self.metrics_before,
            "metrics_after":   self.metrics_after,
            "transformations": self.transformations,
            "reduction_pct":   self.reduction_pct,
            "success":         self.success,
            "error":           self.error,
        }


def optimize_ir(ir_str: str,
                opt_level: int = 3,
                output_file: str = "output.opt.ll") -> OptimizationResult:
    """
    Aplica el Pass Manager de LLVM nivel O3 sobre el IR dado.

    Parámetros
    ----------
    ir_str      : Código LLVM IR como string (generado por ir_generator.py)
    opt_level   : Nivel de optimización (0-3). Por defecto 3 (O3).
    output_file : Ruta donde guardar el IR optimizado.

    Retorna
    -------
    OptimizationResult con el IR antes/después y métricas de reducción.
    """
    result = OptimizationResult()
    result.ir_before = ir_str

    try:
        # ── 1. Parsear el IR ─────────────────────────────────────────────────
        mod = llvm.parse_assembly(ir_str)
        mod.verify()

        # Obtener triple del IR o usar el nativo
        triple = llvm.get_default_triple()
        try:
            mod.triple = triple
        except Exception:
            pass

        target  = llvm.Target.from_triple(triple)
        tm      = target.create_target_machine(opt=opt_level)

        # ── 2. Métricas ANTES ────────────────────────────────────────────────
        result.metrics_before = _collect_metrics(ir_str)

        # ── 3. Aplicar Pass Manager O3 ───────────────────────────────────────
        pto = llvm.PipelineTuningOptions()
        pto.speed_level       = opt_level
        pto.size_level        = 0
        pto.loop_interleaving = True
        pto.loop_unrolling    = True

        pb  = llvm.create_pass_builder(tm, pto)
        mpm = pb.getModulePassManager()
        mpm.run(mod, pb)

        # ── 4. IR optimizado ─────────────────────────────────────────────────
        optimized_ir = str(mod)
        result.ir_after = optimized_ir

        # ── 5. Métricas DESPUÉS ──────────────────────────────────────────────
        result.metrics_after = _collect_metrics(optimized_ir)

        # ── 6. Calcular reducción ────────────────────────────────────────────
        instr_before = result.metrics_before["instructions"]
        instr_after  = result.metrics_after["instructions"]
        if instr_before > 0:
            result.reduction_pct = round(
                ((instr_before - instr_after) / instr_before) * 100, 2
            )

        # ── 7. Detectar transformaciones ─────────────────────────────────────
        result.transformations = _detect_transformations(ir_str, optimized_ir)

        # ── 8. Guardar archivo ───────────────────────────────────────────────
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(optimized_ir)

        result.success = True

    except Exception as exc:
        result.error   = str(exc)
        result.success = False
        # Devolver el IR original sin modificar si falla la optimización
        if not result.ir_after:
            result.ir_after       = ir_str
            result.metrics_after  = result.metrics_before.copy()
            result.transformations = [{
                "name": "Error en optimización",
                "description": f"No se pudo aplicar O3: {exc}",
                "reduction": 0,
            }]

    return result