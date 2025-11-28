# Compilador-Java

Un compilador educativo para el lenguaje Java desarrollado con fines de aprendizaje.

> **Nota**: Este proyecto está actualmente en desarrollo. La documentación a continuación describe la funcionalidad planificada.

## Descripción

Este proyecto implementa un compilador para el lenguaje de programación Java. El compilador realiza las siguientes funciones principales:

1. **Análisis Léxico**: Tokeniza el código fuente Java, identificando palabras clave, identificadores, operadores, literales y otros elementos del lenguaje.

2. **Análisis Sintáctico**: Construye un árbol de sintaxis abstracta (AST) a partir de los tokens, verificando que el código siga las reglas gramaticales de Java.

3. **Análisis Semántico**: Valida el significado del código, incluyendo verificación de tipos, resolución de nombres y otras comprobaciones contextuales.

4. **Generación de Código**: Produce código intermedio o bytecode ejecutable a partir del AST validado.

## Requisitos

- Java Development Kit (JDK) 11 o superior
- Maven 3.6+ (opcional, para gestión de dependencias)

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/E1P3LON/Compilador-Java.git

# Entrar al directorio del proyecto
cd Compilador-Java

# Compilar el proyecto (cuando el código esté disponible)
# javac -d bin src/*.java
```

## Uso (Planificado)

Una vez implementado el compilador, podrás usarlo de la siguiente manera:

### Compilar un archivo Java

```bash
# Sintaxis básica
java -jar compilador.jar <archivo_fuente.java>

# Ejemplo
java -jar compilador.jar MiPrograma.java
```

### Opciones disponibles

| Opción | Descripción |
|--------|-------------|
| `-o <archivo>` | Especifica el nombre del archivo de salida |
| `-v` | Modo verbose, muestra información detallada del proceso de compilación |
| `-h` | Muestra la ayuda y las opciones disponibles |

### Ejemplo de código fuente

```java
// Ejemplo de un programa simple que el compilador puede procesar
public class HolaMundo {
    public static void main(String[] args) {
        System.out.println("¡Hola, Mundo!");
    }
}
```

## Estructura del Proyecto (Planificada)

```
Compilador-Java/
├── src/                    # Código fuente del compilador
│   ├── lexer/             # Analizador léxico
│   ├── parser/            # Analizador sintáctico
│   ├── semantic/          # Analizador semántico
│   └── codegen/           # Generador de código
├── tests/                  # Pruebas unitarias
├── examples/              # Ejemplos de programas Java
├── docs/                  # Documentación adicional
├── README.md              # Este archivo
└── LICENSE                # Licencia MIT
```

## Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Haz un fork del repositorio
2. Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Realiza tus cambios y haz commit (`git commit -am 'Agrega nueva funcionalidad'`)
4. Sube tu rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## Autor

Desarrollado por [E1P3LON](https://github.com/E1P3LON)