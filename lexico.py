import re
from enum import Enum, auto

class TipoToken(Enum):
    """Tipos de tokens reconocidos por el analizador léxico"""
    # Palabras clave (prefijo KW_ para diferenciar)
    KW_CLASS = auto()
    PUBLIC = auto()
    PRIVATE = auto()
    STATIC = auto()
    VOID = auto()
    NEW = auto()
    THIS = auto()
    TRUE = auto()
    FALSE = auto()
    NULL = auto()

    # Tipos de datos
    INT = auto()
    FLOAT = auto()
    BOOLEAN = auto()
    STRING = auto()
    CHAR = auto()
    
    # Palabras clave de control
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    DO = auto()
    FOR = auto()
    RETURN = auto()
    BREAK = auto()
    CONTINUE = auto()
    
    # Operadores (asignación y aritméticos)
    ASIGNACION = auto()   # =
    MAS = auto()          # +
    MENOS = auto()        # -
    MULTIPLICACION = auto()
    DIVISION = auto()
    MODULO = auto()
    INCREMENTO = auto()   # ++
    DECREMENTO = auto()   # --
    MAS_IGUAL = auto()    # +=
    MENOS_IGUAL = auto()  # -=
    
    # Comparadores
    IGUAL_IGUAL = auto()
    DIFERENTE = auto()
    MAYOR = auto()
    MENOR = auto()
    MAYOR_IGUAL = auto()
    MENOR_IGUAL = auto()
    
    # Lógicos
    AND = auto()
    OR = auto()
    NOT = auto()
    
    # Delimitadores
    PARENTESIS_IZQ = auto()
    PARENTESIS_DER = auto()
    LLAVE_IZQ = auto()
    LLAVE_DER = auto()
    CORCHETE_IZQ = auto()
    CORCHETE_DER = auto()
    PUNTO_COMA = auto()
    COMA = auto()
    PUNTO = auto()
    
    # Especiales / literales
    IDENTIFICADOR = auto()
    NUMERO_ENTERO = auto()
    NUMERO_FLOTANTE = auto()
    CADENA = auto()
    CARACTER = auto()
    COMENTARIO = auto()
    EOF = auto()
    ERROR = auto()
    CLASS = auto()   # <-- agregar este miembro si falta


class Token:
    """Representa un token individual"""
    def __init__(self, tipo, valor, linea, columna):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.columna = columna
    
    def __repr__(self):
        return f"Token({self.tipo.name}, '{self.valor}', L{self.linea}:C{self.columna})"


class AnalizadorLexico:
    """Analizador Léxico (Scanner/Lexer)"""
    
    PALABRAS_RESERVADAS = {
        'class': TipoToken.KW_CLASS,
        'public': TipoToken.PUBLIC,
        'private': TipoToken.PRIVATE,
        'static': TipoToken.STATIC,
        'void': TipoToken.VOID,
        'int': TipoToken.INT,
        'float': TipoToken.FLOAT,
        'boolean': TipoToken.BOOLEAN,
        'String': TipoToken.STRING,
        'char': TipoToken.CHAR,
        'if': TipoToken.IF,
        'else': TipoToken.ELSE,
        'while': TipoToken.WHILE,
        'for': TipoToken.FOR,
        'do': TipoToken.DO,
        'return': TipoToken.RETURN,
        'new': TipoToken.NEW,
        'this': TipoToken.THIS,
        'true': TipoToken.TRUE,
        'false': TipoToken.FALSE,
        'null': TipoToken.NULL
    }
    
    def __init__(self):
        self.codigo = ""
        self.posicion = 0
        self.linea = 1
        self.columna = 1
        self.tokens = []
        self.errores = []
    
    def analizar(self, codigo):
        """Analiza el código fuente y retorna lista de tokens"""
        self.codigo = codigo
        self.posicion = 0
        self.linea = 1
        self.columna = 1
        self.tokens = []
        self.errores = []
        
        while self.posicion < len(self.codigo):
            self._saltar_espacios()
            
            if self.posicion >= len(self.codigo):
                break
            
            # Intentar reconocer comentarios
            if self._reconocer_comentario():
                continue
            
            # Intentar reconocer tokens
            if not (self._reconocer_numero() or
                    self._reconocer_cadena() or
                    self._reconocer_caracter() or
                    self._reconocer_identificador_o_palabra_reservada() or
                    self._reconocer_operador() or
                    self._reconocer_delimitador()):
                
                # Token no reconocido - error léxico
                caracter = self.codigo[self.posicion]
                self.errores.append(f"Error léxico en L{self.linea}:C{self.columna}: "
                                  f"Carácter no reconocido '{caracter}'")
                self.tokens.append(Token(TipoToken.ERROR, caracter, self.linea, self.columna))
                self._avanzar()
        
        # Agregar token EOF
        self.tokens.append(Token(TipoToken.EOF, '', self.linea, self.columna))
        return self.tokens
    
    def _caracter_actual(self):
        """Retorna el carácter actual sin avanzar"""
        if self.posicion < len(self.codigo):
            return self.codigo[self.posicion]
        return None
    
    def _siguiente_caracter(self):
        """Retorna el siguiente carácter sin avanzar"""
        if self.posicion + 1 < len(self.codigo):
            return self.codigo[self.posicion + 1]
        return None
    
    def _avanzar(self):
        """Avanza una posición en el código"""
        if self.posicion < len(self.codigo):
            if self.codigo[self.posicion] == '\n':
                self.linea += 1
                self.columna = 1
            else:
                self.columna += 1
            self.posicion += 1
    
    def _saltar_espacios(self):
        """Salta espacios en blanco, tabuladores y saltos de línea"""
        while self.posicion < len(self.codigo) and self.codigo[self.posicion] in ' \t\n\r':
            self._avanzar()
    
    def _reconocer_comentario(self):
        """Reconoce comentarios de línea (//) y de bloque (/* */)"""
        if self._caracter_actual() == '/' and self._siguiente_caracter() == '/':
            # Comentario de línea
            linea_inicio = self.linea
            col_inicio = self.columna
            comentario = ""
            
            while self._caracter_actual() and self._caracter_actual() != '\n':
                comentario += self._caracter_actual()
                self._avanzar()
            
            self.tokens.append(Token(TipoToken.COMENTARIO, comentario, linea_inicio, col_inicio))
            return True
        
        if self._caracter_actual() == '/' and self._siguiente_caracter() == '*':
            # Comentario de bloque
            linea_inicio = self.linea
            col_inicio = self.columna
            comentario = ""
            self._avanzar()  # /
            self._avanzar()  # *
            
            while self.posicion < len(self.codigo) - 1:
                if self._caracter_actual() == '*' and self._siguiente_caracter() == '/':
                    comentario += '*/'
                    self._avanzar()
                    self._avanzar()
                    break
                comentario += self._caracter_actual()
                self._avanzar()
            else:
                self.errores.append(f"Error léxico en L{linea_inicio}:C{col_inicio}: "
                                  f"Comentario de bloque sin cerrar")
            
            self.tokens.append(Token(TipoToken.COMENTARIO, comentario, linea_inicio, col_inicio))
            return True
        
        return False
    
    def _reconocer_numero(self):
        """Reconoce números enteros y flotantes"""
        if not self._caracter_actual().isdigit():
            return False
        
        linea_inicio = self.linea
        col_inicio = self.columna
        numero = ""
        es_flotante = False
        
        # Parte entera
        while self._caracter_actual() and self._caracter_actual().isdigit():
            numero += self._caracter_actual()
            self._avanzar()
        
        # Parte decimal
        if self._caracter_actual() == '.' and self._siguiente_caracter() and self._siguiente_caracter().isdigit():
            es_flotante = True
            numero += self._caracter_actual()
            self._avanzar()
            
            while self._caracter_actual() and self._caracter_actual().isdigit():
                numero += self._caracter_actual()
                self._avanzar()
        
        tipo = TipoToken.NUMERO_FLOTANTE if es_flotante else TipoToken.NUMERO_ENTERO
        self.tokens.append(Token(tipo, numero, linea_inicio, col_inicio))
        return True
    
    def _reconocer_cadena(self):
        """Reconoce cadenas de texto entre comillas dobles"""
        if self._caracter_actual() != '"':
            return False
        
        linea_inicio = self.linea
        col_inicio = self.columna
        cadena = ""
        self._avanzar()  # Saltar comilla inicial
        
        while self._caracter_actual() and self._caracter_actual() != '"':
            if self._caracter_actual() == '\\' and self._siguiente_caracter():
                # Manejar secuencias de escape
                cadena += self._caracter_actual()
                self._avanzar()
                cadena += self._caracter_actual()
                self._avanzar()
            else:
                cadena += self._caracter_actual()
                self._avanzar()
        
        if self._caracter_actual() == '"':
            self._avanzar()  # Saltar comilla final
            self.tokens.append(Token(TipoToken.CADENA, cadena, linea_inicio, col_inicio))
        else:
            self.errores.append(f"Error léxico en L{linea_inicio}:C{col_inicio}: "
                              f"Cadena sin cerrar")
            self.tokens.append(Token(TipoToken.ERROR, cadena, linea_inicio, col_inicio))
        
        return True
    
    def _reconocer_caracter(self):
        """Reconoce caracteres entre comillas simples"""
        if self._caracter_actual() != "'":
            return False
        
        linea_inicio = self.linea
        col_inicio = self.columna
        caracter = ""
        self._avanzar()  # Saltar comilla inicial
        
        if self._caracter_actual() and self._caracter_actual() != "'":
            caracter = self._caracter_actual()
            self._avanzar()
        
        if self._caracter_actual() == "'":
            self._avanzar()  # Saltar comilla final
            self.tokens.append(Token(TipoToken.CARACTER, caracter, linea_inicio, col_inicio))
        else:
            self.errores.append(f"Error léxico en L{linea_inicio}:C{col_inicio}: "
                              f"Carácter sin cerrar")
            self.tokens.append(Token(TipoToken.ERROR, caracter, linea_inicio, col_inicio))
        
        return True
    
    def _reconocer_identificador_o_palabra_reservada(self):
        """Reconoce identificadores y palabras reservadas"""
        if not (self._caracter_actual().isalpha() or self._caracter_actual() == '_'):
            return False
        
        linea_inicio = self.linea
        col_inicio = self.columna
        identificador = ""
        
        while (self._caracter_actual() and 
               (self._caracter_actual().isalnum() or self._caracter_actual() == '_')):
            identificador += self._caracter_actual()
            self._avanzar()
        
        # Verificar si es palabra reservada
        tipo = self.PALABRAS_RESERVADAS.get(identificador, TipoToken.IDENTIFICADOR)
        self.tokens.append(Token(tipo, identificador, linea_inicio, col_inicio))
        return True
    
    def _reconocer_operador(self):
        """Reconoce operadores"""
        linea_inicio = self.linea
        col_inicio = self.columna
        c = self._caracter_actual()
        sig = self._siguiente_caracter()
        
        # Operadores de dos caracteres
        if c == '+' and sig == '+':
            self.tokens.append(Token(TipoToken.INCREMENTO, '++', linea_inicio, col_inicio))
            self._avanzar()
            self._avanzar()
            return True
        elif c == '-' and sig == '-':
            self.tokens.append(Token(TipoToken.DECREMENTO, '--', linea_inicio, col_inicio))
            self._avanzar()
            self._avanzar()
            return True
        elif c == '+' and sig == '=':
            self.tokens.append(Token(TipoToken.MAS_IGUAL, '+=', linea_inicio, col_inicio))
            self._avanzar()
            self._avanzar()
            return True
        elif c == '-' and sig == '=':
            self.tokens.append(Token(TipoToken.MENOS_IGUAL, '-=', linea_inicio, col_inicio))
            self._avanzar()
            self._avanzar()
            return True
        elif c == '=' and sig == '=':
            self.tokens.append(Token(TipoToken.IGUAL_IGUAL, '==', linea_inicio, col_inicio))
            self._avanzar()
            self._avanzar()
            return True
        elif c == '!' and sig == '=':
            self.tokens.append(Token(TipoToken.DIFERENTE, '!=', linea_inicio, col_inicio))
            self._avanzar()
            self._avanzar()
            return True
        elif c == '<' and sig == '=':
            self.tokens.append(Token(TipoToken.MENOR_IGUAL, '<=', linea_inicio, col_inicio))
            self._avanzar()
            self._avanzar()
            return True
        elif c == '>' and sig == '=':
            self.tokens.append(Token(TipoToken.MAYOR_IGUAL, '>=', linea_inicio, col_inicio))
            self._avanzar()
            self._avanzar()
            return True
        elif c == '&' and sig == '&':
            self.tokens.append(Token(TipoToken.AND, '&&', linea_inicio, col_inicio))
            self._avanzar()
            self._avanzar()
            return True
        elif c == '|' and sig == '|':
            self.tokens.append(Token(TipoToken.OR, '||', linea_inicio, col_inicio))
            self._avanzar()
            self._avanzar()
            return True
        
        # Operadores de un carácter
        operadores_simples = {
            '+': TipoToken.MAS,
            '-': TipoToken.MENOS,
            '*': TipoToken.MULTIPLICACION,
            '/': TipoToken.DIVISION,
            '%': TipoToken.MODULO,
            '=': TipoToken.ASIGNACION,
            '<': TipoToken.MENOR,
            '>': TipoToken.MAYOR,
            '!': TipoToken.NOT
        }
        
        if c in operadores_simples:
            self.tokens.append(Token(operadores_simples[c], c, linea_inicio, col_inicio))
            self._avanzar()
            return True
        
        return False
    
    def _reconocer_delimitador(self):
        """Reconoce delimitadores"""
        linea_inicio = self.linea
        col_inicio = self.columna
        c = self._caracter_actual()
        
        delimitadores = {
            '(': TipoToken.PARENTESIS_IZQ,
            ')': TipoToken.PARENTESIS_DER,
            '{': TipoToken.LLAVE_IZQ,
            '}': TipoToken.LLAVE_DER,
            '[': TipoToken.CORCHETE_IZQ,
            ']': TipoToken.CORCHETE_DER,
            ';': TipoToken.PUNTO_COMA,
            ',': TipoToken.COMA,
            '.': TipoToken.PUNTO
        }
        
        if c in delimitadores:
            self.tokens.append(Token(delimitadores[c], c, linea_inicio, col_inicio))
            self._avanzar()
            return True
        
        return False
    
    def obtener_tabla_tokens(self):
        """Genera la tabla de tokens reconocidos"""
        resultado = '\n' + '='*70 + '\n'
        resultado += '📋 ANÁLISIS LÉXICO\n'
        resultado += '='*70 + '\n'
        resultado += f'{"Tipo":<20} {"Valor":<25} {"Línea":<10}\n'
        resultado += '-'*70 + '\n'
        
        for token in self.tokens:
            resultado += f'{str(token.tipo.name):<20} {str(token.valor):<25} {str(token.linea):<10}\n'
        
        resultado += '='*70 + '\n'
        resultado += f'Total de tokens: {len(self.tokens)}\n'
        resultado += '='*70 + '\n'
        
        # NO agregues errores aquí - solo la tabla de tokens
        return resultado