import re


class Interprete:
    """Intérprete simple para código intermedio TAC"""
    
    def __init__(self, codigo_intermedio):
        self.codigo = codigo_intermedio
        self.variables = {}
        self.etiquetas = {}
        self.pc = 0  # Program counter
        self.salida = []
        self.pila_llamadas = []
        self.max_instrucciones = 10000  # Prevenir bucles infinitos
        self.contador_instrucciones = 0
    
    def ejecutar(self):
        """Ejecuta el código intermedio"""
        try:
            # Primera pasada: encontrar todas las etiquetas
            self._mapear_etiquetas()
            
            # Segunda pasada: ejecutar instrucciones
            while self.pc < len(self.codigo):
                if self.contador_instrucciones >= self.max_instrucciones:
                    self.salida.append("⚠️  Límite de instrucciones alcanzado (posible bucle infinito)")
                    break
                
                instruccion = self.codigo[self.pc].strip()
                
                # Ignorar líneas vacías y etiquetas
                if not instruccion or instruccion.endswith(':'):
                    self.pc += 1
                    continue
                
                self._ejecutar_instruccion(instruccion)
                self.contador_instrucciones += 1
            
            return True
        except Exception as e:
            self.salida.append(f"❌ Error en ejecución: {str(e)}")
            return False
    
    def _mapear_etiquetas(self):
        """Mapea las etiquetas a sus posiciones en el código"""
        for i, instruccion in enumerate(self.codigo):
            instruccion = instruccion.strip()
            if instruccion.endswith(':'):
                etiqueta = instruccion[:-1]
                self.etiquetas[etiqueta] = i
    
    def _ejecutar_instruccion(self, instruccion):
        """Ejecuta una instrucción individual"""
        # Asignación simple: x = valor
        match = re.match(r'(\w+)\s*=\s*(.+)', instruccion)
        if match:
            var = match.group(1)
            expr = match.group(2).strip()
            
            # Verificar si es una llamada a función
            if 'call' in expr:
                self._ejecutar_llamada(var, expr)
            else:
                valor = self._evaluar_expresion(expr)
                self.variables[var] = valor
            
            self.pc += 1
            return
        
        # Salto condicional: if_false cond goto etiqueta
        match = re.match(r'if_false\s+(\w+)\s+goto\s+(\w+)', instruccion)
        if match:
            cond = match.group(1)
            etiqueta = match.group(2)
            
            valor_cond = self._obtener_valor(cond)
            if not valor_cond:
                self.pc = self.etiquetas[etiqueta]
            else:
                self.pc += 1
            return
        
        # Salto condicional: if_true cond goto etiqueta
        match = re.match(r'if_true\s+(\w+)\s+goto\s+(\w+)', instruccion)
        if match:
            cond = match.group(1)
            etiqueta = match.group(2)
            
            valor_cond = self._obtener_valor(cond)
            if valor_cond:
                self.pc = self.etiquetas[etiqueta]
            else:
                self.pc += 1
            return
        
        # Salto incondicional: goto etiqueta
        match = re.match(r'goto\s+(\w+)', instruccion)
        if match:
            etiqueta = match.group(1)
            self.pc = self.etiquetas[etiqueta]
            return
        
        # Parámetros: param valores
        match = re.match(r'param\s+(.+)', instruccion)
        if match:
            # Guardar parámetros para la siguiente llamada
            self.parametros_actuales = match.group(1).split(',')
            self.parametros_actuales = [p.strip() for p in self.parametros_actuales]
            self.pc += 1
            return
        
        # Return
        if instruccion.startswith('return'):
            parts = instruccion.split()
            if len(parts) > 1:
                valor = self._evaluar_expresion(parts[1])
                if self.pila_llamadas:
                    var_retorno = self.pila_llamadas.pop()
                    self.variables[var_retorno] = valor
            # Fin de ejecución
            self.pc = len(self.codigo)
            return
        
        # Si no coincide con nada, avanzar
        self.pc += 1
    
    def _ejecutar_llamada(self, var_destino, expr):
        """Ejecuta una llamada a función"""
        # Extraer nombre de función
        match = re.match(r'call\s+(.+)', expr)
        if match:
            nombre_funcion = match.group(1).strip()
            
            # System.out.println - función especial
            if nombre_funcion == 'System.out.println':
                if hasattr(self, 'parametros_actuales') and self.parametros_actuales:
                    valores = [str(self._obtener_valor(p)) for p in self.parametros_actuales]
                    self.salida.append(' '.join(valores))
                    self.parametros_actuales = []
                else:
                    self.salida.append('')
                self.variables[var_destino] = None
            else:
                # Función desconocida, asignar 0
                self.variables[var_destino] = 0
    
    def _evaluar_expresion(self, expr):
        """Evalúa una expresión y retorna su valor"""
        expr = expr.strip()
        
        # Operadores binarios
        # Prioridad: *, /, % -> +, - -> ==, !=, <, >, <=, >= -> &&, ||
        
        # OR
        if '||' in expr:
            partes = expr.split('||')
            izq = self._evaluar_expresion(partes[0])
            der = self._evaluar_expresion(partes[1])
            return izq or der
        
        # AND
        if '&&' in expr:
            partes = expr.split('&&')
            izq = self._evaluar_expresion(partes[0])
            der = self._evaluar_expresion(partes[1])
            return izq and der
        
        # Comparaciones
        for op in ['==', '!=', '<=', '>=', '<', '>']:
            if op in expr:
                partes = expr.split(op)
                if len(partes) == 2:
                    izq = self._evaluar_expresion(partes[0])
                    der = self._evaluar_expresion(partes[1])
                    
                    if op == '==':
                        return izq == der
                    elif op == '!=':
                        return izq != der
                    elif op == '<':
                        return izq < der
                    elif op == '>':
                        return izq > der
                    elif op == '<=':
                        return izq <= der
                    elif op == '>=':
                        return izq >= der
        
        # Suma y resta (menor prioridad entre aritméticos)
        for op in ['+', '-']:
            # Buscar operador que no esté al inicio (para - unario)
            pos = expr.rfind(op)
            if pos > 0:
                izq = self._evaluar_expresion(expr[:pos])
                der = self._evaluar_expresion(expr[pos+1:])
                
                if op == '+':
                    return izq + der
                elif op == '-':
                    return izq - der
        
        # Multiplicación, división y módulo
        for op in ['*', '/', '%']:
            if op in expr:
                partes = expr.split(op)
                if len(partes) == 2:
                    izq = self._evaluar_expresion(partes[0])
                    der = self._evaluar_expresion(partes[1])
                    
                    if op == '*':
                        return izq * der
                    elif op == '/':
                        return izq / der if der != 0 else 0
                    elif op == '%':
                        return izq % der if der != 0 else 0
        
        # Operador unario NOT
        if expr.startswith('!'):
            operando = self._evaluar_expresion(expr[1:])
            return not operando
        
        # Operador unario - (negación)
        if expr.startswith('-') and len(expr) > 1:
            operando = self._evaluar_expresion(expr[1:])
            return -operando
        
        # Operador unario +
        if expr.startswith('+') and len(expr) > 1:
            return self._evaluar_expresion(expr[1:])
        
        # Valor literal o variable
        return self._obtener_valor(expr)
    
    def _obtener_valor(self, nombre):
        """Obtiene el valor de una variable o literal"""
        nombre = nombre.strip()
        
        # Literal numérico
        try:
            if '.' in nombre:
                return float(nombre)
            return int(nombre)
        except ValueError:
            pass
        
        # Booleanos
        if nombre.lower() == 'true':
            return True
        if nombre.lower() == 'false':
            return False
        
        # Variable
        if nombre in self.variables:
            return self.variables[nombre]
        
        # Variable no inicializada
        return 0
    
    def obtener_resultado(self):
        """Retorna el resultado de la ejecución"""
        resultado = '\n' + '='*70 + '\n'
        resultado += '▶️  RESULTADO DE EJECUCIÓN\n'
        resultado += '='*70 + '\n'
        
        if self.salida:
            resultado += '📤 Salida del programa:\n'
            resultado += '-'*70 + '\n'
            for linea in self.salida:
                resultado += f"{linea}\n"
        else:
            resultado += 'El programa no produjo salida.\n'
        
        resultado += '\n📊 Estado de variables:\n'
        resultado += '-'*70 + '\n'
        
        if self.variables:
            for var, valor in sorted(self.variables.items()):
                if not var.startswith('t'):  # No mostrar temporales
                    resultado += f"  {var} = {valor}\n"
        else:
            resultado += '  (no hay variables)\n'
        
        resultado += '\n📈 Estadísticas:\n'
        resultado += f"  • Instrucciones ejecutadas: {self.contador_instrucciones}\n"
        resultado += f"  • Variables creadas: {len([v for v in self.variables if not v.startswith('t')])}\n"
        resultado += f"  • Temporales usados: {len([v for v in self.variables if v.startswith('t')])}\n"
        
        resultado += '='*70 + '\n'
        return resultado