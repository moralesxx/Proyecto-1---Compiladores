from antlr4.error.ErrorListener import ErrorListener

class MyErrorListener(ErrorListener):
    def __init__(self):
        super(MyErrorListener, self).__init__()
        self.errores = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        # Determinar si es un error léxico o sintáctico basado en el mensaje o el símbolo
        tipo = "Sintáctico"
        if "token recognition error" in msg or offendingSymbol is None:
            tipo = "Léxico"
            
        formato_error = f"[{tipo}] Línea {line}, Columna {column}: {msg}"
        self.errores.append(formato_error)

    def has_errors(self):
        return len(self.errores) > 0

    def imprimir_errores(self):
        for err in self.errores:
            print(err)