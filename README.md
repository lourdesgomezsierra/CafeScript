# CafeScript

CafeScript es un compilador educativo escrito en Python para una materia de Teoria de la Computacion. El proyecto se enfoca solamente en cuatro fases fundamentales:

1. Analisis lexico
2. Analisis sintactico
3. Analisis semantico
4. Generacion de codigo intermedio

El compilador no ejecuta programas. Su salida final es una Representacion Intermedia (IR) en codigo de tres direcciones.

## Instalacion

Requiere Python 3.10+ y Lark:

```bash
pip install -r requirements.txt
```

## Uso

Compilar un programa CafeScript:

```bash
python cafescript/main.py cafescript/examples/control_stock.cafe
```

Mostrar todas las fases:

```bash
python cafescript/main.py cafescript/examples/control_stock.cafe --show-tokens --show-parse-tree --show-ast --show-ir
```

Opciones disponibles:

| Opcion | Salida |
| --- | --- |
| `--show-tokens` | Tokens generados por el lexer |
| `--show-parse-tree` | Arbol sintactico producido por Lark |
| `--show-ast` | AST simplificado |
| `--show-ir` | Codigo intermedio de tres direcciones |

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

## Ejemplo De Entrada

```cafescript
Pedido cafe = 10
Pedido te = 5
Pedido total = cafe + te

Servir("Total:", total)
```

## Fase 1: Analisis Lexico

Archivo principal: `cafescript/lexer.py`

El lexer lee el codigo fuente caracter por caracter y produce tokens. Tambien detecta errores lexicos, por ejemplo caracteres invalidos o strings sin cerrar.

Ejemplo:

```cafescript
Pedido cafe = 10
```

Salida con `--show-tokens`:

```text
TOKEN(PEDIDO, Pedido)
TOKEN(ID, cafe)
TOKEN(ASSIGN, =)
TOKEN(NUMBER, 10)
```

Tokens reconocidos:

- Identificadores
- Numeros enteros
- Strings
- Operadores aritmeticos
- Operadores relacionales
- Asignacion
- Parentesis
- Llaves
- Corchetes
- Comas
- Palabras reservadas

## Fase 2: Analisis Sintactico

Archivos principales:

- `cafescript/cafescript.lark`
- `cafescript/main.py`

Lark usa la gramatica de `cafescript.lark` para verificar que el programa tenga una estructura valida.

Con `--show-parse-tree` se muestra el Parse Tree. Este arbol conserva muchos detalles de la gramatica concreta, como reglas intermedias y estructura sintactica completa.

Con `--show-ast` se muestra el AST. El AST es una version mas limpia y semantica del programa: elimina detalles innecesarios del parse tree y conserva nodos como declaraciones, expresiones, condicionales y funciones.

Ejemplo conceptual:

```text
Parse Tree: muestra como el texto encaja en cada regla gramatical.
AST: muestra que operaciones representa el programa.
```

## Fase 3: Analisis Semantico

Archivo principal: `cafescript/semantic_analyzer.py`

Esta fase revisa que el programa tenga sentido mas alla de la sintaxis.

Verifica:

- Variables declaradas antes de usarse
- Funciones declaradas antes de llamarse
- Cantidad correcta de argumentos
- Uso valido de identificadores
- Algunos errores basicos de tipos

Ejemplos de errores:

```text
Variable 'x' no declarada.
Funcion 'calcularTotal' no declarada.
Funcion 'sumar' espera 2 argumentos y recibio 1.
```

## Fase 4: Generacion De Codigo Intermedio

Archivo principal: `cafescript/intermediate_representation.py`

Esta fase convierte el AST en una Representacion Intermedia (IR) de tres direcciones. La IR usa temporales automaticos para descomponer expresiones.

Entrada:

```cafescript
Pedido total = cafe + te
```

Salida con `--show-ir`:

```text
t1 = cafe + te
total = t1
```

Para condicionales y ciclos, la IR usa etiquetas y saltos:

```text
JUMP_IF_FALSE t1 if_next_1
PRINT t2
JUMP if_end_2
if_next_1:
if_end_2:
```

## Arquitectura

```text
cafescript/
|-- lexer.py
|-- cafescript.lark
|-- ast_nodes.py
|-- semantic_analyzer.py
|-- intermediate_representation.py
|-- main.py
|-- examples/
`-- resultados/
```

## Flujo Del Compilador

```text
Codigo Fuente
      |
      v
Analisis Lexico
      |
      v
Lista de Tokens
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
Representacion Intermedia (IR)
```
