from antlr4.error.ErrorListener import ErrorListener

class MyErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        print("\n" + "!"*30)
        print(f"ERROR SINTÁCTICO DETECTADO")
        print(f"Línea: {line} | Columna: {column}")
        print(f"Mensaje: {msg}")
        print("!"*30 + "\n")
