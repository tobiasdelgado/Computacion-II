#!/usr/bin/env python3
"""
Ejercicio 2: Validación de número positivo
"""
import argparse

def check_positive(value):
    # Convertir a entero y validar que sea positivo
    num = int(value)
    if num <= 0:
        raise argparse.ArgumentTypeError("Debe ser un entero positivo")
    return num

def main():
    parser = argparse.ArgumentParser(description="Procesador con validación")
    
    parser.add_argument("-i", "--input", required=True, help="Archivo de entrada")
    parser.add_argument("-o", "--output", required=True, help="Archivo de salida")
    # type: función de validación personalizada
    # Otros valores: int, float, str, bool, o cualquier función que tome string y retorne el tipo deseado
    parser.add_argument("-n", "--num_lines", type=check_positive, 
                       required=True, help="Número de líneas (positivo)")
    
    args = parser.parse_args()
    
    print(f"Entrada: {args.input}")
    print(f"Salida: {args.output}")
    print(f"Líneas a procesar: {args.num_lines}")

if __name__ == "__main__":
    main()