import sys
from antlr4 import *
from ExpresionesLexer import ExpresionesLexer
from ExpresionesParser import ExpresionesParser
from custom_errors import MyErrorListener
from semantic_visitor import SemanticVisitor
from interpreter_visitor import InterpreterVisitor

def run_pipeline(archivo_entrada):
    print(f"--- INICIANDO PIPELINE PARA: {archivo_entrada} ---")
    
    try:
        # 1. Leer código fuente
        input_stream = FileStream(archivo_entrada, encoding='utf-8')
        
        # 2. Fase Léxica (Scanner)
        lexer = ExpresionesLexer(input_stream)
        lexer_errors = MyErrorListener()
        lexer.removeErrorListeners()
        lexer.addErrorListener(lexer_errors)
        
        # 3. Fase Sintáctica (Parser)
        token_stream = CommonTokenStream(lexer)
        parser = ExpresionesParser(token_stream)
        parser_errors = MyErrorListener()
        parser.removeErrorListeners()
        parser.addErrorListener(parser_errors)
        
        tree = parser.root()
        
        # Validación de Parada (Fase 1 y 2)
        if lexer_errors.has_errors() or parser_errors.has_errors():
            print("\n[STOP] Errores detectados en fase inicial:")
            lexer_errors.imprimir_errores()
            parser_errors.imprimir_errores()
            return

        # 4. Fase Semántica (Type Checking y Scopes)
        print("Analizando semántica...")
        semantic_checker = SemanticVisitor()
        semantic_checker.visit(tree)
        
        if semantic_checker.errores:
            print("\n[STOP] Errores Semánticos detectados:")
            for err in semantic_checker.errores:
                print(err)
            return

        # 5. Fase de Ejecución (Interpreter)
        print("Ejecutando programa...\n" + "-"*20)
        interpreter = InterpreterVisitor()
        interpreter.visit(tree)
        print("-" * 20 + "\nEjecución finalizada con éxito.")

    except Exception as e:
        print(f"Error crítico del sistema: {e}")

if __name__ == "__main__":
    # Puedes pasar el nombre del archivo por consola o dejar uno por defecto
    archivo = sys.argv[1] if len(sys.argv) > 1 else "entrada.txt"
    run_pipeline(archivo)