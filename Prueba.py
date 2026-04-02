import sys
import tkinter as tk
from tkinter import filedialog
from antlr4 import *
from ExpresionesLexer import ExpresionesLexer
from ExpresionesParser import ExpresionesParser
from Visitor import Visitor
# IMPORTAMOS TU CLASE NUEVA
from ManejadorErrores import MyErrorListener

def seleccionar_archivo():
    root = tk.Tk()
    root.withdraw()
    ruta = filedialog.askopenfilename(title="Seleccionar código fuente", filetypes=(("Texto", "*.txt"),))
    root.destroy()
    return ruta

def main():
    ruta = seleccionar_archivo()
    if not ruta: return
    try:
        input_stream = FileStream(ruta, encoding='utf-8')
        
        # --- CONFIGURACIÓN DEL LEXER ---
        lexer = ExpresionesLexer(input_stream)
        # Quitamos el manejador por defecto y ponemos el tuyo
        lexer.removeErrorListeners()
        lexer.addErrorListener(MyErrorListener())
        
        stream = CommonTokenStream(lexer)
        
        # --- CONFIGURACIÓN DEL PARSER ---
        parser = ExpresionesParser(stream)
        # Quitamos el manejador por defecto y ponemos el tuyo
        parser.removeErrorListeners()
        parser.addErrorListener(MyErrorListener())
        
        tree = parser.root()

        if parser.getNumberOfSyntaxErrors() > 0:
            print("\n[ERROR] Se detectaron errores sintácticos. Revisa los detalles arriba.")
        else:
            v = Visitor()
            v.visit(tree)
            print("\n--- TABLA DE SÍMBOLOS FINAL ---")
            print(f"{'ID':<15} | {'Tipo':<10} | {'Valor':<10}")
            print("-" * 40)
            for n, s in v.tabla_simbolos.items():
                print(f"{n:<15} | {s.tipo:<10} | {s.valor}")
                
    except Exception as e:
        print(f"Error durante la ejecución: {e}")

if __name__ == '__main__':
    main()