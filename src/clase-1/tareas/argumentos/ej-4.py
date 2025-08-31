#!/usr/bin/env python3
"""
Ejercicio 4: Argumentos obligatorios y opcionales
"""
import argparse

def check_positive(value):
    num = int(value)
    if num <= 0:
        raise argparse.ArgumentTypeError("Debe ser un entero positivo")
    return num

def main():
    parser = argparse.ArgumentParser(description="Argumentos obligatorios y opcionales")
    
    # Argumentos obligatorios
    parser.add_argument("-i", "--input", required=True, help="Archivo de entrada")
    parser.add_argument("-o", "--output", required=True, help="Archivo de salida")
    parser.add_argument("-n", "--num_lines", type=check_positive, 
                       required=True, help="Número de líneas (positivo)")
    
    # Argumentos opcionales
    parser.add_argument("--verbose", action="store_true", 
                       help="Mostrar mensajes detallados")
    # choices: limita los valores permitidos a una lista específica
    parser.add_argument("--format", choices=["txt", "csv", "json"], 
                       default="txt", help="Formato de salida (default: txt)")
    # default: valor que se usa si no se proporciona el argumento
    parser.add_argument("--encoding", default="utf-8", 
                       help="Codificación de archivos (default: utf-8)")
    
    args = parser.parse_args()
    
    if args.verbose:
        print("=== CONFIGURACIÓN ===")
        print(f"Entrada: {args.input}")
        print(f"Salida: {args.output}")
        print(f"Líneas: {args.num_lines}")
        print(f"Formato: {args.format}")
        print(f"Codificación: {args.encoding}")
    else:
        print(f"Procesando {args.input} -> {args.output}")

if __name__ == "__main__":
    main()