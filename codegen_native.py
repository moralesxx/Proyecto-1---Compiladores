"""
codegen_native.py — Generación de Ejecutables Nativo para Linux y Windows (.exe)
Fase 8 del Pipeline v4.
"""

import subprocess
import os
import tempfile

def compile_to_native(ir_str: str, output_name: str = "output_program") -> bool:
    """
    Toma el código LLVM IR de la fase anterior, genera un archivo temporal .ll,
    y utiliza clang / llc para compilar el archivo binario ejecutable nativo.
    """
    try:
        # Crear archivo temporal con el código IR
        with tempfile.NamedTemporaryFile(suffix=".ll", delete=False, mode="w", encoding="utf-8") as tmp_ir:
            tmp_ir.write(ir_str)
            tmp_ir_path = tmp_ir.name

        # Determinar nombres de salida según la plataforma destino
        # Generar binario ejecutable nativo
        cmd = ["clang", tmp_ir_path, "-o", output_name, "-O3"]
        
        # Ejecutar la compilación nativa a través de un subproceso silencioso
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Limpieza del archivo temporal .ll
        if os.path.exists(tmp_ir_path):
            os.unlink(tmp_ir_path)
            
        if res.returncode == 0:
            return True
        else:
            print(f"[Codegen Native Error]: {res.stderr}")
            return False
            
    except Exception as e:
        print(f"[Codegen Native Exception]: {str(e)}")
        return False