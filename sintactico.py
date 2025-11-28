from ast_nodes import *
from lexico import TipoToken

class AnalizadorSintactico:
    MAX_ITERACIONES = 10000  # Límite para evitar bucles infinitos

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errores = []
        self.ast = None
        self._errores_encontrados = False
        self._iteraciones = 0

    def _verificar_limite(self):
        """Verifica que no se exceda el límite de iteraciones"""
        self._iteraciones += 1
        if self._iteraciones > self.MAX_ITERACIONES:
            raise Exception("Límite de iteraciones excedido (posible bucle infinito)")

    def analizar(self):
        try:
            self.ast = self.programa()
        except Exception as e:
            self.errores.append(f"Error crítico: {str(e)}")
            self._errores_encontrados = True
        return not self._errores_encontrados

    def obtener_reporte(self):
        if self.errores:
            return '\n'.join(f'❌ {e}' for e in self.errores)
        return '✅ Sin errores sintácticos'

    # ========== PROGRAMA Y DECLARACIONES ==========
    def programa(self):
        declaraciones = []
        last_pos = -1
        while not self._es(TipoToken.EOF):
            self._verificar_limite()
            # Guardia anti-bucle: si no avanzamos, forzar avance
            if self.pos == last_pos:
                self._avanzar()
                continue
            last_pos = self.pos
            
            decl = self.declaracion()
            if decl:
                declaraciones.append(decl)
        return Programa(declaraciones)

    def declaracion(self):
        self._verificar_limite()
        # Declaración de variable/arreglo con tipo
        if self._es_tipo():
            return self.declaracion_variable()
        # Bloque
        if self._es(TipoToken.LLAVE_IZQ):
            return self.bloque()
        # Sentencias de control o expresiones
        return self.sentencia()

    def declaracion_variable(self):
        self._verificar_limite()
        if not self._actual():
            return None

        tipo = self._actual().valor
        self._avanzar()

        es_arreglo = False

        # Forma Java: int[] nombre ...
        if self._es(TipoToken.CORCHETE_IZQ):
            es_arreglo = True
            self._avanzar()
            if self._es(TipoToken.CORCHETE_DER):
                self._avanzar()
                tipo = tipo + "[]"
            else:
                self._error("Falta corchete de cierre ']' en declaración de arreglo.")
                return None

        if not self._es(TipoToken.IDENTIFICADOR):
            self._error("Se esperaba nombre de variable.")
            return None
        nombre = self._actual().valor
        self._avanzar()

        inicializador = None

        # Inicialización de arreglo por literal: int[] nums = [1,2,3];
        if es_arreglo and self._es(TipoToken.ASIGNACION):
            self._avanzar()
            if self._es(TipoToken.CORCHETE_IZQ):
                elementos = self.lista_expresiones_arreglo()
                inicializador = elementos
            else:
                self._error("Se esperaba literal de arreglo con '[' para inicializar.")
                return None
        # Inicialización estándar de variable simple: int a = 5;
        elif self._es(TipoToken.ASIGNACION):
            self._avanzar()
            inicializador = self.expresion()

        # Declaración de arreglo de tamaño fijo: int arreglo[10];
        if self._es(TipoToken.CORCHETE_IZQ):
            es_arreglo = True
            self._avanzar()
            if self._es(TipoToken.NUMERO_ENTERO):
                tam = self._actual().valor
                self._avanzar()
                if self._es(TipoToken.CORCHETE_DER):
                    self._avanzar()
                    inicializador = Literal(int(tam), 'int')
                else:
                    self._error("Falta corchete de cierre ']' en declaración de arreglo.")
                    return None
            else:
                self._error("Se esperaba número de tamaño en arreglo.")
                return None

        if self._es(TipoToken.PUNTO_COMA):
            self._avanzar()
            return DeclaracionVariable(tipo, nombre, inicializador)

        self._error("Falta punto y coma en declaración.")
        return None

    def lista_expresiones_arreglo(self):
        self._verificar_limite()
        self._avanzar()  # Consumir '['
        elementos = []
        while not self._es(TipoToken.CORCHETE_DER) and not self._es(TipoToken.EOF):
            self._verificar_limite()
            expr = self.expresion()
            elementos.append(expr)
            if self._es(TipoToken.COMA):
                self._avanzar()
            else:
                break
        if self._es(TipoToken.CORCHETE_DER):
            self._avanzar()
            return elementos
        else:
            self._error("Falta corchete de cierre en literal de arreglo.")
            return elementos

    # =========== BLOQUES Y SENTENCIAS ============
    def bloque(self):
        self._verificar_limite()
        if not self._es(TipoToken.LLAVE_IZQ):
            self._error("Se esperaba '{' para iniciar bloque.")
            return None
        self._avanzar()
        sentencias = []
        last_pos = -1
        while not self._es(TipoToken.LLAVE_DER) and not self._es(TipoToken.EOF):
            self._verificar_limite()
            # Guardia anti-bucle
            if self.pos == last_pos:
                self._avanzar()
                continue
            last_pos = self.pos
            
            stmt = self.declaracion()
            if stmt:
                sentencias.append(stmt)
        
        if self._es(TipoToken.LLAVE_DER):
            self._avanzar()
            return Bloque(sentencias)
        else:
            self._error("Falta llave de cierre '}' en bloque.")
            return Bloque(sentencias)  # Retornar lo que tenemos

    def sentencia(self):
        self._verificar_limite()
        if self._es(TipoToken.IF):
            return self.sentencia_if()
        if self._es(TipoToken.WHILE):
            return self.sentencia_while()
        if self._es(TipoToken.DO):
            return self.sentencia_do_while()
        if self._es(TipoToken.FOR):
            return self.sentencia_for()
        if self._es(TipoToken.RETURN):
            return self.sentencia_return()
        if self._es(TipoToken.LLAVE_IZQ):
            return self.bloque()
        return self.sentencia_expresion()

    def sentencia_if(self):
        self._verificar_limite()
        self._avanzar()  # Consumir 'if'
        if not self._es(TipoToken.PARENTESIS_IZQ):
            self._error("Falta paréntesis de apertura '(' en if.")
            return None
        self._avanzar()
        condicion = self.expresion()
        if not self._es(TipoToken.PARENTESIS_DER):
            self._error("Falta paréntesis de cierre ')' en if.")
        else:
            self._avanzar()
        
        bloque_if = self.bloque() if self._es(TipoToken.LLAVE_IZQ) else self._sentencia_simple()
        bloque_else = None
        if self._es(TipoToken.ELSE):
            self._avanzar()
            bloque_else = self.bloque() if self._es(TipoToken.LLAVE_IZQ) else self._sentencia_simple()
        return SentenciaIf(condicion, bloque_if, bloque_else)

    def _sentencia_simple(self):
        """Para sentencias sin llaves (if sin bloque)"""
        self._verificar_limite()
        stmt = self.sentencia()
        return Bloque([stmt]) if stmt else Bloque([])

    def sentencia_while(self):
        self._verificar_limite()
        self._avanzar()  # Consumir 'while'
        if not self._es(TipoToken.PARENTESIS_IZQ):
            self._error("Falta paréntesis de apertura '(' en while.")
            return None
        self._avanzar()
        cond = self.expresion()
        if not self._es(TipoToken.PARENTESIS_DER):
            self._error("Falta paréntesis de cierre ')' en while.")
        else:
            self._avanzar()
        
        cuerpo = self.bloque() if self._es(TipoToken.LLAVE_IZQ) else self._sentencia_simple()
        return SentenciaWhile(cond, cuerpo)

    def sentencia_do_while(self):
        self._verificar_limite()
        self._avanzar()  # Consumir 'do'
        cuerpo = self.bloque() if self._es(TipoToken.LLAVE_IZQ) else self._sentencia_simple()
        if not self._es(TipoToken.WHILE):
            self._error("Se esperaba 'while' después de 'do' {...}")
            return SentenciaDoWhile(cuerpo, Literal(True, 'boolean'))
        self._avanzar()
        if not self._es(TipoToken.PARENTESIS_IZQ):
            self._error("Falta paréntesis de apertura '(' en do-while.")
        else:
            self._avanzar()
        cond = self.expresion()
        if not self._es(TipoToken.PARENTESIS_DER):
            self._error("Falta paréntesis de cierre ')' en do-while.")
        else:
            self._avanzar()
        if self._es(TipoToken.PUNTO_COMA):
            self._avanzar()
        else:
            self._error("Falta punto y coma ';' después de do-while.")
        return SentenciaDoWhile(cuerpo, cond)

    def sentencia_for(self):
        self._verificar_limite()
        self._avanzar()  # Consumir 'for'
        if not self._es(TipoToken.PARENTESIS_IZQ):
            self._error("Falta paréntesis de apertura '(' en for.")
            return None
        self._avanzar()

        # Inicialización
        inicial = None
        if self._es_tipo():
            inicial = self.declaracion_variable()
        elif not self._es(TipoToken.PUNTO_COMA):
            inicial = self.expresion()
            if self._es(TipoToken.PUNTO_COMA):
                self._avanzar()
        else:
            self._avanzar()  # Saltar ';'

        # Condición
        cond = None
        if not self._es(TipoToken.PUNTO_COMA):
            cond = self.expresion()
        if self._es(TipoToken.PUNTO_COMA):
            self._avanzar()

        # Incremento
        inc = None
        if not self._es(TipoToken.PARENTESIS_DER):
            inc = self.expresion()
        if not self._es(TipoToken.PARENTESIS_DER):
            self._error("Falta paréntesis de cierre ')' en for.")
        else:
            self._avanzar()

        cuerpo = self.bloque() if self._es(TipoToken.LLAVE_IZQ) else self._sentencia_simple()
        return SentenciaFor(inicial, cond, inc, cuerpo)

    def sentencia_return(self):
        self._verificar_limite()
        self._avanzar()  # Consumir 'return'
        expr = None
        if not self._es(TipoToken.PUNTO_COMA):
            expr = self.expresion()
        if self._es(TipoToken.PUNTO_COMA):
            self._avanzar()
        else:
            self._error("Falta punto y coma ';' en return.")
        return SentenciaReturn(expr)

    def sentencia_expresion(self):
        self._verificar_limite()
        expr = self.expresion()
        if self._es(TipoToken.PUNTO_COMA):
            self._avanzar()
            return SentenciaExpresion(expr)
        else:
            self._error("Falta punto y coma ';' en sentencia.")
            return SentenciaExpresion(expr) if expr else None

    # =========== EXPRESIONES ============
    def expresion(self):
        self._verificar_limite()
        return self.expresion_asignacion()

    def expresion_asignacion(self):
        self._verificar_limite()
        expr = self.expresion_binaria()
        if self._es(TipoToken.ASIGNACION):
            if isinstance(expr, Identificador) or isinstance(expr, ExpresionIndice):
                self._avanzar()
                valor = self.expresion_asignacion()
                if isinstance(expr, ExpresionIndice):
                    return AsignacionIndice(expr.arreglo, expr.indice, valor)
                return Asignacion(expr.nombre, valor)
            else:
                self._error("El lado izquierdo de una asignación debe ser identificador o índice de arreglo.")
        return expr

    def expresion_binaria(self, min_prec=0):
        self._verificar_limite()
        izquierda = self.expresion_unaria()
        while True:
            self._verificar_limite()
            actual = self._actual()
            if not actual:
                break
            op, prec = self._op_binario(actual.tipo)
            if prec < min_prec:
                break
            self._avanzar()
            derecha = self.expresion_binaria(prec + 1)
            izquierda = ExpresionBinaria(izquierda, op, derecha)
        return izquierda

    def _op_binario(self, tipo):
        tabla = {
            TipoToken.MAS: ('+', 10),
            TipoToken.MENOS: ('-', 10),
            TipoToken.MULTIPLICACION: ('*', 20),
            TipoToken.DIVISION: ('/', 20),
            TipoToken.MODULO: ('%', 20),
            TipoToken.IGUAL_IGUAL: ('==', 5),
            TipoToken.DIFERENTE: ('!=', 5),
            TipoToken.MENOR: ('<', 5),
            TipoToken.MAYOR: ('>', 5),
            TipoToken.MENOR_IGUAL: ('<=', 5),
            TipoToken.MAYOR_IGUAL: ('>=', 5),
            TipoToken.AND: ('&&', 3),
            TipoToken.OR: ('||', 2),
        }
        return tabla.get(tipo, (None, -1))

    def expresion_unaria(self):
        self._verificar_limite()
        if self._es(TipoToken.MAS):
            self._avanzar()
            return self.expresion_unaria()
        if self._es(TipoToken.MENOS):
            self._avanzar()
            expr = self.expresion_unaria()
            return ExpresionUnaria('-', expr)
        if self._es(TipoToken.NOT):
            self._avanzar()
            expr = self.expresion_unaria()
            return ExpresionUnaria('!', expr)
        if self._es(TipoToken.INCREMENTO):
            self._avanzar()
            expr = self.expresion_unaria()
            return ExpresionUnaria('++', expr)
        if self._es(TipoToken.DECREMENTO):
            self._avanzar()
            expr = self.expresion_unaria()
            return ExpresionUnaria('--', expr)
        return self.expresion_postfija()

    def expresion_postfija(self):
        self._verificar_limite()
        expr = self.expresion_primaria()
        while True:
            self._verificar_limite()
            if self._es(TipoToken.INCREMENTO):
                self._avanzar()
                expr = ExpresionUnaria('++_post', expr)
            elif self._es(TipoToken.DECREMENTO):
                self._avanzar()
                expr = ExpresionUnaria('--_post', expr)
            elif self._es(TipoToken.PARENTESIS_IZQ):
                args = self._argumentos_llamada()
                nombre = expr.nombre if isinstance(expr, Identificador) else "<anon>"
                expr = ExpresionLlamada(nombre, args)
            elif self._es(TipoToken.PUNTO):
                self._avanzar()
                if self._es(TipoToken.IDENTIFICADOR):
                    miembro = self._actual().valor
                    self._avanzar()
                    expr = ExpresionAcceso(expr, miembro)
                else:
                    self._error("Falta identificador después de '.'")
                    break
            elif self._es(TipoToken.CORCHETE_IZQ):
                self._avanzar()
                idx = self.expresion()
                if self._es(TipoToken.CORCHETE_DER):
                    self._avanzar()
                    expr = ExpresionIndice(expr, idx)
                else:
                    self._error("Falta ']' después de índice de arreglo.")
                    break
            else:
                break
        return expr

    def _argumentos_llamada(self):
        self._verificar_limite()
        self._avanzar()  # Consumir '('
        args = []
        while not self._es(TipoToken.PARENTESIS_DER) and not self._es(TipoToken.EOF):
            self._verificar_limite()
            args.append(self.expresion())
            if self._es(TipoToken.COMA):
                self._avanzar()
            else:
                break
        if self._es(TipoToken.PARENTESIS_DER):
            self._avanzar()
        else:
            self._error("Falta ')' en llamada.")
        return args

    def expresion_primaria(self):
        self._verificar_limite()
        if self._es(TipoToken.NUMERO_ENTERO):
            valor = int(self._actual().valor)
            self._avanzar()
            return Literal(valor, 'int')
        if self._es(TipoToken.NUMERO_FLOTANTE):
            valor = float(self._actual().valor)
            self._avanzar()
            return Literal(valor, 'float')
        if self._es(TipoToken.CADENA):
            valor = self._actual().valor
            self._avanzar()
            return Literal(valor, 'string')
        if self._es(TipoToken.CARACTER):
            valor = self._actual().valor
            self._avanzar()
            return Literal(valor, 'char')
        if self._es(TipoToken.TRUE):
            self._avanzar()
            return Literal(True, 'boolean')
        if self._es(TipoToken.FALSE):
            self._avanzar()
            return Literal(False, 'boolean')
        if self._es(TipoToken.NULL):
            self._avanzar()
            return Literal(None, 'null')
        if self._es(TipoToken.IDENTIFICADOR):
            nombre = self._actual().valor
            self._avanzar()
            return Identificador(nombre)
        if self._es(TipoToken.PARENTESIS_IZQ):
            self._avanzar()
            expr = self.expresion()
            if self._es(TipoToken.PARENTESIS_DER):
                self._avanzar()
            else:
                self._error("Falta ')' de agrupación.")
            return ExpresionAgrupada(expr)
        
        # Si no es nada reconocido, avanzar para no quedarnos atascados
        tok = self._actual()
        if tok and tok.tipo != TipoToken.EOF:
            self._error(f"Expresión inesperada: '{tok.valor}'")
            self._avanzar()
        return Literal(0, 'int')

    # ======= Helpers =======
    def _es(self, tipo):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos].tipo == tipo
        return False

    def _actual(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _avanzar(self):
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        else:
            self.pos = len(self.tokens)

    def _es_tipo(self):
        return self._es(TipoToken.INT) or self._es(TipoToken.FLOAT) or \
               self._es(TipoToken.BOOLEAN) or self._es(TipoToken.STRING) or \
               self._es(TipoToken.CHAR)

    def _error(self, mensaje):
        tok = self._actual()
        linea = tok.linea if tok else '?'
        self.errores.append(f"L{linea}: {mensaje}")
        self._errores_encontrados = True

