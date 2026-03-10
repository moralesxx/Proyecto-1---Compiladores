import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from antlr4 import *
from ExpresionesLexer import ExpresionesLexer
from ExpresionesParser import ExpresionesParser
from Visitor import Visitor

def seleccionar_archivo():
    if len(sys.argv) < 2:
        print("Uso: python3 Prueba.py <archivo>")
        sys.exit(1)

    archivo_ruta = sys.argv[1]

    if not os.path.isfile(archivo_ruta):
        print(f"Error: El archivo '{archivo_ruta}' no existe.")
        sys.exit(1)

    return archivo_ruta

def main():
    # --- PASO 1: SELECCIONAR ARCHIVO DINÁMICAMENTE ---
    archivo_ruta = seleccionar_archivo()

    if not archivo_ruta:
        print("No se seleccionó ningún archivo. Saliendo...")
        return

    try:
        # --- PASO 2: LECTURA Y ANÁLISIS ---
        input_stream = FileStream(archivo_ruta, encoding='utf-8')
        lexer = ExpresionesLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = ExpresionesParser(token_stream)
        
        # Generamos el árbol desde la regla 'root' definida en tu .g4
        tree = parser.root()

        # Verificar errores sintácticos según requerimiento 
        if parser.getNumberOfSyntaxErrors() > 0:
            print(f"\n[ERROR] El archivo '{archivo_ruta}' tiene errores gramaticales.")
        else:
            print(f"\n[OK] Archivo '{archivo_ruta}' cargado correctamente.")
            print("-" * 30)
            
            # --- PASO 3: EJECUCIÓN CON VISITOR ---
            # El visitor calculará e imprimirá los resultados [cite: 25, 75]
            visitor = Visitor()
            visitor.visit(tree)
            
            print("-" * 30)
            print("Ejecución finalizada con éxito.")
            print(f"Estado de la memoria: {visitor.memoria}")

    except Exception as e:
        print(f"Error al procesar el archivo: {e}")

if __name__ == '__main__':
    main()