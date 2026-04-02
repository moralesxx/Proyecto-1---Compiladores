class Simbolo:
    def __init__(self, nombre, tipo, valor=None):
        self.nombre = nombre
        self.tipo = tipo
        self.valor = valor

class SymbolTable:
    def __init__(self):
        # La pila de ámbitos: una lista de diccionarios (Tablas Hash)
        # El índice 0 siempre será el ámbito global
        self.stack = [{}]

    def push_scope(self):
        """Crea un nuevo ámbito (ej. al entrar a una función o ciclo)"""
        self.stack.append({})

    def pop_scope(self):
        """Elimina el ámbito actual (al salir de una función o ciclo)"""
        if len(self.stack) > 1:
            self.stack.pop()

    def declarar(self, nombre, tipo, valor=None):
        """
        Declara una variable en el ámbito actual.
        Lanza error si ya existe en el MISMO ámbito.
        """
        ambito_actual = self.stack[-1]
        if nombre in ambito_actual:
            return False, f"Error Semántico: La variable '{nombre}' ya ha sido declarada en este ámbito."
        
        ambito_actual[nombre] = Simbolo(nombre, tipo, valor)
        return True, None

    def asignar(self, nombre, valor):
        """
        Busca una variable desde el ámbito más interno hacia el global y la actualiza.
        """
        for i in range(len(self.stack) - 1, -1, -1):
            if nombre in self.stack[i]:
                self.stack[i][nombre].valor = valor
                return True
        return False

    def obtener(self, nombre):
        """
        Busca una variable y retorna su objeto Simbolo.
        """
        for i in range(len(self.stack) - 1, -1, -1):
            if nombre in self.stack[i]:
                return self.stack[i][nombre]
        return None

    def existe_en_ambito_actual(self, nombre):
        """Útil para validaciones de redeclaración rápida"""
        return nombre in self.stack[-1]