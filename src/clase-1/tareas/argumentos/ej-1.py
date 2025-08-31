#!/usr/bin/env python3
"""
Ejercicio 1: Script básico con argumentos -i, -o y -n
"""
import argparse

def main():
    # Crear el parser
    parser = argparse.ArgumentParser(description="Procesador de archivos")
    
    # Argumentos requeridos
    parser.add_argument("-i", "--input", required=True, help="Archivo de entrada")
    parser.add_argument("-o", "--output", required=True, help="Archivo de salida")
    parser.add_argument("-n", "--num_lines", required=True, type=int, help="Número de líneas")
    
    args = parser.parse_args()
    
    # Mostrar valores recibidos
    print(f"Entrada: {args.input}")
    print(f"Salida: {args.output}")
    print(f"Líneas a procesar: {args.num_lines}")

if __name__ == "__main__":
    main()