class Simbolo:
    """Representa un símbolo en la tabla"""
    def __init__(self, nombre, tipo, linea, es_arreglo=False, tamanio=0, inicializada=False):
        self.nombre = nombre
        self.tipo = tipo  # Tipo base: 'int', 'float', 'String', etc.
        self.tipo_completo = tipo + '[]' if es_arreglo else tipo  # 'int[]' o 'int'
        self.linea = linea
        self.es_arreglo = es_arreglo
        self.tamanio = tamanio
        self.inicializada = inicializada

    def __repr__(self):
        arr = f"[{self.tamanio}]" if self.es_arreglo else ""
        return f"Simbolo({self.tipo}{arr} {self.nombre}, linea {self.linea})"


class Alcance:
    """Representa un alcance (scope) en la tabla de símbolos"""
    def __init__(self, nombre="global", padre=None):
        self.nombre = nombre
        self.padre = padre
        self.simbolos = {}

    def declarar(self, simbolo):
        """Declara un símbolo en este alcance"""
        self.simbolos[simbolo.nombre] = simbolo

    def buscar_local(self, nombre):
        """Busca un símbolo solo en este alcance"""
        return self.simbolos.get(nombre)

    def buscar(self, nombre):
        """Busca un símbolo en este alcance y sus padres"""
        if nombre in self.simbolos:
            return self.simbolos[nombre]
        if self.padre:
            return self.padre.buscar(nombre)
        return None


class TablaSimbolos:
    """Gestiona la tabla de símbolos con múltiples alcances"""
    def __init__(self):
        self.alcance_global = Alcance("global")
        self.alcance_actual = self.alcance_global
        self.errores = []

    def entrar_alcance(self, nombre="bloque"):
        """Crea un nuevo alcance"""
        nuevo = Alcance(nombre, self.alcance_actual)
        self.alcance_actual = nuevo

    def salir_alcance(self):
        """Sale del alcance actual"""
        if self.alcance_actual.padre:
            self.alcance_actual = self.alcance_actual.padre

    def declarar_variable(self, nombre, tipo, linea):
        """Declara una variable en el alcance actual"""
        existente = self.alcance_actual.buscar_local(nombre)
        if existente:
            self.errores.append(f"Error semántico en línea {linea}: Variable '{nombre}' ya declarada en línea {existente.linea}")
            return None
        simbolo = Simbolo(nombre, tipo, linea, es_arreglo=False)
        self.alcance_actual.declarar(simbolo)
        return simbolo

    def declarar_arreglo(self, nombre, tipo_base, tamanio, linea):
        """Declara un arreglo en el alcance actual"""
        existente = self.alcance_actual.buscar_local(nombre)
        if existente:
            self.errores.append(f"Error semántico en línea {linea}: Variable '{nombre}' ya declarada en línea {existente.linea}")
            return None
        simbolo = Simbolo(nombre, tipo_base, linea, es_arreglo=True, tamanio=tamanio)
        self.alcance_actual.declarar(simbolo)
        return simbolo

    def buscar_variable(self, nombre, linea):
        """Busca una variable y reporta error si no existe"""
        # Ignorar System.out.println
        if nombre.startswith("System.out"):
            return Simbolo(nombre, "void", linea)
        
        simbolo = self.alcance_actual.buscar(nombre)
        if not simbolo:
            self.errores.append(f"Error semántico en línea {linea}: Variable '{nombre}' no declarada")
            return None
        return simbolo

    def marcar_inicializada(self, nombre):
        """Marca una variable como inicializada"""
        simbolo = self.alcance_actual.buscar(nombre)
        if simbolo:
            simbolo.inicializada = True

    def obtener_tipo_elemento_arreglo(self, nombre, linea):
        """Obtiene el tipo base de un elemento de arreglo (para acceso con índice)"""
        simbolo = self.alcance_actual.buscar(nombre)
        if not simbolo:
            self.errores.append(f"Error semántico en línea {linea}: Variable '{nombre}' no declarada")
            return None
        if not simbolo.es_arreglo:
            self.errores.append(f"Error semántico en línea {linea}: '{nombre}' no es un arreglo")
            return None
        # Retornar el tipo base (int, float, etc.), no int[]
        return simbolo.tipo

    def verificar_compatibilidad_tipos(self, tipo1, tipo2, linea):
        """Verifica si dos tipos son compatibles para asignación"""
        if tipo1 is None or tipo2 is None:
            return True  # No verificar si hay errores previos
        
        # Normalizar tipos
        t1 = self._normalizar_tipo(tipo1)
        t2 = self._normalizar_tipo(tipo2)
        
        # Tipos iguales son compatibles
        if t1 == t2:
            return True
        
        # int y float son compatibles (promoción numérica)
        if {t1, t2} <= {'int', 'float'}:
            return True
        
        # null es compatible con tipos de referencia (String, arreglos)
        if t2 == 'null' and t1 in ('string', 'String'):
            return True
        
        # String solo es compatible con String
        if t1 in ('string', 'String') and t2 not in ('string', 'String', 'null'):
            self.errores.append(f"Error semántico en línea {linea}: No se puede asignar '{tipo2}' a variable de tipo '{tipo1}'")
            return False
        
        # int/float no son compatibles con String
        if t1 in ('int', 'float') and t2 in ('string', 'String'):
            self.errores.append(f"Error semántico en línea {linea}: No se puede asignar '{tipo2}' a variable de tipo '{tipo1}'")
            return False
        
        # char solo es compatible con char o int (código ASCII)
        if t1 == 'char' and t2 not in ('char', 'int'):
            self.errores.append(f"Error semántico en línea {linea}: No se puede asignar '{tipo2}' a variable de tipo '{tipo1}'")
            return False
        
        # boolean solo es compatible con boolean
        if t1 == 'boolean' and t2 != 'boolean':
            self.errores.append(f"Error semántico en línea {linea}: No se puede asignar '{tipo2}' a variable de tipo '{tipo1}'")
            return False
        
        if t2 == 'boolean' and t1 != 'boolean':
            self.errores.append(f"Error semántico en línea {linea}: No se puede asignar '{tipo2}' a variable de tipo '{tipo1}'")
            return False
        
        # Si llegamos aquí, son tipos incompatibles
        if t1 != t2:
            self.errores.append(f"Error semántico en línea {linea}: Tipos incompatibles: '{tipo1}' y '{tipo2}'")
            return False
        
        return True

    def _normalizar_tipo(self, tipo):
        """Normaliza un tipo para comparación"""
        if tipo is None:
            return None
        tipo_str = str(tipo)
        # Quitar [] para comparación de elementos
        if tipo_str.endswith('[]'):
            return tipo_str[:-2].lower()
        # Normalizar String/string
        if tipo_str.lower() == 'string':
            return 'string'
        return tipo_str.lower()

    def obtener_tipo_expresion_binaria(self, tipo_izq, operador, tipo_der, linea):
        """Determina el tipo resultante de una expresión binaria"""
        if tipo_izq is None or tipo_der is None:
            return None
        
        # Normalizar tipos (quitar [] si es acceso a elemento)
        t_izq = self._normalizar_tipo(tipo_izq)
        t_der = self._normalizar_tipo(tipo_der)
        
        # Operadores de comparación: resultado es boolean
        if operador in ('<', '>', '<=', '>=', '==', '!='):
            # Verificar que los operandos sean comparables
            if t_izq in ('int', 'float') and t_der in ('int', 'float'):
                return 'boolean'
            if t_izq == t_der:
                return 'boolean'
            if operador in ('==', '!='):
                # == y != pueden comparar cualquier cosa del mismo tipo
                if t_izq == t_der:
                    return 'boolean'
                # Comparar String con String
                if t_izq in ('string', 'String') and t_der in ('string', 'String'):
                    return 'boolean'
                # Comparar con null
                if t_izq == 'null' or t_der == 'null':
                    return 'boolean'
            # Comparaciones inválidas
            if t_izq in ('string', 'String') or t_der in ('string', 'String'):
                if operador in ('<', '>', '<=', '>='):
                    self.errores.append(f"Error semántico en línea {linea}: No se puede usar '{operador}' con String")
                    return 'boolean'
            self.errores.append(f"Error semántico en línea {linea}: Operador '{operador}' no aplicable a tipos '{tipo_izq}' y '{tipo_der}'")
            return 'boolean'
        
        # Operadores lógicos: requieren boolean
        if operador in ('&&', '||'):
            if t_izq != 'boolean':
                self.errores.append(f"Error semántico en línea {linea}: Operador '{operador}' requiere operando boolean, se encontró '{tipo_izq}'")
            if t_der != 'boolean':
                self.errores.append(f"Error semántico en línea {linea}: Operador '{operador}' requiere operando boolean, se encontró '{tipo_der}'")
            return 'boolean'
        
        # Operadores aritméticos
        if operador in ('+', '-', '*', '/', '%'):
            # Concatenación de strings con +
            if operador == '+':
                if t_izq in ('string', 'String') or t_der in ('string', 'String'):
                    return 'String'
            
            # Operaciones numéricas
            if t_izq in ('int', 'float') and t_der in ('int', 'float'):
                # Si alguno es float, el resultado es float
                if t_izq == 'float' or t_der == 'float':
                    return 'float'
                return 'int'
            
            # Operaciones aritméticas inválidas
            if t_izq in ('string', 'String') and operador != '+':
                self.errores.append(f"Error semántico en línea {linea}: No se puede usar '{operador}' con String")
                return None
            if t_der in ('string', 'String') and operador != '+':
                self.errores.append(f"Error semántico en línea {linea}: No se puede usar '{operador}' con String")
                return None
            if t_izq == 'boolean' or t_der == 'boolean':
                self.errores.append(f"Error semántico en línea {linea}: No se puede usar '{operador}' con boolean")
                return None
                
            self.errores.append(f"Error semántico en línea {linea}: Operador '{operador}' no aplicable a tipos '{tipo_izq}' y '{tipo_der}'")
            return None
        
        return None