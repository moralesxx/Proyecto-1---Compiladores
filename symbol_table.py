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

    # ── FIX: Método requerido por interpreter_visitor para arreglos ──
    def declarar_array(self, nombre, tipo, valor=None):
        """
        Registra la declaración de un arreglo en el ámbito actual.
        Reutiliza la lógica de declaración estándar de forma segura.
        """
        return self.declarar(nombre, tipo, valor)

    def asignar(self, nombre, valor):
        """
        Busca una variable desde el ámbito más interno hacia el global y la actualiza.
        """
        for i in range(len(self.stack) - 1, -1, -1):
            if nombre in self.stack[i]:
                self.stack[i][nombre].valor = valor
                return True, None
        return False, f"Error Semántico: La variable '{nombre}' no ha sido declarada."

    def obtener(self, nombre):
        """
        Busca y retorna el objeto Simbolo desde el ámbito más interno al global.
        Retorna None si no existe.
        """
        for i in range(len(self.stack) - 1, -1, -1):
            if nombre in self.stack[i]:
                return self.stack[i][nombre]
        return None

    # ── Métodos para manejo de Arreglos (Asignación y Acceso por índice) ──

    def asignar_array(self, nombre, indice, valor):
        """Modifica el elemento en la posición 'indice' del arreglo."""
        simbolo = self.obtener(nombre)
        if simbolo is None:
            return False, f"Variable '{nombre}' no declarada."
        if not isinstance(simbolo.valor, list):
            return False, f"'{nombre}' no es un arreglo."
        try:
            simbolo.valor[indice] = valor
            return True, None
        except IndexError:
            return False, f"Índice {indice} fuera de rango para el arreglo '{nombre}'."

    def obtener_array(self, nombre, indice):
        """Retorna el elemento en la posición 'indice' del arreglo."""
        simbolo = self.obtener(nombre)
        if simbolo is None:
            print(f"[Error] Variable '{nombre}' no declarada.")
            return None
        if not isinstance(simbolo.valor, list):
            print(f"[Error] '{nombre}' no es un arreglo.")
            return None
        try:
            return simbolo.valor[indice]
        except IndexError:
            print(f"[Error] Índice {indice} fuera de rango para el arreglo '{nombre}'.")
            return None

    # ── Métodos para manejo de Structs (Fase 4 - v4) ──

    def __init_struct_registry(self):
        """Asegura la existencia del diccionario global de definiciones de structs en la raíz."""
        if not hasattr(self, '_structs'):
            self._structs = {}

    def registrar_struct(self, nombre_tipo, campos_dict):
        """
        Registra la definición estructural de un nuevo tipo Struct.
        campos_dict: {'x': 'int', 'y': 'int'}
        """
        self.__init_struct_registry()
        if nombre_tipo in self._structs:
            return False, f"Tipo struct '{nombre_tipo}' ya definido."
        self._structs[nombre_tipo] = campos_dict
        return True, None

    def obtener_struct_def(self, nombre_tipo):
        """Retorna el diccionario de campos de un struct o None si no existe."""
        self.__init_struct_registry()
        return self._structs.get(nombre_tipo)

    def declarar_instancia_struct(self, nombre_var, nombre_tipo):
        """
        Declara una variable cuyo tipo es un struct registrado.
        Inicializa todos sus campos a None.
        """
        self.__init_struct_registry()
        definicion = self._structs.get(nombre_tipo)
        if definicion is None:
            return False, f"Tipo struct '{nombre_tipo}' no definido."
        valor_inicial = {campo: None for campo in definicion}
        # ── FIX QUIRÚRGICO REALIZADO AQUÍ: Corrección de comillas en el string literal ──
        return self.declarar(nombre_var, f"struct:{nombre_tipo}", valor_inicial)

    def asignar_campo(self, nombre_var, campo, valor):
        """
        Asigna valor a un campo de una instancia de struct.
        Ej: p.x = 10  →  asignar_campo('p', 'x', 10)
        """
        simbolo = self.obtener(nombre_var)
        if simbolo is None:
            return False, f"Variable '{nombre_var}' no declarada."
        if not isinstance(simbolo.valor, dict):
            return False, f"'{nombre_var}' no es una instancia de struct."
        simbolo.valor[campo] = valor
        return True, None

    def obtener_campo(self, nombre_var, campo):
        """
        Retorna el valor de un campo de una instancia de struct.
        Ej: p.x  →  obtener_campo('p', 'x')
        """
        simbolo = self.obtener(nombre_var)
        if simbolo is None:
            print(f"[Error] Variable '{nombre_var}' no declarada.")
            return None
        if not isinstance(simbolo.valor, dict):
            print(f"[Error] '{nombre_var}' no es una instancia de struct.")
            return None
        return simbolo.valor.get(campo)