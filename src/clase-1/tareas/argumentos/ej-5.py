#!/usr/bin/env python3
"""
Ejercicio 5: Implementar ayuda completa
Script completo con todos los argumentos y documentación detallada
"""
import argparse

def check_positive(value):
    """Valida que el valor sea un entero positivo"""
    num = int(value)
    if num <= 0:
        raise argparse.ArgumentTypeError("Debe ser un entero positivo")
    return num

def main():
    # Parser con opciones avanzadas de formato
    # epilog: texto que aparece después de la ayuda de argumentos
    # formatter_class: controla el formato del texto de ayuda
    # Otros valores: ArgumentDefaultsHelpFormatter, RawTextHelpFormatter, MetavarTypeHelpFormatter
    parser = argparse.ArgumentParser(
        description="Procesador de archivos de texto con opciones avanzadas",
        epilog="""
Ejemplos de uso:
  %(prog)s -i entrada.txt -o salida.txt -n 100
  %(prog)s -i data.txt -o output.csv -n 50 --format csv --verbose
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Argumentos obligatorios con descripciones detalladas
    # metavar: nombre que aparece en la ayuda en lugar del nombre del argumento
    parser.add_argument("-i", "--input", required=True, 
                       metavar="ARCHIVO",
                       help="Archivo de entrada que será procesado")
    parser.add_argument("-o", "--output", required=True,
                       metavar="ARCHIVO", 
                       help="Archivo donde se guardará el resultado")
    parser.add_argument("-n", "--num_lines", type=check_positive, 
                       required=True, metavar="N",
                       help="Número de líneas a procesar (debe ser positivo)")
    
    # Argumentos opcionales
    parser.add_argument("--verbose", action="store_true", 
                       help="Mostrar información detallada durante el procesamiento")
    # %(default)s: placeholder que muestra el valor por defecto en la ayuda
    parser.add_argument("--format", choices=["txt", "csv", "json"], 
                       default="txt", metavar="FORMATO",
                       help="Formato del archivo de salida (default: %(default)s)")
    parser.add_argument("--encoding", default="utf-8", metavar="CODIFICACION",
                       help="Codificación de caracteres (default: %(default)s)")
    
    # action="version": muestra la versión y termina el programa
    # %(prog)s: placeholder que se reemplaza por el nombre del programa
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    
    args = parser.parse_args()
    
    # Procesar según configuración
    if args.verbose:
        print("=== PROCESADOR DE ARCHIVOS v1.0 ===")
        print(f"Archivo de entrada: {args.input}")
        print(f"Archivo de salida: {args.output}")
        print(f"Líneas a procesar: {args.num_lines}")
        print(f"Formato de salida: {args.format}")
        print(f"Codificación: {args.encoding}")
        print("Iniciando procesamiento...")
    
    print(f"Procesando {args.num_lines} líneas de {args.input} -> {args.output}")
    print("Procesamiento completado.")

if __name__ == "__main__":
    main()