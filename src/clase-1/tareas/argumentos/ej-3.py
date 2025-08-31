#!/usr/bin/env python3
"""
Ejercicio 3: Agregar opción verbose
"""
import argparse

def check_positive(value):
    num = int(value)
    if num <= 0:
        raise argparse.ArgumentTypeError("Debe ser un entero positivo")
    return num

def main():
    parser = argparse.ArgumentParser(description="Procesador con modo verbose")
    
    parser.add_argument("-i", "--input", required=True, help="Archivo de entrada")
    parser.add_argument("-o", "--output", required=True, help="Archivo de salida")
    parser.add_argument("-n", "--num_lines", type=check_positive, 
                       required=True, help="Número de líneas (positivo)")
    # action="store_true": guarda True si se pasa la opción, False si no
    # Otros valores de action: "store_false", "store_const", "append", "count", "version"
    parser.add_argument("--verbose", action="store_true", 
                       help="Mostrar mensajes detallados")
    
    args = parser.parse_args()
    
    if args.verbose:
        print("Modo detallado activado")
        print(f"Procesando archivo: {args.input}")
        print(f"Escribiendo a: {args.output}")
        print(f"Procesando {args.num_lines} líneas")
    else:
        print(f"Procesando {args.input} -> {args.output} ({args.num_lines} líneas)")

if __name__ == "__main__":
    main()