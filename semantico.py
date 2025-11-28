"""
Analizador Semántico
Verifica tipos, alcances y reglas semánticas del lenguaje
"""

from lexico import TipoToken
from tabla_simbolos import TablaSimbolos


class AnalizadorSemantico:
    """Analizador semántico que recorre tokens"""
    MAX_ITERACIONES = 10000

    def __init__(self, tokens):
        self.tokens = tokens
        self.posicion = 0
        self.tabla_simbolos = TablaSimbolos()
        self.tipo_actual = None
        self.en_bucle = 0  # Nivel de anidamiento de bucles
        self.en_funcion = False
        self._iteraciones = 0
        # Información sobre ciclos anidados
        self.ciclos_anidados = []  # Lista de (tipo_externo, tipo_interno, linea, nivel)
        self.pila_ciclos = []  # Pila para rastrear ciclos actuales (tipo, linea)

    def _verificar_limite(self):
        self._iteraciones += 1
        if self._iteraciones > self.MAX_ITERACIONES:
            raise Exception("Límite de iteraciones excedido en análisis semántico")

    def _token_actual(self):
        if self.posicion < len(self.tokens):
            return self.tokens[self.posicion]
        return self.tokens[-1] if self.tokens else None

    def _avanzar(self):
        if self.posicion < len(self.tokens) - 1:
            self.posicion += 1

    def _verificar(self, tipo):
        tok = self._token_actual()
        return tok and tok.tipo == tipo

    def _peek(self, k=1):
        idx = self.posicion + k
        if 0 <= idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1] if self.tokens else None

    def analizar(self):
        try:
            self._analizar_programa()
            return len(self.tabla_simbolos.errores) == 0
        except Exception as e:
            self.tabla_simbolos.errores.append(f"Error crítico: {str(e)}")
            return False

    def _analizar_programa(self):
        last_pos = -1
        while not self._verificar(TipoToken.EOF):
            self._verificar_limite()
            if self.posicion == last_pos:
                self._avanzar()
                continue
            last_pos = self.posicion
            self._analizar_declaracion()

    def _analizar_declaracion(self):
        self._verificar_limite()
        t = self._token_actual()
        if not t:
            return
        if t.tipo in (TipoToken.INT, TipoToken.FLOAT, TipoToken.BOOLEAN, TipoToken.STRING, TipoToken.CHAR):
            self._analizar_declaracion_variable()
        else:
            self._analizar_sentencia()

    def _analizar_declaracion_variable(self):
        self._verificar_limite()
        token_tipo = self._token_actual()
        if not token_tipo or token_tipo.tipo not in (TipoToken.INT, TipoToken.FLOAT, TipoToken.BOOLEAN, TipoToken.STRING, TipoToken.CHAR):
            return
        tipo_base = token_tipo.valor
        self._avanzar()

        es_arreglo = False
        tam_arreglo = 0

        # Formato Java: tipo[] nombre
        if self._verificar(TipoToken.CORCHETE_IZQ):
            peek = self._peek()
            if peek and peek.tipo == TipoToken.CORCHETE_DER:
                es_arreglo = True
                self._avanzar()
                self._avanzar()

        if not self._verificar(TipoToken.IDENTIFICADOR):
            return
        nombre = self._token_actual().valor
        linea_decl = self._token_actual().linea
        self._avanzar()

        # Formato C: nombre[NUM]
        if self._verificar(TipoToken.CORCHETE_IZQ):
            es_arreglo = True
            self._avanzar()
            if self._verificar(TipoToken.NUMERO_ENTERO):
                tam_arreglo = int(self._token_actual().valor)
                self._avanzar()
            if self._verificar(TipoToken.CORCHETE_DER):
                self._avanzar()

        if es_arreglo:
            self.tabla_simbolos.declarar_arreglo(nombre, tipo_base, tam_arreglo, linea_decl)
        else:
            self.tabla_simbolos.declarar_variable(nombre, tipo_base, linea_decl)

        if self._verificar(TipoToken.ASIGNACION):
            self._avanzar()
            if self._verificar(TipoToken.CORCHETE_IZQ):
                self._saltar_literal_arreglo()
                self.tabla_simbolos.marcar_inicializada(nombre)
            else:
                self._analizar_expresion()
                self.tabla_simbolos.marcar_inicializada(nombre)

        if self._verificar(TipoToken.PUNTO_COMA):
            self._avanzar()

    def _analizar_sentencia(self):
        self._verificar_limite()
        t = self._token_actual()
        if not t:
            return
        if t.tipo == TipoToken.LLAVE_IZQ:
            self._analizar_bloque()
        elif t.tipo == TipoToken.IF:
            self._analizar_if()
        elif t.tipo == TipoToken.WHILE:
            self._analizar_while()
        elif t.tipo == TipoToken.DO:
            self._analizar_do_while()
        elif t.tipo == TipoToken.FOR:
            self._analizar_for()
        elif t.tipo == TipoToken.RETURN:
            self._analizar_return()
        else:
            self._analizar_sentencia_expresion()

    def _analizar_bloque(self):
        self._verificar_limite()
        if not self._verificar(TipoToken.LLAVE_IZQ):
            return
        self._avanzar()
        self.tabla_simbolos.entrar_alcance("bloque")
        last_pos = -1
        while not self._verificar(TipoToken.LLAVE_DER) and not self._verificar(TipoToken.EOF):
            self._verificar_limite()
            if self.posicion == last_pos:
                self._avanzar()
                continue
            last_pos = self.posicion
            self._analizar_declaracion()
        self.tabla_simbolos.salir_alcance()
        if self._verificar(TipoToken.LLAVE_DER):
            self._avanzar()

    def _analizar_if(self):
        self._verificar_limite()
        self._avanzar()
        if self._verificar(TipoToken.PARENTESIS_IZQ):
            self._avanzar()
        tipo_cond = self._analizar_expresion()
        if tipo_cond and tipo_cond != 'boolean':
            tok = self._token_actual()
            linea = tok.linea if tok else '?'
            self.tabla_simbolos.errores.append(f"Error semántico en línea {linea}: La condición del if debe ser boolean")
        if self._verificar(TipoToken.PARENTESIS_DER):
            self._avanzar()
        self._analizar_sentencia()
        if self._verificar(TipoToken.ELSE):
            self._avanzar()
            self._analizar_sentencia()

    def _registrar_ciclo_anidado(self, tipo_ciclo, linea):
        """Registra un ciclo y detecta anidamiento"""
        if self.en_bucle > 0 and len(self.pila_ciclos) > 0:
            # Hay un ciclo externo, registrar anidamiento
            ciclo_externo = self.pila_ciclos[-1]
            self.ciclos_anidados.append({
                'tipo_externo': ciclo_externo['tipo'],
                'linea_externo': ciclo_externo['linea'],
                'tipo_interno': tipo_ciclo,
                'linea_interno': linea,
                'nivel': self.en_bucle + 1
            })
        
        # Agregar este ciclo a la pila
        self.pila_ciclos.append({'tipo': tipo_ciclo, 'linea': linea})

    def _salir_ciclo(self):
        """Sale del ciclo actual"""
        if self.pila_ciclos:
            self.pila_ciclos.pop()

    def _analizar_while(self):
        self._verificar_limite()
        token_while = self._token_actual()
        linea = token_while.linea if token_while else 0
        self._avanzar()
        
        if self._verificar(TipoToken.PARENTESIS_IZQ):
            self._avanzar()
        tipo_cond = self._analizar_expresion()
        if tipo_cond and tipo_cond != 'boolean':
            tok = self._token_actual()
            ln = tok.linea if tok else '?'
            self.tabla_simbolos.errores.append(f"Error semántico en línea {ln}: La condición del while debe ser boolean")
        if self._verificar(TipoToken.PARENTESIS_DER):
            self._avanzar()
        
        # Registrar ciclo anidado
        self._registrar_ciclo_anidado('while', linea)
        self.en_bucle += 1
        self._analizar_sentencia()
        self.en_bucle -= 1
        self._salir_ciclo()

    def _analizar_do_while(self):
        self._verificar_limite()
        token_do = self._token_actual()
        linea = token_do.linea if token_do else 0
        self._avanzar()
        
        # Registrar ciclo anidado
        self._registrar_ciclo_anidado('do-while', linea)
        self.en_bucle += 1
        self._analizar_sentencia()
        self.en_bucle -= 1
        self._salir_ciclo()
        
        if self._verificar(TipoToken.WHILE):
            self._avanzar()
        if self._verificar(TipoToken.PARENTESIS_IZQ):
            self._avanzar()
        tipo_cond = self._analizar_expresion()
        if tipo_cond and tipo_cond != 'boolean':
            tok = self._token_actual()
            ln = tok.linea if tok else '?'
            self.tabla_simbolos.errores.append(f"Error semántico en línea {ln}: La condición del do-while debe ser boolean")
        if self._verificar(TipoToken.PARENTESIS_DER):
            self._avanzar()
        if self._verificar(TipoToken.PUNTO_COMA):
            self._avanzar()

    def _analizar_for(self):
        self._verificar_limite()
        token_for = self._token_actual()
        linea = token_for.linea if token_for else 0
        self._avanzar()
        
        if self._verificar(TipoToken.PARENTESIS_IZQ):
            self._avanzar()

        self.tabla_simbolos.entrar_alcance("for")

        # Inicialización
        if not self._verificar(TipoToken.PUNTO_COMA):
            tok = self._token_actual()
            if tok and tok.tipo in (TipoToken.INT, TipoToken.FLOAT, TipoToken.BOOLEAN, TipoToken.STRING, TipoToken.CHAR):
                self._analizar_declaracion_variable()
            else:
                self._analizar_expresion()
                if self._verificar(TipoToken.PUNTO_COMA):
                    self._avanzar()
        else:
            self._avanzar()

        # Condición
        if not self._verificar(TipoToken.PUNTO_COMA):
            tipo_cond = self._analizar_expresion()
            if tipo_cond and tipo_cond != 'boolean':
                tok = self._token_actual()
                ln = tok.linea if tok else '?'
                self.tabla_simbolos.errores.append(f"Error semántico en línea {ln}: La condición del for debe ser boolean")
        if self._verificar(TipoToken.PUNTO_COMA):
            self._avanzar()

        # Incremento
        if not self._verificar(TipoToken.PARENTESIS_DER):
            self._analizar_expresion()
        if self._verificar(TipoToken.PARENTESIS_DER):
            self._avanzar()

        # Registrar ciclo anidado
        self._registrar_ciclo_anidado('for', linea)
        self.en_bucle += 1
        self._analizar_sentencia()
        self.en_bucle -= 1
        self._salir_ciclo()
        self.tabla_simbolos.salir_alcance()

    def _analizar_return(self):
        self._verificar_limite()
        self._avanzar()
        if not self._verificar(TipoToken.PUNTO_COMA):
            self._analizar_expresion()
        if self._verificar(TipoToken.PUNTO_COMA):
            self._avanzar()

    def _analizar_sentencia_expresion(self):
        self._verificar_limite()
        self._analizar_expresion()
        if self._verificar(TipoToken.PUNTO_COMA):
            self._avanzar()

    def _analizar_expresion(self):
        self._verificar_limite()
        return self._analizar_asignacion()

    def _analizar_asignacion(self):
        self._verificar_limite()
        pos_inicial = self.posicion

        # Caso: identificador = valor
        if self._verificar(TipoToken.IDENTIFICADOR):
            token_id = self._token_actual()
            nombre = token_id.valor
            linea = token_id.linea
            self._avanzar()

            # Caso: arreglo[indice] = valor
            if self._verificar(TipoToken.CORCHETE_IZQ):
                self._avanzar()
                tipo_idx = self._analizar_expresion()
                if tipo_idx and tipo_idx != 'int':
                    self.tabla_simbolos.errores.append(f"Error semántico en línea {linea}: índice de arreglo debe ser int")
                if self._verificar(TipoToken.CORCHETE_DER):
                    self._avanzar()
                
                if self._verificar(TipoToken.ASIGNACION):
                    self._avanzar()
                    tipo_valor = self._analizar_asignacion()
                    # Obtener tipo base del arreglo
                    tipo_elemento = self.tabla_simbolos.obtener_tipo_elemento_arreglo(nombre, linea)
                    if tipo_elemento and tipo_valor:
                        self.tabla_simbolos.verificar_compatibilidad_tipos(tipo_elemento, tipo_valor, linea)
                    return tipo_elemento
                else:
                    # Solo acceso, no asignación
                    self.posicion = pos_inicial
                    return self._analizar_or()

            # Caso: variable = valor
            if self._verificar(TipoToken.ASIGNACION):
                self._avanzar()
                if self._verificar(TipoToken.CORCHETE_IZQ):
                    self._saltar_literal_arreglo()
                    simbolo = self.tabla_simbolos.buscar_variable(nombre, linea)
                    if simbolo:
                        self.tabla_simbolos.marcar_inicializada(nombre)
                        return simbolo.tipo
                    return None
                simbolo = self.tabla_simbolos.buscar_variable(nombre, linea)
                tipo_valor = self._analizar_asignacion()
                if simbolo and tipo_valor:
                    self.tabla_simbolos.verificar_compatibilidad_tipos(simbolo.tipo, tipo_valor, linea)
                    self.tabla_simbolos.marcar_inicializada(nombre)
                    return simbolo.tipo
                elif simbolo:
                    self.tabla_simbolos.marcar_inicializada(nombre)
                    return simbolo.tipo
                return tipo_valor

        self.posicion = pos_inicial
        return self._analizar_or()

    def _analizar_or(self):
        self._verificar_limite()
        tipo_izq = self._analizar_and()
        while self._verificar(TipoToken.OR):
            token = self._token_actual()
            self._avanzar()
            tipo_der = self._analizar_and()
            tipo_izq = self.tabla_simbolos.obtener_tipo_expresion_binaria(tipo_izq, '||', tipo_der, token.linea)
        return tipo_izq

    def _analizar_and(self):
        self._verificar_limite()
        tipo_izq = self._analizar_igualdad()
        while self._verificar(TipoToken.AND):
            token = self._token_actual()
            self._avanzar()
            tipo_der = self._analizar_igualdad()
            tipo_izq = self.tabla_simbolos.obtener_tipo_expresion_binaria(tipo_izq, '&&', tipo_der, token.linea)
        return tipo_izq

    def _analizar_igualdad(self):
        self._verificar_limite()
        tipo_izq = self._analizar_comparacion()
        while self._verificar(TipoToken.IGUAL_IGUAL) or self._verificar(TipoToken.DIFERENTE):
            token = self._token_actual()
            operador = token.valor
            self._avanzar()
            tipo_der = self._analizar_comparacion()
            tipo_izq = self.tabla_simbolos.obtener_tipo_expresion_binaria(tipo_izq, operador, tipo_der, token.linea)
        return tipo_izq

    def _analizar_comparacion(self):
        self._verificar_limite()
        tipo_izq = self._analizar_termino()
        tok = self._token_actual()
        while tok and tok.tipo in (TipoToken.MENOR, TipoToken.MAYOR, TipoToken.MENOR_IGUAL, TipoToken.MAYOR_IGUAL):
            self._verificar_limite()
            operador = tok.valor
            self._avanzar()
            tipo_der = self._analizar_termino()
            tipo_izq = self.tabla_simbolos.obtener_tipo_expresion_binaria(tipo_izq, operador, tipo_der, tok.linea)
            tok = self._token_actual()
        return tipo_izq

    def _analizar_termino(self):
        self._verificar_limite()
        tipo_izq = self._analizar_factor()
        while self._verificar(TipoToken.MAS) or self._verificar(TipoToken.MENOS):
            self._verificar_limite()
            token = self._token_actual()
            operador = token.valor
            self._avanzar()
            tipo_der = self._analizar_factor()
            tipo_izq = self.tabla_simbolos.obtener_tipo_expresion_binaria(tipo_izq, operador, tipo_der, token.linea)
        return tipo_izq

    def _analizar_factor(self):
        self._verificar_limite()
        tipo_izq = self._analizar_postfijo()
        tok = self._token_actual()
        while tok and tok.tipo in (TipoToken.MULTIPLICACION, TipoToken.DIVISION, TipoToken.MODULO):
            self._verificar_limite()
            operador = tok.valor
            self._avanzar()
            tipo_der = self._analizar_postfijo()
            tipo_izq = self.tabla_simbolos.obtener_tipo_expresion_binaria(tipo_izq, operador, tipo_der, tok.linea)
            tok = self._token_actual()
        return tipo_izq

    def _analizar_postfijo(self):
        self._verificar_limite()
        tipo = self._analizar_unario()
        tok = self._token_actual()
        while tok and tok.tipo in (TipoToken.INCREMENTO, TipoToken.DECREMENTO):
            self._verificar_limite()
            self._avanzar()
            # Normalizar tipo para verificación
            tipo_base = tipo[:-2] if tipo and tipo.endswith('[]') else tipo
            if tipo_base not in ('int', 'float'):
                self.tabla_simbolos.errores.append(f"Error semántico en línea {tok.linea}: Operador requiere operando numérico")
            tok = self._token_actual()
        return tipo

    def _analizar_unario(self):
        self._verificar_limite()
        tok = self._token_actual()
        if tok and tok.tipo in (TipoToken.NOT, TipoToken.MENOS, TipoToken.MAS, TipoToken.INCREMENTO, TipoToken.DECREMENTO):
            operador = tok.valor
            linea = tok.linea
            self._avanzar()
            tipo_operando = self._analizar_unario()
            tipo_base = tipo_operando[:-2] if tipo_operando and tipo_operando.endswith('[]') else tipo_operando
            if operador in ('++', '--'):
                if tipo_base not in ('int', 'float'):
                    self.tabla_simbolos.errores.append(f"Error semántico en línea {linea}: Operador requiere operando numérico")
                return tipo_operando
            if operador == '!':
                if tipo_base != 'boolean':
                    self.tabla_simbolos.errores.append(f"Error semántico en línea {linea}: Operador '!' requiere operando booleano")
                return 'boolean'
            if operador in ('+', '-'):
                if tipo_base not in ('int', 'float'):
                    self.tabla_simbolos.errores.append(f"Error semántico en línea {linea}: Operador requiere operando numérico")
                return tipo_operando
        return self._analizar_primario()

    def _analizar_primario(self):
        self._verificar_limite()
        token = self._token_actual()
        if not token:
            return None

        if token.tipo == TipoToken.NUMERO_ENTERO:
            self._avanzar()
            return 'int'
        if token.tipo == TipoToken.NUMERO_FLOTANTE:
            self._avanzar()
            return 'float'
        if token.tipo == TipoToken.CADENA:
            # Las cadenas entre comillas dobles son tipo String
            self._avanzar()
            return 'String'
        if token.tipo == TipoToken.CARACTER:
            # Los caracteres entre comillas simples son tipo char
            self._avanzar()
            return 'char'
        if token.tipo in (TipoToken.TRUE, TipoToken.FALSE):
            self._avanzar()
            return 'boolean'
        if token.tipo == TipoToken.NULL:
            self._avanzar()
            return 'null'

        if token.tipo == TipoToken.IDENTIFICADOR:
            nombre = token.valor
            linea_token = token.linea
            self._avanzar()

            # Acceso a miembros (System.out.println, etc.)
            while self._verificar(TipoToken.PUNTO):
                self._verificar_limite()
                self._avanzar()
                if self._verificar(TipoToken.IDENTIFICADOR):
                    nombre = f"{nombre}.{self._token_actual().valor}"
                    self._avanzar()
                else:
                    break

            # Llamada a función
            if self._verificar(TipoToken.PARENTESIS_IZQ):
                self._avanzar()
                while not self._verificar(TipoToken.PARENTESIS_DER) and not self._verificar(TipoToken.EOF):
                    self._verificar_limite()
                    self._analizar_expresion()
                    if self._verificar(TipoToken.COMA):
                        self._avanzar()
                    else:
                        break
                if self._verificar(TipoToken.PARENTESIS_DER):
                    self._avanzar()
                if nombre == "System.out.println":
                    return 'void'
                return 'int'

            # Acceso a índice de arreglo
            if self._verificar(TipoToken.CORCHETE_IZQ):
                self._avanzar()
                tipo_idx = self._analizar_expresion()
                if tipo_idx and tipo_idx != 'int':
                    self.tabla_simbolos.errores.append(f"Error semántico en línea {linea_token}: índice de arreglo debe ser int, se encontró '{tipo_idx}'")
                if self._verificar(TipoToken.CORCHETE_DER):
                    self._avanzar()
                # Retornar tipo BASE del arreglo, no int[]
                tipo_elemento = self.tabla_simbolos.obtener_tipo_elemento_arreglo(nombre, linea_token)
                return tipo_elemento if tipo_elemento else 'int'

            # Variable simple
            simbolo = self.tabla_simbolos.buscar_variable(nombre, linea_token)
            if simbolo:
                # Si es arreglo sin índice, retornar tipo completo (int[])
                # Si tiene índice, ya se manejó arriba
                return simbolo.tipo_completo if simbolo.es_arreglo else simbolo.tipo
            return None

        if token.tipo == TipoToken.PARENTESIS_IZQ:
            self._avanzar()
            tipo = self._analizar_expresion()
            if self._verificar(TipoToken.PARENTESIS_DER):
                self._avanzar()
            return tipo

        if token.tipo == TipoToken.CORCHETE_IZQ:
            self._saltar_literal_arreglo()
            return None

        # Token no reconocido, avanzar
        self._avanzar()
        return None

    def _saltar_literal_arreglo(self):
        if not self._verificar(TipoToken.CORCHETE_IZQ):
            return
        profundidad = 0
        while self.posicion < len(self.tokens):
            self._verificar_limite()
            t = self._token_actual()
            if not t:
                break
            if t.tipo == TipoToken.CORCHETE_IZQ:
                profundidad += 1
            elif t.tipo == TipoToken.CORCHETE_DER:
                profundidad -= 1
            self._avanzar()
            if profundidad == 0:
                break

    def obtener_reporte_ciclos_anidados(self):
        """Genera un reporte de los ciclos anidados encontrados"""
        if not self.ciclos_anidados:
            return ""
        
        resultado = '\n' + '='*70 + '\n'
        resultado += '🔄 ESTRUCTURAS ITERATIVAS ANIDADAS DETECTADAS\n'
        resultado += '='*70 + '\n'
        
        for i, ciclo in enumerate(self.ciclos_anidados, 1):
            nivel = ciclo['nivel']
            indent = "  " * (nivel - 1)
            resultado += f"\n  📍 Anidamiento #{i}:\n"
            resultado += f"     ┌─ Ciclo externo: {ciclo['tipo_externo'].upper()} (línea {ciclo['linea_externo']})\n"
            resultado += f"     └─ Ciclo interno: {ciclo['tipo_interno'].upper()} (línea {ciclo['linea_interno']})\n"
            resultado += f"        Nivel de anidamiento: {nivel}\n"
        
        # Resumen
        resultado += '\n' + '-'*70 + '\n'
        resultado += f"  📊 Resumen:\n"
        resultado += f"     • Total de anidamientos: {len(self.ciclos_anidados)}\n"
        
        # Contar tipos de combinaciones
        combinaciones = {}
        for ciclo in self.ciclos_anidados:
            comb = f"{ciclo['tipo_externo']} → {ciclo['tipo_interno']}"
            combinaciones[comb] = combinaciones.get(comb, 0) + 1
        
        resultado += f"     • Combinaciones encontradas:\n"
        for comb, count in combinaciones.items():
            resultado += f"       - {comb}: {count} vez(es)\n"
        
        # Nivel máximo
        max_nivel = max(c['nivel'] for c in self.ciclos_anidados)
        resultado += f"     • Nivel máximo de anidamiento: {max_nivel}\n"
        
        resultado += '='*70 + '\n'
        return resultado

    def obtener_reporte(self):
        resultado = '\n' + '='*70 + '\n'
        resultado += '✨ ANÁLISIS SEMÁNTICO\n'
        resultado += '='*70 + '\n'
        errores = self.tabla_simbolos.errores if self.tabla_simbolos.errores else []
        if errores:
            resultado += '❌ ERRORES SEMÁNTICOS:\n'
            for e in errores:
                resultado += f'  • {e}\n'
        else:
            resultado += '✅ Sin errores semánticos\n'
        resultado += '='*70 + '\n'
        
        # Agregar reporte de ciclos anidados
        resultado += self.obtener_reporte_ciclos_anidados()
        
        return resultado