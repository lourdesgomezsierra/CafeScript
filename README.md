# CafeScript

CafeScript es un compilador educativo escrito en Python. Define un lenguaje con tematica de cafeteria y recorre las fases clasicas de un compilador academico: parsing, AST, analisis semantico, representacion intermedia, optimizacion, generacion de instrucciones para una maquina de pila e interpretacion.

## Instalacion

Requiere Python 3.10+ y Lark:

```bash
pip install lark
```

## Ejecutar

```bash
python cafescript/main.py cafescript/examples/control_stock.cafe
```

Para ver las fases intermedias:

```bash
python cafescript/main.py cafescript/examples/control_stock.cafe --show-ast --show-ir --show-optimized-ir --show-bytecode
```

## Lenguaje

Palabras clave principales:

| CafeScript | Significado |
| --- | --- |
| `Pedido` | declaracion de variable |
| `Servir` | salida por pantalla |
| `TomarPedido` | entrada por teclado |
| `SiHay` | `if` |
| `SinoSi` | `elif` |
| `Sino` | `else` |
| `Disponible` | `True` |
| `Agotado` | `False` |
| `Receta` | funcion |
| `Entregar` | retorno |
| `MientrasAbierto` | `while` |
| `ParaCadaPedido` | `for` |

Operadores soportados:

```text
+ - * /
> < >= <= == !=
and or not
```

## Ejemplo

```cafescript
Pedido cafe = 10

Servir("Control de stock")

SiHay(cafe > 0){
    Servir("Hay cafe disponible")
}
Sino{
    Servir("Sin stock")
}

Pedido cliente = TomarPedido("Nombre:")
Servir("Bienvenido", cliente)

Receta calcularTotal(precio, cantidad){
    Entregar precio * cantidad
}

Pedido total = calcularTotal(1200, 3)
Servir("Total:", total)
```

## Fases Del Compilador

1. **Analisis lexico y sintactico**: Lark lee `cafescript.lark` y produce un arbol parseado.
2. **AST**: `ast_nodes.py` define nodos estructurados; `main.py` transforma el parse tree en AST.
3. **Analisis semantico**: `semantic_analyzer.py` verifica variables y funciones declaradas, aridad de llamadas y errores basicos de tipos constantes.
4. **IR**: `intermediate_representation.py` genera codigo de tres direcciones con temporales y etiquetas.
5. **Optimizacion**: `ir_optimizer.py` aplica constant folding, constant propagation y dead code elimination.
6. **Maquina de pila**: `stack_instructions.py` traduce la IR a instrucciones.
7. **Interpretacion**: `stack_machine.py` ejecuta las instrucciones.

## Estructura

```text
cafescript/
|-- main.py
|-- cafescript.lark
|-- ast_nodes.py
|-- semantic_analyzer.py
|-- intermediate_representation.py
|-- ir_optimizer.py
|-- stack_instructions.py
|-- stack_machine.py
|-- examples/
|   |-- control_stock.cafe
|   |-- gestion_pedidos.cafe
|   |-- facturacion.cafe
|   |-- funciones.cafe
|   `-- ciclos.cafe
`-- resultados/
```

## Notas Didacticas

CafeScript no busca competir con lenguajes reales. Su objetivo es mostrar como se conectan las partes de un compilador:

- La gramatica define que programas son validos.
- El AST elimina detalles sintacticos y deja una estructura semantica.
- La IR separa el frontend del backend.
- Las optimizaciones trabajan sobre una forma simple y uniforme.
- La maquina de pila ejecuta instrucciones pequenas y faciles de inspeccionar.
