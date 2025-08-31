# **Capítulo 4: Guía sobre `getopt` y `argparse` en Python**

En la construcción de programas en Python, una de las necesidades más frecuentes es la de recibir información desde la línea de comandos. Esta práctica resulta fundamental porque permite que un mismo código pueda adaptarse a distintos contextos de ejecución sin ser modificado directamente. El mecanismo más sencillo para acceder a esos parámetros es a través de `sys.argv`, que ofrece una lista con todos los argumentos proporcionados al script. Si bien este método básico resulta suficiente en ejemplos simples, rápidamente se vuelve limitado cuando se requiere algo más complejo, como validar tipos de datos, asociar valores a opciones o mostrar mensajes de ayuda.

## Ejemplo con sys.argv

```python
import sys

# script.py
print(f"Nombre del script: {sys.argv[0]}")
print(f"Argumentos: {sys.argv[1:]}")

if len(sys.argv) > 1:
    print(f"Primer argumento: {sys.argv[1]}")
```

Ejecución:
```bash
python script.py archivo.txt --verbose
# Salida:
# Nombre del script: script.py
# Argumentos: ['archivo.txt', '--verbose']
# Primer argumento: archivo.txt
```

Un ejemplo clásico muestra cómo, al ejecutar un programa desde la terminal, `sys.argv` captura los parámetros y los devuelve como una lista. Sin embargo, este enfoque carece de un sistema para diferenciar entre argumentos posicionales y opcionales, no incluye validación automática y tampoco ofrece la posibilidad de generar una ayuda integrada. Estas limitaciones fueron la razón por la cual Python incorporó módulos más potentes: `getopt` y `argparse`.

El primero de ellos, `getopt`, es heredero directo de la tradición del lenguaje C. Su filosofía consiste en brindar un control detallado y explícito al programador sobre cómo se analizan los argumentos. La forma de trabajo consiste en definir opciones cortas y largas, así como los posibles valores que cada una puede recibir. A través de este mecanismo, el script puede interpretar de manera estructurada la entrada del usuario. La desventaja es que el código necesario tiende a ser más extenso y menos intuitivo, pues el programador debe encargarse de tareas adicionales como mostrar mensajes de ayuda o verificar la validez de los datos. Por ello, `getopt` suele considerarse más adecuado en programas muy simples o en contextos donde se busca mantener compatibilidad con proyectos escritos originalmente en C.

## Ejemplo con getopt

```python
import sys
import getopt

def main():
    try:
        # Opciones cortas: 'ho:v' significa -h, -o con valor, -v
        # Opciones largas: ['help', 'output=', 'verbose']
        opts, args = getopt.getopt(sys.argv[1:], 'ho:v', ['help', 'output=', 'verbose'])
    except getopt.GetoptError as err:
        print(f"Error: {err}")
        sys.exit(2)
    
    output = None
    verbose = False
    
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print("Uso: script.py -o archivo [-v]")
            sys.exit()
        elif opt in ('-o', '--output'):
            output = arg
        elif opt in ('-v', '--verbose'):
            verbose = True
    
    print(f"Archivo de salida: {output}")
    print(f"Modo verboso: {verbose}")
    print(f"Argumentos restantes: {args}")

if __name__ == "__main__":
    main()
```

Ejecución:
```bash
python script.py -o resultado.txt -v archivo1.txt archivo2.txt
# Salida:
# Archivo de salida: resultado.txt
# Modo verboso: True
# Argumentos restantes: ['archivo1.txt', 'archivo2.txt']
```

En contraposición, Python ofrece `argparse`, un módulo diseñado para simplificar y modernizar el tratamiento de los argumentos de línea de comandos. La principal diferencia es que `argparse` no solo analiza lo que el usuario escribe en la terminal, sino que además proporciona automáticamente mensajes de ayuda, valida el tipo de datos ingresado y permite establecer valores por defecto. Su sintaxis resulta mucho más clara y declarativa: en lugar de construir manualmente cada validación, el programador define los parámetros esperados y el propio módulo se encarga de gestionar la lógica necesaria. Por ejemplo, basta con indicar que un argumento debe ser un número entero para que `argparse` rechace de inmediato entradas inválidas, evitando así errores en tiempo de ejecución.

## Ejemplo básico con argparse

```python
import argparse

def main():
    parser = argparse.ArgumentParser(description='Procesador de archivos')
    
    # Argumento posicional (obligatorio)
    parser.add_argument('archivo', help='Archivo a procesar')
    
    # Argumentos opcionales
    parser.add_argument('-o', '--output', help='Archivo de salida')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='Mostrar información detallada')
    parser.add_argument('-n', '--numero', type=int, default=10,
                        help='Número de líneas (por defecto: 10)')
    
    args = parser.parse_args()
    
    print(f"Archivo: {args.archivo}")
    print(f"Salida: {args.output}")
    print(f"Verboso: {args.verbose}")
    print(f"Número: {args.numero}")

if __name__ == "__main__":
    main()
```

Ejecución:
```bash
python script.py archivo.txt -o salida.txt -v -n 20
# Salida:
# Archivo: archivo.txt
# Salida: salida.txt
# Verboso: True
# Número: 20
```

## Ejemplo avanzado con argparse

```python
import argparse

def main():
    parser = argparse.ArgumentParser(description='Calculadora de línea de comandos')
    
    # Subcomandos
    subparsers = parser.add_subparsers(dest='operacion', help='Operaciones disponibles')
    
    # Subcomando suma
    suma_parser = subparsers.add_parser('suma', help='Sumar números')
    suma_parser.add_argument('numeros', nargs='+', type=float, help='Números a sumar')
    
    # Subcomando multiplicar
    mult_parser = subparsers.add_parser('mult', help='Multiplicar números')
    mult_parser.add_argument('numeros', nargs=2, type=float, help='Dos números a multiplicar')
    
    # Opciones globales
    parser.add_argument('--precision', type=int, default=2,
                        help='Decimales de precisión (por defecto: 2)')
    
    args = parser.parse_args()
    
    if args.operacion == 'suma':
        resultado = sum(args.numeros)
        print(f"Suma: {resultado:.{args.precision}f}")
    elif args.operacion == 'mult':
        resultado = args.numeros[0] * args.numeros[1]
        print(f"Multiplicación: {resultado:.{args.precision}f}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

Ejecución:
```bash
python calculadora.py suma 1.5 2.3 4.7 --precision 3
# Salida: Suma: 8.500

python calculadora.py mult 3.14 2.0
# Salida: Multiplicación: 6.28
```

Otra de sus ventajas radica en la distinción entre argumentos posicionales y opcionales. Los primeros corresponden a valores que el usuario debe ingresar en un orden específico, mientras que los opcionales permiten mayor flexibilidad al estar acompañados de prefijos como `-` o `--`. Esta distinción favorece la legibilidad del programa y hace más comprensible la interacción desde la terminal. Como complemento, la opción `--help` genera de manera automática una guía detallada del uso del script, algo que con `getopt` debe implementarse manualmente.

En definitiva, aunque ambos módulos cumplen la misma función general, la experiencia que ofrecen es muy distinta. `getopt` se caracteriza por su sencillez y su cercanía con la tradición de C, lo que lo vuelve apropiado en casos mínimos o cuando se busca mantener compatibilidad con código clásico. `argparse`, en cambio, se presenta como la herramienta moderna y robusta, recomendada para la mayoría de los desarrollos en Python, especialmente cuando se requieren validaciones, mensajes de ayuda automáticos o configuraciones más elaboradas.

La elección entre uno u otro depende entonces del contexto y de los objetivos del proyecto. Si el propósito es escribir un script elemental y rápido, `getopt` puede ser suficiente. Pero cuando el programa está destinado a ser usado por otros, a crecer en complejidad o simplemente a ofrecer una interfaz más clara y profesional, `argparse` se convierte en la opción natural.

