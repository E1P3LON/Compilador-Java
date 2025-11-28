# Compilador-Java

Este proyecto es un compilador implementado en Java. Su objetivo es tomar como entrada un programa escrito en un lenguaje fuente definido para la materia (o para el proyecto) y transformarlo en una representación de salida (por ejemplo, código intermedio, código ensamblador, bytecode o simplemente verificar su corrección sintáctica y semántica).

## ¿Qué hace el compilador?

En términos generales, el compilador realiza las siguientes etapas:

1. **Análisis léxico (scanner / lexer)**  
   - Lee el archivo de entrada carácter por carácter.  
   - Agrupa los caracteres en **tokens** (palabras clave, identificadores, números, operadores, símbolos, etc.).  
   - Detecta errores léxicos (caracteres no válidos o secuencias ilegales).

2. **Análisis sintáctico (parser)**  
   - Recibe la lista de tokens producida por el análisis léxico.  
   - Verifica que la secuencia de tokens cumpla las reglas gramaticales del lenguaje (la gramática).  
   - Construye una estructura como un **árbol sintáctico** o **árbol de derivación**.  
   - Informa errores de sintaxis (por ejemplo, paréntesis faltantes, palabras clave mal ubicadas, etc.).

3. **Análisis semántico**  
   - Comprueba reglas de significado que no se pueden verificar sólo con la gramática.  
   - Ejemplos de comprobaciones:
     - Variables declaradas antes de usarse.  
     - Tipos compatibles en asignaciones y operaciones.  
     - Cantidad y tipo de parámetros correctos en llamadas a funciones.  
   - Puede construir y mantener **tablas de símbolos**.

4. **Generación de código / salida**  
   - A partir del árbol sintáctico (y la información semántica), genera:
     - Código intermedio, o  
     - Código de máquina/ensamblador, o  
     - Algún tipo de representación/resultado que se quiera para el proyecto (por ejemplo, una versión traducida del programa o simplemente un reporte de análisis).
   - En algunos proyectos académicos, esta etapa puede limitarse a generar una salida intermedia o un árbol anotado.

5. **Manejo de errores y reporte**  
   - En cada etapa, el compilador informa errores (léxicos, sintácticos y semánticos).  
   - Idealmente, proporciona mensajes claros e indica la línea y posición aproximada del error.  
   - Puede continuar analizando para reportar múltiples errores en una sola ejecución.

## Estructura general del proyecto (ejemplo)

Aunque la organización exacta puede variar, típicamente el proyecto se divide en:

- `lexer/` o clases relacionadas con **análisis léxico**.  
- `parser/` o clases relacionadas con **análisis sintáctico**.  
- Clases para el **árbol sintáctico abstracto (AST)**.  
- Módulos para **análisis semántico** y manejo de tablas de símbolos.  
- Módulo de **generación de código** (si aplica).  
- Una clase `Main` (o similar) que:
  - Lee el archivo de entrada.
  - Ejecuta el lexer y el parser.
  - Llama a las fases posteriores (semántica, generación de código).
  - Muestra resultados y errores por consola o archivo.

## Cómo usar el compilador (ejemplo)

> Nota: ajusta esta sección según la forma real de ejecutar tu proyecto.

1. Compila el proyecto con Maven, Gradle o desde tu IDE.  
2. Ejecuta el programa indicando como parámetro el archivo fuente a compilar. Por ejemplo:

```bash
java -jar Compilador-Java.jar programaFuente.txt
```

3. Revisa en la consola (o en los archivos de salida configurados) los mensajes de:
   - Errores léxicos, sintácticos o semánticos.  
   - Resultado de la compilación (éxito o fallo).  
   - Código generado, si corresponde.

## Objetivo del proyecto

Este compilador sirve tanto como:

- **Herramienta didáctica**, para comprender cómo se implementan las diferentes fases de un compilador en Java.  
- **Base de experimentación**, para:
  - Probar nuevas reglas del lenguaje.  
  - Agregar optimizaciones.  
  - Cambiar o ampliar la generación de código.

Puedes adaptar y extender este README a medida que el proyecto crezca, agregando detalles concretos sobre:

- La gramática usada.  
- El tipo de código generado.  
- Ejemplos de programas de entrada y su salida correspondiente.  
- Dependencias o herramientas adicionales (por ejemplo, ANTLR, JFlex, CUP, etc.).
