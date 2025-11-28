from ast_nodes import *


class GeneradorCodigoIntermedio:
    """Genera código intermedio en formato TAC"""
    
    def __init__(self, ast):
        self.ast = ast
        self.codigo = []
        self.contador_temporal = 0
        self.contador_etiqueta = 0
        self.tabla_variables = {}
    
    def generar(self):
        """Genera el código intermedio a partir del AST"""
        if self.ast:
            self._generar_programa(self.ast)
        return self.codigo
    
    def _nuevo_temporal(self):
        """Genera un nuevo nombre de variable temporal"""
        temp = f"t{self.contador_temporal}"
        self.contador_temporal += 1
        return temp
    
    def _nueva_etiqueta(self):
        """Genera una nueva etiqueta"""
        etiq = f"L{self.contador_etiqueta}"
        self.contador_etiqueta += 1
        return etiq
    
    def _emitir(self, instruccion):
        """Emite una instrucción de código intermedio"""
        self.codigo.append(instruccion)
    
    # ========== PROGRAMA ==========
    
    def _generar_programa(self, nodo):
        """Genera código para el programa completo"""
        for declaracion in nodo.declaraciones:
            self._generar_declaracion(declaracion)
    
    def _generar_declaracion(self, nodo):
        """Genera código para una declaración"""
        if isinstance(nodo, DeclaracionVariable):
            self._generar_declaracion_variable(nodo)
        elif isinstance(nodo, Bloque):
            self._generar_bloque(nodo)
        elif isinstance(nodo, (SentenciaIf, SentenciaWhile, SentenciaDoWhile,
                               SentenciaFor, SentenciaReturn, SentenciaExpresion)):
            self._generar_sentencia(nodo)
    
    def _generar_declaracion_variable(self, nodo):
        """Genera código para declaración de variable"""
        # Registrar la variable
        self.tabla_variables[nodo.nombre] = nodo.tipo
        
        # Si tiene inicializador, generar asignación
        if nodo.inicializador:
            valor = self._generar_expresion(nodo.inicializador)
            self._emitir(f"{nodo.nombre} = {valor}")
    
    # ========== SENTENCIAS ==========
    
    def _generar_sentencia(self, nodo):
        """Genera código para una sentencia"""
        if isinstance(nodo, Bloque):
            self._generar_bloque(nodo)
        elif isinstance(nodo, SentenciaIf):
            self._generar_if(nodo)
        elif isinstance(nodo, SentenciaWhile):
            self._generar_while(nodo)
        elif isinstance(nodo, SentenciaDoWhile):
            self._generar_do_while(nodo)
        elif isinstance(nodo, SentenciaFor):
            self._generar_for(nodo)
        elif isinstance(nodo, SentenciaReturn):
            self._generar_return(nodo)
        elif isinstance(nodo, SentenciaExpresion):
            self._generar_expresion(nodo.expresion)
    
    def _generar_bloque(self, nodo):
        """Genera código para un bloque"""
        for sentencia in nodo.sentencias:
            self._generar_declaracion(sentencia)
    
    def _generar_if(self, nodo):
        """Genera código para sentencia if"""
        etiq_else = self._nueva_etiqueta()
        etiq_fin = self._nueva_etiqueta()
        
        # Evaluar condición
        cond = self._generar_expresion(nodo.condicion)
        
        # Salto condicional
        if nodo.bloque_else:
            self._emitir(f"if_false {cond} goto {etiq_else}")
        else:
            self._emitir(f"if_false {cond} goto {etiq_fin}")
        
        # Bloque then
        self._generar_sentencia(nodo.bloque_if)
        
        if nodo.bloque_else:
            self._emitir(f"goto {etiq_fin}")
            self._emitir(f"{etiq_else}:")
            self._generar_sentencia(nodo.bloque_else)
        
        self._emitir(f"{etiq_fin}:")
    
    def _generar_while(self, nodo):
        """Genera código para sentencia while"""
        etiq_inicio = self._nueva_etiqueta()
        etiq_fin = self._nueva_etiqueta()
        
        # Etiqueta de inicio del bucle
        self._emitir(f"{etiq_inicio}:")
        
        # Evaluar condición
        cond = self._generar_expresion(nodo.condicion)
        self._emitir(f"if_false {cond} goto {etiq_fin}")
        
        # Cuerpo del bucle
        self._generar_sentencia(nodo.cuerpo)
        
        # Saltar al inicio
        self._emitir(f"goto {etiq_inicio}")
        
        # Etiqueta de fin
        self._emitir(f"{etiq_fin}:")
    
    def _generar_do_while(self, nodo):
        """Genera código para sentencia do-while"""
        etiq_inicio = self._nueva_etiqueta()
        
        # Etiqueta de inicio del bucle
        self._emitir(f"{etiq_inicio}:")
        
        # Cuerpo del bucle
        self._generar_sentencia(nodo.cuerpo)
        
        # Evaluar condición
        cond = self._generar_expresion(nodo.condicion)
        self._emitir(f"if_true {cond} goto {etiq_inicio}")
    
    def _generar_for(self, nodo):
        """Genera código para sentencia for"""
        etiq_inicio = self._nueva_etiqueta()
        etiq_fin = self._nueva_etiqueta()
        
        # Inicialización
        if nodo.inicializacion:
            if isinstance(nodo.inicializacion, DeclaracionVariable):
                self._generar_declaracion_variable(nodo.inicializacion)
            else:
                self._generar_expresion(nodo.inicializacion)
        
        # Etiqueta de inicio del bucle
        self._emitir(f"{etiq_inicio}:")
        
        # Condición
        if nodo.condicion:
            cond = self._generar_expresion(nodo.condicion)
            self._emitir(f"if_false {cond} goto {etiq_fin}")
        
        # Cuerpo
        self._generar_sentencia(nodo.cuerpo)
        
        # Incremento
        if nodo.incremento:
            self._generar_expresion(nodo.incremento)
        
        # Saltar al inicio
        self._emitir(f"goto {etiq_inicio}")
        
        # Etiqueta de fin
        self._emitir(f"{etiq_fin}:")
    
    def _generar_return(self, nodo):
        """Genera código para sentencia return"""
        if nodo.expresion:
            valor = self._generar_expresion(nodo.expresion)
            self._emitir(f"return {valor}")
        else:
            self._emitir("return")
    
    # ========== EXPRESIONES ==========
    
    def _generar_expresion(self, nodo):
        """Genera código para una expresión y retorna el temporal/variable resultado"""
        if isinstance(nodo, Literal):
            return str(nodo.valor)
        
        elif isinstance(nodo, Identificador):
            return nodo.nombre
        
        elif isinstance(nodo, Asignacion):
            valor = self._generar_expresion(nodo.valor)
            self._emitir(f"{nodo.nombre} = {valor}")
            return nodo.nombre
        
        elif isinstance(nodo, ExpresionBinaria):
            izq = self._generar_expresion(nodo.izquierda)
            der = self._generar_expresion(nodo.derecha)
            temp = self._nuevo_temporal()
            self._emitir(f"{temp} = {izq} {nodo.operador} {der}")
            return temp
        
        elif isinstance(nodo, ExpresionUnaria):
            operando = self._generar_expresion(nodo.operando)
            temp = self._nuevo_temporal()
            
            if nodo.operador == '++':
                self._emitir(f"{operando} = {operando} + 1")
                return operando
            elif nodo.operador == '--':
                self._emitir(f"{operando} = {operando} - 1")
                return operando
            elif nodo.operador == '++_post':
                self._emitir(f"{temp} = {operando}")
                self._emitir(f"{operando} = {operando} + 1")
                return temp
            elif nodo.operador == '--_post':
                self._emitir(f"{temp} = {operando}")
                self._emitir(f"{operando} = {operando} - 1")
                return temp
            else:
                self._emitir(f"{temp} = {nodo.operador}{operando}")
                return temp
        
        elif isinstance(nodo, ExpresionLlamada):
            # Generar código para argumentos
            args = []
            for arg in nodo.argumentos:
                args.append(self._generar_expresion(arg))
            
            # Llamada a función
            if args:
                args_str = ", ".join(args)
                self._emitir(f"param {args_str}")
            
            temp = self._nuevo_temporal()
            self._emitir(f"{temp} = call {nodo.nombre}")
            return temp
        
        elif isinstance(nodo, ExpresionAgrupada):
            return self._generar_expresion(nodo.expresion)
        
        return "0"
    
    def obtener_codigo(self):
        """Retorna el código intermedio como string formateado"""
        resultado = '\n' + '='*70 + '\n'
        resultado += '⚙️  CÓDIGO INTERMEDIO (TAC)\n'
        resultado += '='*70 + '\n'
        
        if not self.codigo:
            resultado += 'No se generó código intermedio.\n'
        else:
            for i, instruccion in enumerate(self.codigo, 1):
                resultado += f"{i:3d}. {instruccion}\n"
        
        resultado += '='*70 + '\n'
        return resultado