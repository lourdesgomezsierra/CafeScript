# CafeScript

CafeScript es un compilador educativo escrito en Python para una materia de Teoria de la Computacion. El proyecto muestra cuatro fases fundamentales de un compilador y termina ejecutando un codigo generado simple, legible y orientado a demostracion.

## Fases

1. Analisis lexico
2. Analisis sintactico
3. Analisis semantico
4. Generacion de codigo

Flujo final:

```text
Codigo Fuente
      |
      v
Analisis Lexico
      |
      v
Tokens
      |
      v
Analisis Sintactico
      |
      v
Parse Tree
      |
      v
AST
      |
      v
Analisis Semantico
      |
      v
Codigo Generado
      |
      v
Ejecucion
```

## Instalacion

Requiere Python 3.10+ y Lark:

```bash
pip install -r requirements.txt
```

## Uso Basico

Ejecutar un programa CafeScript:

```bash
python cafescript/main.py cafescript/examples/funciones.cafe
```

Mostrar todas las fases y ejecutar:

```bash
python cafescript/main.py cafescript/examples/funciones.cafe --show-tokens --show-parse-tree --show-ast --show-semantic --show-code
```

Generar codigo sin ejecutar:

```bash
python cafescript/main.py cafescript/examples/funciones.cafe --show-code --no-execute
```

Opciones disponibles:

| Opcion | Descripcion |
| --- | --- |
| `--show-tokens` | Muestra los tokens generados por el lexer |
| `--show-parse-tree` | Muestra el Parse Tree generado por Lark |
| `--show-ast` | Muestra el AST simplificado |
| `--show-semantic` | Confirma que el analisis semantico termino sin errores |
| `--show-code` | Muestra el codigo generado |
| `--no-execute` | No ejecuta el codigo generado |

## Lenguaje

Palabras reservadas principales:

| CafeScript | Significado |
| --- | --- |
| `Pedido` | Declaracion de variable |
| `Servir` | Salida |
| `TomarPedido` | Entrada |
| `SiHay` | Condicional `if` |
| `SinoSi` | Condicional `elif` |
| `Sino` | Condicional `else` |
| `Disponible` | Booleano verdadero |
| `Agotado` | Booleano falso |
| `Receta` | Funcion |
| `Entregar` | Retorno |
| `MientrasAbierto` | Bucle `while` |
| `ParaCadaPedido` | Bucle `for` |

Operadores soportados:

```text
+ - * /
> < >= <= == !=
and or not
```

## Fase 1: Analisis Lexico

Archivo: `cafescript/lexer.py`

El lexer lee el codigo fuente caracter por caracter y produce tokens. Tambien detecta errores lexicos, como caracteres invalidos o strings sin cerrar.

Entrada:

```cafescript
Pedido cafe = 10
```

Comando:

```bash
python cafescript/main.py cafescript/examples/control_stock.cafe --show-tokens --no-execute
```

Salida esperada parcial:

```text
TOKEN(PEDIDO, Pedido)
TOKEN(ID, cafe)
TOKEN(ASSIGN, =)
TOKEN(NUMBER, 10)
```

## Fase 2: Analisis Sintactico

Archivos:

- `cafescript/cafescript.lark`
- `cafescript/main.py`
- `cafescript/ast_nodes.py`

La gramatica en Lark verifica que el programa tenga una estructura valida.

El **Parse Tree** muestra como el codigo encaja en las reglas concretas de la gramatica.

El **AST** es una version mas limpia del programa. Conserva el significado principal y elimina detalles sintacticos innecesarios.

Comandos:

```bash
python cafescript/main.py cafescript/examples/funciones.cafe --show-parse-tree --no-execute
python cafescript/main.py cafescript/examples/funciones.cafe --show-ast --no-execute
```

## Fase 3: Analisis Semantico

Archivo: `cafescript/semantic_analyzer.py`

Esta fase revisa que el programa tenga sentido despues de ser sintacticamente valido.

Verifica:

- Variables declaradas antes de usarse
- Funciones declaradas
- Uso correcto de identificadores
- Cantidad correcta de argumentos
- Algunos errores basicos de tipos

Comando:

```bash
python cafescript/main.py cafescript/examples/funciones.cafe --show-semantic --no-execute
```

Salida:

```text
=== ANALISIS SEMANTICO ===
Analisis semantico completado sin errores.
```

Ejemplos de errores:

```text
Error semantico: Variable 'x' no declarada.
Error semantico: Funcion 'calcularTotal' no declarada.
Error semantico: Funcion 'sumar' espera 2 argumentos y recibio 1.
```

## Fase 4: Generacion De Codigo

Archivos:

- `cafescript/code_generator.py`
- `cafescript/executor.py`

El generador recorre el AST y produce instrucciones simples.

Entrada:

```cafescript
Pedido cafe = 10
Servir("Cafe disponible", cafe)
```

Codigo generado:

```text
DECLARE cafe 10
PRINT "Cafe disponible" cafe
```

Entrada:

```cafescript
SiHay(cafe > 0){
    Servir("Hay cafe")
}
Sino{
    Servir("Sin stock")
}
```

Codigo generado:

```text
IF cafe > 0
    PRINT "Hay cafe"
ELSE
    PRINT "Sin stock"
END_IF
```

Comando:

```bash
python cafescript/main.py cafescript/examples/control_stock.cafe --show-code --no-execute
```

## Ejecucion

La ejecucion se realiza usando el codigo generado. No se usa una maquina virtual compleja.

Ejemplo:

```bash
python cafescript/main.py cafescript/examples/funciones.cafe --show-code
```

Salida esperada:

```text
=== CODIGO GENERADO ===
FUNCTION doble(valor)
    RETURN valor * 2
END_FUNCTION
FUNCTION esDisponible(stock)
    RETURN stock > 0
END_FUNCTION
DECLARE stock doble(4)
DECLARE disponible esDisponible(stock)
IF disponible
    PRINT "Stock calculado:" stock
ELSE
    PRINT "Sin stock"
END_IF
=== EJECUCION ===
Stock calculado: 8
```

## Arquitectura

```text
cafescript/
|-- lexer.py
|-- cafescript.lark
|-- ast_nodes.py
|-- semantic_analyzer.py
|-- code_generator.py
|-- executor.py
|-- main.py
`-- examples/
```
