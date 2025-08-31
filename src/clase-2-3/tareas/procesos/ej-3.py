#!/usr/bin/env python3
"""
Ejercicio 3: Ejecutar otro programa con exec()
Objetivo: Reemplazar el proceso hijo con un nuevo programa externo
"""
import os

def main():
    print("=== Ejercicio 3: Usando exec() para ejecutar otro programa ===")
    
    pid = os.fork()
    
    if pid == 0:
        # Proceso hijo: reemplazar con el comando 'ls'
        print("[HIJO] Ejecutando 'ls -l'...")
        # execlp() reemplaza completamente el proceso actual
        # No hay vuelta atrás - el código después de exec() no se ejecuta
        os.execlp("ls", "ls", "-l")
    else:
        # Proceso padre espera a que termine el hijo
        print("[PADRE] Esperando que termine el comando...")
        status = os.wait()
        print(f"[PADRE] Comando terminó con código: {status[1]}")

if __name__ == "__main__":
    main()