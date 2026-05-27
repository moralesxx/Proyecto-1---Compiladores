"""
binary_generator.py — Generación de Binarios Nativos
Compila el IR optimizado a binario Linux o ejecutable Windows (.exe)
desde WSL2 usando LLVM y cross-compilation toolchain (MinGW).
"""

import os
import time
import shutil
import subprocess
import platform

# ─── Targets ──────────────────────────────────────────────────────────────────

LINUX_TRIPLE   = "x86_64-pc-linux-gnu"
WINDOWS_TRIPLE = "x86_64-pc-windows-gnu"


def _run(cmd: list, timeout: int = 60) -> tuple:
    """Ejecuta un comando y retorna (returncode, stdout, stderr)."""
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError as e:
        return -1, "", f"Herramienta no encontrada: {e.filename}"
    except subprocess.TimeoutExpired:
        return -2, "", f"Timeout: el comando superó {timeout} segundos."
    except Exception as e:
        return -3, "", str(e)


def _tool_available(name: str) -> bool:
    return shutil.which(name) is not None


# ─── Clase de resultado ────────────────────────────────────────────────────────

class BinaryResult:
    def __init__(self, platform_target: str):
        self.platform      = platform_target   # "linux" | "windows"
        self.success       = False
        self.binary_path   = ""
        self.error         = ""
        self.time_ms       = 0.0
        self.size_bytes    = 0
        self.run_output    = ""
        self.steps         = []                # Pasos intermedios con estado

    def add_step(self, step: str, ok: bool, detail: str = ""):
        self.steps.append({"step": step, "ok": ok, "detail": detail})

    def to_dict(self):
        return {
            "platform":    self.platform,
            "success":     self.success,
            "binary_path": self.binary_path,
            "error":       self.error,
            "time_ms":     round(self.time_ms, 3),
            "size_bytes":  self.size_bytes,
            "run_output":  self.run_output,
            "steps":       self.steps,
        }


# ─── Generación para Linux ────────────────────────────────────────────────────

def compile_linux(ll_file: str = "output_opt.ll",
                  out_file: str = "output_linux") -> BinaryResult:
    """
    Compila el IR a binario nativo Linux usando llc + clang/gcc.
    Flujo: .ll → .o (llc) → binario (clang/gcc)
    """
    result = BinaryResult("linux")
    t0 = time.perf_counter()

    # Verificar archivo IR
    if not os.path.exists(ll_file):
        # Intentar con el IR no optimizado como fallback
        ll_file_fallback = "output.ll"
        if os.path.exists(ll_file_fallback):
            ll_file = ll_file_fallback
        else:
            result.error = f"Archivo IR '{ll_file}' no encontrado. Ejecutar la Fase 5 primero."
            result.time_ms = (time.perf_counter() - t0) * 1000
            return result

    obj_file = out_file + ".o"

    # Paso 1: llc → .o
    if _tool_available("llc"):
        rc, out, err = _run(["llc", "-filetype=obj",
                              "-relocation-model=pic",
                              "-o", obj_file, ll_file])
        if rc != 0:
            result.add_step("llc → .o", False, err.strip())
            # Intentar con clang directamente
        else:
            result.add_step("llc → .o", True, f"Objeto generado: {obj_file}")
            # Paso 2: enlazar con clang o gcc
            linker = "clang" if _tool_available("clang") else ("gcc" if _tool_available("gcc") else None)
            if linker is None:
                result.error = "No se encontró clang ni gcc para enlazar el objeto."
                result.time_ms = (time.perf_counter() - t0) * 1000
                return result
            rc2, out2, err2 = _run([linker, obj_file, "-o", out_file, "-lm", "-no-pie"])
            if rc2 != 0:
                # Intentar sin -no-pie
                rc2, out2, err2 = _run([linker, obj_file, "-o", out_file, "-lm"])
            if rc2 == 0:
                result.add_step(f"{linker} (enlazar)", True, f"Binario: {out_file}")
            else:
                result.add_step(f"{linker} (enlazar)", False, err2.strip())
                result.error = f"Error de enlazado: {err2.strip()}"
                result.time_ms = (time.perf_counter() - t0) * 1000
                return result
    else:
        # Sin llc: intentar directamente con clang
        if not _tool_available("clang"):
            result.error = ("No se encontró 'llc' ni 'clang'. "
                            "Instalar con: sudo apt install llvm clang")
            result.time_ms = (time.perf_counter() - t0) * 1000
            return result
        rc, out, err = _run(["clang", ll_file, "-o", out_file, "-lm"])
        if rc != 0:
            result.add_step("clang (compilar+enlazar)", False, err.strip())
            result.error = f"Error compilando con clang: {err.strip()}"
            result.time_ms = (time.perf_counter() - t0) * 1000
            return result
        result.add_step("clang (compilar+enlazar)", True, f"Binario: {out_file}")

    # Verificar que el binario existe
    if not os.path.exists(out_file):
        result.error = "El binario no fue generado correctamente."
        result.time_ms = (time.perf_counter() - t0) * 1000
        return result

    result.binary_path = os.path.abspath(out_file)
    result.size_bytes  = os.path.getsize(out_file)

    # Hacer ejecutable
    os.chmod(out_file, 0o755)

    # Ejecutar y capturar salida
    rc_run, out_run, err_run = _run([out_file], timeout=10)
    result.run_output = (out_run + err_run).strip()
    result.add_step("Ejecutar binario Linux", rc_run >= 0, result.run_output[:300] if result.run_output else "(sin salida)")

    # Limpieza del .o
    if os.path.exists(obj_file):
        os.remove(obj_file)

    result.success = True
    result.time_ms = (time.perf_counter() - t0) * 1000
    return result


# ─── Generación para Windows (.exe) ──────────────────────────────────────────

def compile_windows(ll_file: str = "output_opt.ll",
                    out_file: str = "output_windows.exe") -> BinaryResult:
    """
    Genera un .exe para Windows 64-bit mediante cross-compilation desde WSL2.
    Requiere: x86_64-w64-mingw32-gcc (sudo apt install mingw-w64)
              o clang con target windows.
    Flujo: .ll → bitcode → .exe  (via clang --target o llc + mingw32-gcc)
    """
    result = BinaryResult("windows")
    t0 = time.perf_counter()

    if not os.path.exists(ll_file):
        ll_file_fallback = "output.ll"
        if os.path.exists(ll_file_fallback):
            ll_file = ll_file_fallback
        else:
            result.error = f"Archivo IR '{ll_file}' no encontrado. Ejecutar la Fase 5 primero."
            result.time_ms = (time.perf_counter() - t0) * 1000
            return result

    # Estrategia 1: clang con target windows (más directo)
    clang_w64 = "x86_64-w64-mingw32-clang" if _tool_available("x86_64-w64-mingw32-clang") else None
    clang_generic = "clang" if _tool_available("clang") else None

    obj_file = out_file.replace(".exe", ".obj")

    # Estrategia 2: llc + mingw32 linker
    mingw_gcc = "x86_64-w64-mingw32-gcc" if _tool_available("x86_64-w64-mingw32-gcc") else None

    if clang_w64:
        # Clang con target MinGW
        rc, out, err = _run([clang_w64, ll_file,
                              "-target", WINDOWS_TRIPLE,
                              "-o", out_file, "-lm"])
        if rc == 0:
            result.add_step("clang (cross-win64)", True, f".exe generado: {out_file}")
        else:
            result.add_step("clang (cross-win64)", False, err.strip())

    elif clang_generic and mingw_gcc:
        # llc → .obj → mingw-gcc
        if _tool_available("llc"):
            rc, out, err = _run(["llc",
                                  "-mtriple=" + WINDOWS_TRIPLE,
                                  "-filetype=obj",
                                  "-o", obj_file, ll_file])
            if rc != 0:
                result.add_step("llc → .obj (win64)", False, err.strip())
            else:
                result.add_step("llc → .obj (win64)", True, f"Objeto: {obj_file}")
                rc2, out2, err2 = _run([mingw_gcc, obj_file, "-o", out_file,
                                        "-static", "-lm"])
                if rc2 == 0:
                    result.add_step("mingw32-gcc (enlazar)", True, f".exe: {out_file}")
                else:
                    result.add_step("mingw32-gcc (enlazar)", False, err2.strip())
                    result.error = f"Error de enlazado: {err2.strip()}"
                    result.time_ms = (time.perf_counter() - t0) * 1000
                    return result
        else:
            result.error = "llc no disponible para compilación cruzada."
            result.time_ms = (time.perf_counter() - t0) * 1000
            return result

    elif clang_generic:
        # clang genérico con --target
        rc, out, err = _run([clang_generic, ll_file,
                              "--target=" + WINDOWS_TRIPLE,
                              "-o", out_file])
        if rc == 0:
            result.add_step("clang --target win64", True, f".exe generado: {out_file}")
        else:
            result.add_step("clang --target win64", False, err.strip())
            result.error = (
                "No se encontraron herramientas de cross-compilación para Windows.\n"
                "Instalar con:\n"
                "  sudo apt install mingw-w64\n"
                "  sudo apt install clang llvm\n"
                f"Detalle: {err.strip()}"
            )
            result.time_ms = (time.perf_counter() - t0) * 1000
            return result

    elif mingw_gcc and _tool_available("llc"):
        rc, out, err = _run(["llc",
                              "-mtriple=" + WINDOWS_TRIPLE,
                              "-filetype=obj",
                              "-o", obj_file, ll_file])
        if rc == 0:
            result.add_step("llc → .obj (win64)", True, "")
            rc2, out2, err2 = _run([mingw_gcc, obj_file, "-o", out_file, "-static"])
            if rc2 == 0:
                result.add_step("mingw32-gcc (enlazar)", True, f".exe: {out_file}")
            else:
                result.add_step("mingw32-gcc (enlazar)", False, err2.strip())
                result.error = err2.strip()
                result.time_ms = (time.perf_counter() - t0) * 1000
                return result
        else:
            result.add_step("llc (cross)", False, err.strip())
            result.error = err.strip()
            result.time_ms = (time.perf_counter() - t0) * 1000
            return result
    else:
        result.error = (
            "No se encontraron herramientas de cross-compilación para Windows.\n"
            "Instalar con:\n"
            "  sudo apt install mingw-w64 llvm clang"
        )
        result.time_ms = (time.perf_counter() - t0) * 1000
        return result

    # Verificar .exe
    if not os.path.exists(out_file):
        result.error = "El ejecutable .exe no fue generado."
        result.time_ms = (time.perf_counter() - t0) * 1000
        return result

    result.binary_path = os.path.abspath(out_file)
    result.size_bytes  = os.path.getsize(out_file)

    # Intentar ejecutar con wine (si disponible) para verificar
    wine = "wine" if _tool_available("wine") else None
    if wine:
        rc_run, out_run, err_run = _run([wine, out_file], timeout=15)
        result.run_output = (out_run + err_run).strip()
        result.add_step("Verificar con wine", rc_run >= 0,
                        result.run_output[:300] if result.run_output else "(sin salida)")
    else:
        result.run_output = (
            "[wine no disponible en este entorno — transferir el .exe a Windows para ejecutarlo]\n"
            f"Ruta del ejecutable: {result.binary_path}"
        )

    # Limpieza
    if os.path.exists(obj_file):
        os.remove(obj_file)

    result.success = True
    result.time_ms = (time.perf_counter() - t0) * 1000
    return result


def check_tools() -> dict:
    """Verifica las herramientas disponibles para compilación binaria."""
    tools = {
        "llc":                    _tool_available("llc"),
        "clang":                  _tool_available("clang"),
        "gcc":                    _tool_available("gcc"),
        "lli":                    _tool_available("lli"),
        "x86_64-w64-mingw32-gcc": _tool_available("x86_64-w64-mingw32-gcc"),
        "x86_64-w64-mingw32-clang": _tool_available("x86_64-w64-mingw32-clang"),
        "wine":                   _tool_available("wine"),
    }
    tools["linux_compile_ready"]   = tools["llc"] or tools["clang"]
    tools["windows_compile_ready"] = (
        (tools["llc"] and tools["x86_64-w64-mingw32-gcc"]) or
        tools["x86_64-w64-mingw32-clang"] or
        (tools["clang"] and tools["x86_64-w64-mingw32-gcc"])
    )
    return tools


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "linux"
    ll     = sys.argv[2] if len(sys.argv) > 2 else "output_opt.ll"

    tools = check_tools()
    print("Herramientas disponibles:")
    for k, v in tools.items():
        if not k.endswith("_ready"):
            print(f"  {'✅' if v else '❌'} {k}")

    if target == "linux":
        res = compile_linux(ll)
    elif target == "windows":
        res = compile_windows(ll)
    else:
        print(f"Target desconocido: {target}. Usar 'linux' o 'windows'.")
        sys.exit(1)

    if res.success:
        print(f" Binario generado para {target} en {res.time_ms:.2f} ms")
        print(f"   Ruta: {res.binary_path}")
        print(f"   Tamaño: {res.size_bytes:,} bytes")
        if res.run_output:
            print(f"   Salida:\n{res.run_output}")
    else:
        print(f"❌ Error generando binario para {target}: {res.error}")
    for step in res.steps:
        icon = "  ✅" if step["ok"] else "  ❌"
        print(f"{icon} {step['step']}: {step['detail']}")