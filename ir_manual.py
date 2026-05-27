"""
ir_manual.py — Módulo de Optimización Manual del IR (Panel Interactivo)

Permite seleccionar y aplicar passes de optimización individuales sobre el IR,
generando un comparador diff y permitiendo re-ejecución del resultado.

Passes disponibles (mínimos requeridos por el proyecto):
  mem2reg, instcombine, simplifycfg, dce, inline, loop-unroll
"""

import re
import subprocess
import tempfile
import os
from llvmlite import binding as llvm

# ─── Inicialización de LLVM ───────────────────────────────────────────────────

def _init_llvm():
    try:
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()
    except Exception:
        pass

_init_llvm()


# ─── Catálogo de passes disponibles ─────────────────────────────────────────

AVAILABLE_PASSES = {
    "mem2reg": {
        "label":       "mem2reg",
        "name":        "Memory to Register (mem2reg / SROA)",
        "description": (
            "Promueve variables locales (allocas) a registros virtuales SSA. "
            "Elimina instrucciones load/store redundantes y convierte el IR "
            "a forma SSA pura, habilitando todas las demás optimizaciones."
        ),
        "category": "Memoria",
    },
    "instcombine": {
        "label":       "instcombine",
        "name":        "Instruction Combine (instcombine)",
        "description": (
            "Combina secuencias de instrucciones simples en instrucciones "
            "equivalentes más eficientes. Por ejemplo, reemplaza 'x + 0' por 'x', "
            "o colapsa operaciones aritméticas y lógicas consecutivas de tipo constante."
        ),
        "category": "Peephole",
    },
    "simplifycfg": {
        "label":       "simplifycfg",
        "name":        "Simplify Control Flow Graph (simplifycfg)",
        "description": (
            "Simplifica el grafo de flujo de control eliminando bloques básicos vacíos, "
            "fusionando bloques consecutivos con una única transición clara y eliminando "
            "saltos inalcanzables del código."
        ),
        "category": "Estructural",
    },
    "dce": {
        "label":       "dce",
        "name":        "Dead Code Elimination (dce)",
        "description": (
            "Elimina de forma agresiva instrucciones muertas, es decir, instrucciones "
            "cuyos resultados nunca son leídos por ninguna otra operación posterior del programa, "
            "reduciendo drásticamente el tamaño del código."
        ),
        "category": "Eliminación",
    },
    "inline": {
        "label":       "inline",
        "name":        "Function Inlining (inline)",
        "description": (
            "Reemplaza las llamadas a funciones pequeñas insertando el cuerpo de la función "
            "directamente en el lugar de la invocación. Elimina el costo del salto y la "
            "creación del marco de activación en la pila."
        ),
        "category": "Interprocedural",
    },
    "loop-unroll": {
        "label":       "loop-unroll",
        "name":        "Loop Unrolling (loop-unroll)",
        "description": (
            "Desenrolla los ciclos duplicando el cuerpo del bucle para disminuir el número "
            "de evaluaciones de la condición de parada y los saltos condicionales, "
            "mejorando sustancialmente el paralelismo de la CPU."
        ),
        "category": "Ciclos",
    }
}


# ─── Estructura de Retorno para el Frontend ─────────────────────────────────

class ManualOptimizationResult:
    def __init__(self):
        self.success = False
        self.ir_before = ""
        self.ir_after = ""
        self.passes_applied = []
        self.diff = []            # Lista de diccionarios con operaciones diff
        self.unchanged = True
        self.error = ""
        self.lli_result = {"success": False, "output": "", "error": ""}


# ─── Generación de Diff utilizando la librería diff_match_patch ──────────────

def _generate_diff(before: str, after: str):
    """
    Genera un diff estructural entre dos versiones de código IR.
    """
    try:
        from diff_match_patch import diff_match_patch
        dmp = diff_match_patch()
        diffs = dmp.diff_main(before, after)
        dmp.diff_cleanupSemantic(diffs)
        
        formatted_diff = []
        for op, text in diffs:
            if op == 0:    # EQUAL
                operation = "equal"
            elif op == 1:  # INSERT
                operation = "insert"
            elif op == -1: # DELETE
                operation = "delete"
                
            formatted_diff.append({
                "operation": operation,
                "text":      text
            })
        return formatted_diff
    except Exception:
        # Fallback si no está instalada la librería en el entorno
        return [
            {"operation": "delete", "text": "--- IR ORIGINAL ---\n" + before},
            {"operation": "insert", "text": "--- IR OPTIMIZADO ---\n" + after}
        ]


# ─── Ejecución con lli de forma silenciosa ────────────────────────────────────

def _run_ir_with_lli(ir_str: str) -> dict:
    try:
        with tempfile.NamedTemporaryFile(suffix=".ll", delete=False, mode="w", encoding="utf-8") as tmp:
            tmp.write(ir_str)
            tmp_path = tmp.name

        res = subprocess.run(["lli", tmp_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
        
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

        if res.returncode == 0:
            return {"success": True, "output": res.stdout, "error": ""}
        else:
            return {"success": False, "output": res.stdout, "error": res.stderr}
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "", "error": "[Timeout lli - Posible ciclo infinito]"}
    except Exception as e:
        return {"success": False, "output": "", "error": f"[Error de lli]: {str(e)}"}


# ─── API Principal ───────────────────────────────────────────────────────────

def get_available_passes() -> dict:
    """Devuelve el catálogo de passes soportados por la interfaz."""
    return AVAILABLE_PASSES


def apply_manual_passes(ir_str: str, passes: list, run_with_lli: bool = True, output_file: str = "output.manual.ll") -> ManualOptimizationResult:
    """
    Aplica una secuencia ordenada de passes sobre el código LLVM IR provisto.
    """
    result = ManualOptimizationResult()
    result.ir_before = ir_str

    if not ir_str.strip():
        result.error = "El código LLVM IR de entrada está vacío."
        return result

    try:
        # Parsear el módulo de texto a un objeto LLVM Module real
        mod = llvm.parse_assembly(ir_str)
        mod.verify()

        # Configurar las estructuras de passes nativos de LLVM
        mpm = llvm.create_module_pass_manager()

        applied = []
        for p in passes:
            p_clean = p.strip().lower()
            if p_clean not in AVAILABLE_PASSES:
                continue

            # Agregar passes correspondientes mapeados de manera nativa
            try:
                if p_clean == "mem2reg":
                    mpm.add_scalar_repl_aggregates_pass()
                    applied.append("mem2reg")
                elif p_clean == "instcombine":
                    mpm.add_instruction_combining_pass()
                    applied.append("instcombine")
                elif p_clean == "simplifycfg":
                    mpm.add_cfg_simplification_pass()
                    applied.append("simplifycfg")
                elif p_clean == "dce":
                    mpm.add_dead_code_elimination_pass()
                    applied.append("dce")
                elif p_clean == "inline":
                    mpm.add_function_inlining_pass(275)
                    applied.append("inline")
                elif p_clean == "loop-unroll":
                    mpm.add_loop_unroll_pass()
                    applied.append("loop-unroll")
            except Exception as pe:
                pass

        # ── FIX EXTRA: mpm.run requiere solo el módulo en las versiones nuevas de llvmlite
        mpm.run(mod)

        optimized_ir = str(mod)
        result.ir_after      = optimized_ir
        result.passes_applied = applied
        result.unchanged      = (ir_str.strip() == optimized_ir.strip())

        # ── Generar diff ──────────────────────────────────────────────────────
        result.diff = _generate_diff(ir_str, optimized_ir)

        # ── Guardar archivo ───────────────────────────────────────────────────
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(optimized_ir)

        # ── Ejecutar con lli ──────────────────────────────────────────────────
        if run_with_lli:
            result.lli_result = _run_ir_with_lli(optimized_ir)
        else:
            result.lli_result = {"success": False, "output": "", "error": "Ejecución no solicitada"}

        result.success = True

    except Exception as exc:
        result.error   = str(exc)
        result.success = False
        result.ir_after = ir_str
        result.diff     = []

    return result


def export_manual_ir(ir_str: str, output_file: str = "output.manual.ll") -> bool:
    """Guarda el IR manual en disco. Retorna True si tuvo éxito."""
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(ir_str)
        return True
    except Exception:
        return False