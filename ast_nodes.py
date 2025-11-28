class NodoAST:
    """Clase base para todos los nodos del AST"""
    pass


# ============== PROGRAMA Y DECLARACIONES ==============

class Programa(NodoAST):
    """Nodo raíz que contiene todo el programa"""
    def __init__(self, declaraciones):
        self.declaraciones = declaraciones  # Lista de declaraciones
    
    def __repr__(self):
        return f"Programa({len(self.declaraciones)} declaraciones)"


class DeclaracionClase(NodoAST):
    """Declaración de una clase"""
    def __init__(self, nombre, miembros):
        self.nombre = nombre
        self.miembros = miembros  # Lista de métodos y atributos
    
    def __repr__(self):
        return f"Clase({self.nombre})"


class DeclaracionMetodo(NodoAST):
    """Declaración de un método"""
    def __init__(self, tipo_retorno, nombre, parametros, cuerpo):
        self.tipo_retorno = tipo_retorno
        self.nombre = nombre
        self.parametros = parametros  # Lista de parámetros
        self.cuerpo = cuerpo  # Bloque de código
    
    def __repr__(self):
        return f"Metodo({self.tipo_retorno} {self.nombre})"


class Parametro(NodoAST):
    """Parámetro de un método"""
    def __init__(self, tipo, nombre):
        self.tipo = tipo
        self.nombre = nombre
    
    def __repr__(self):
        return f"Parametro({self.tipo} {self.nombre})"


class DeclaracionVariable(NodoAST):
    """Declaración de una variable (incluye arreglos)"""
    def __init__(self, tipo, nombre, inicializador=None):
        self.tipo = tipo          # p.ej. 'int', 'int[]'
        self.nombre = nombre
        self.inicializador = inicializador  # Expresión o lista de expresiones
    
    def __repr__(self):
        return f"DeclVar({self.tipo} {self.nombre})"


# ============== SENTENCIAS ==============

class Bloque(NodoAST):
    """Bloque de sentencias entre llaves"""
    def __init__(self, sentencias):
        self.sentencias = sentencias
    
    def __repr__(self):
        return f"Bloque({len(self.sentencias)} sentencias)"


class SentenciaIf(NodoAST):
    """Sentencia condicional if/else"""
    def __init__(self, condicion, bloque_if, bloque_else=None):
        self.condicion = condicion
        self.bloque_if = bloque_if
        self.bloque_else = bloque_else
    
    def __repr__(self):
        return "If"


class SentenciaWhile(NodoAST):
    """Sentencia de bucle while"""
    def __init__(self, condicion, cuerpo):
        self.condicion = condicion
        self.cuerpo = cuerpo
    
    def __repr__(self):
        return "While"


class SentenciaDoWhile(NodoAST):
    """Sentencia de bucle do-while"""
    def __init__(self, cuerpo, condicion):
        self.cuerpo = cuerpo
        self.condicion = condicion
    
    def __repr__(self):
        return "DoWhile"


class SentenciaFor(NodoAST):
    """Sentencia de bucle for"""
    def __init__(self, inicializacion, condicion, incremento, cuerpo):
        self.inicializacion = inicializacion
        self.condicion = condicion
        self.incremento = incremento
        self.cuerpo = cuerpo
    
    def __repr__(self):
        return "For"


class SentenciaReturn(NodoAST):
    """Sentencia de retorno"""
    def __init__(self, expresion=None):
        self.expresion = expresion
    
    def __repr__(self):
        return "Return"


class SentenciaExpresion(NodoAST):
    """Sentencia que contiene una expresión"""
    def __init__(self, expresion):
        self.expresion = expresion
    
    def __repr__(self):
        return "SentenciaExpresion"


# ============== EXPRESIONES ==============

class Asignacion(NodoAST):
    """Expresión de asignación: x = expr"""
    def __init__(self, nombre, valor):
        self.nombre = nombre
        self.valor = valor
    
    def __repr__(self):
        return f"Asignacion({self.nombre})"


class AsignacionIndice(NodoAST):
    """Asignación a un elemento de arreglo: arreglo[indice] = valor"""
    def __init__(self, arreglo, indice, valor):
        self.arreglo = arreglo   # Expresión que representa el arreglo (Identificador o algo más)
        self.indice = indice     # Expresión del índice
        self.valor = valor       # Expresión del valor asignado

    def __repr__(self):
        return "AsignacionIndice"


class ExpresionBinaria(NodoAST):
    """Expresión binaria (operador con dos operandos)"""
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha
    
    def __repr__(self):
        return f"ExpBinaria({self.operador})"


class ExpresionUnaria(NodoAST):
    """Expresión unaria (operador con un operando)"""
    def __init__(self, operador, operando):
        self.operador = operador
        self.operando = operando
    
    def __repr__(self):
        return f"ExpUnaria({self.operador})"


class ExpresionLlamada(NodoAST):
    """Llamada a función o método"""
    def __init__(self, nombre, argumentos):
        self.nombre = nombre
        self.argumentos = argumentos
    
    def __repr__(self):
        return f"Llamada({self.nombre})"


class ExpresionAcceso(NodoAST):
    """Acceso a miembro (obj.campo)"""
    def __init__(self, objeto, miembro):
        self.objeto = objeto
        self.miembro = miembro
    
    def __repr__(self):
        return f"Acceso({self.miembro})"


class ExpresionIndice(NodoAST):
    """Acceso a índice de arreglo: arreglo[expr]"""
    def __init__(self, arreglo, indice):
        self.arreglo = arreglo
        self.indice = indice
    
    def __repr__(self):
        return "AccesoIndice"


# ============== LITERALES E IDENTIFICADORES ==============

class Literal(NodoAST):
    """Literal (valor constante)"""
    def __init__(self, valor, tipo):
        self.valor = valor
        self.tipo = tipo  # 'int', 'float', 'string', 'boolean', 'char'
    
    def __repr__(self):
        return f"Literal({self.tipo}: {self.valor})"


class Identificador(NodoAST):
    """Identificador (nombre de variable)"""
    def __init__(self, nombre):
        self.nombre = nombre
    
    def __repr__(self):
        return f"Id({self.nombre})"


class ExpresionAgrupada(NodoAST):
    """Expresión entre paréntesis"""
    def __init__(self, expresion):
        self.expresion = expresion
    
    def __repr__(self):
        return "Agrupada"


# ============== UTILIDADES ==============

def imprimir_ast(nodo, nivel=0, prefijo=""):
    """Imprime el AST de forma jerárquica"""
    indent = "  " * nivel
    
    if nodo is None:
        return f"{indent}{prefijo}None\n"
    
    resultado = f"{indent}{prefijo}{nodo.__class__.__name__}"
    
    # Agregar información específica según el tipo de nodo
    if isinstance(nodo, Literal):
        resultado += f" ({nodo.tipo}: {nodo.valor})"
    elif isinstance(nodo, Identificador):
        resultado += f" ({nodo.nombre})"
    elif isinstance(nodo, DeclaracionVariable):
        resultado += f" ({nodo.tipo} {nodo.nombre})"
    elif isinstance(nodo, ExpresionBinaria):
        resultado += f" ({nodo.operador})"
    elif isinstance(nodo, ExpresionUnaria):
        resultado += f" ({nodo.operador})"
    elif isinstance(nodo, Asignacion):
        resultado += f" ({nodo.nombre})"
    
    resultado += "\n"
    
    # Recursivamente imprimir hijos
    if isinstance(nodo, Programa):
        for decl in nodo.declaraciones:
            resultado += imprimir_ast(decl, nivel + 1, "├─ ")
    
    elif isinstance(nodo, DeclaracionVariable):
        if nodo.inicializador:
            resultado += imprimir_ast(nodo.inicializador, nivel + 1, "└─ = ")
    
    elif isinstance(nodo, Bloque):
        for sent in nodo.sentencias:
            resultado += imprimir_ast(sent, nivel + 1, "├─ ")
    
    elif isinstance(nodo, SentenciaIf):
        resultado += imprimir_ast(nodo.condicion, nivel + 1, "├─ Cond: ")
        resultado += imprimir_ast(nodo.bloque_if, nivel + 1, "├─ Then: ")
        if nodo.bloque_else:
            resultado += imprimir_ast(nodo.bloque_else, nivel + 1, "└─ Else: ")
    
    elif isinstance(nodo, (SentenciaWhile, SentenciaDoWhile)):
        resultado += imprimir_ast(nodo.condicion, nivel + 1, "├─ Cond: ")
        resultado += imprimir_ast(nodo.cuerpo, nivel + 1, "└─ Cuerpo: ")
    
    elif isinstance(nodo, SentenciaFor):
        if nodo.inicializacion:
            resultado += imprimir_ast(nodo.inicializacion, nivel + 1, "├─ Init: ")
        if nodo.condicion:
            resultado += imprimir_ast(nodo.condicion, nivel + 1, "├─ Cond: ")
        if nodo.incremento:
            resultado += imprimir_ast(nodo.incremento, nivel + 1, "├─ Inc: ")
        resultado += imprimir_ast(nodo.cuerpo, nivel + 1, "└─ Cuerpo: ")
    
    elif isinstance(nodo, SentenciaReturn):
        if nodo.expresion:
            resultado += imprimir_ast(nodo.expresion, nivel + 1, "└─ ")
    
    elif isinstance(nodo, SentenciaExpresion):
        resultado += imprimir_ast(nodo.expresion, nivel + 1, "└─ ")
    
    elif isinstance(nodo, Asignacion):
        resultado += imprimir_ast(nodo.valor, nivel + 1, "└─ ")
    
    elif isinstance(nodo, AsignacionIndice):
        resultado += imprimir_ast(nodo.arreglo, nivel + 1, "├─ Arr: ")
        resultado += imprimir_ast(nodo.indice, nivel + 1, "├─ Idx: ")
        resultado += imprimir_ast(nodo.valor, nivel + 1, "└─ Val: ")
    
    elif isinstance(nodo, ExpresionBinaria):
        resultado += imprimir_ast(nodo.izquierda, nivel + 1, "├─ Izq: ")
        resultado += imprimir_ast(nodo.derecha, nivel + 1, "└─ Der: ")
    
    elif isinstance(nodo, ExpresionUnaria):
        resultado += imprimir_ast(nodo.operando, nivel + 1, "└─ ")
    
    elif isinstance(nodo, ExpresionLlamada):
        if nodo.argumentos:
            for arg in nodo.argumentos:
                resultado += imprimir_ast(arg, nivel + 1, "├─ Arg: ")
    
    elif isinstance(nodo, ExpresionAgrupada):
        resultado += imprimir_ast(nodo.expresion, nivel + 1, "└─ ")
    
    elif isinstance(nodo, ExpresionIndice):
        resultado += imprimir_ast(nodo.arreglo, nivel + 1, "├─ Arr: ")
        resultado += imprimir_ast(nodo.indice, nivel + 1, "└─ Idx: ")
    
    return resultado