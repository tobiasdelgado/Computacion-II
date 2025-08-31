#!/usr/bin/env python3
"""
Ejercicio 1: Crear un proceso hijo y mostrar los PID
Objetivo: Utilizar fork() y comprender la relación padre-hijo
"""
import os

def main():
    print("=== Ejercicio 1: Proceso padre e hijo ===")
    
    # fork() crea una copia exacta del proceso actual
    # Retorna 0 en el hijo, PID del hijo en el padre
    pid = os.fork()
    
    if pid == 0:
        # Código que ejecuta el proceso hijo
        print("[HIJO] PID:", os.getpid(), "PPID:", os.getppid())
    else:
        # Código que ejecuta el proceso padre
        print("[PADRE] PID:", os.getpid(), "Hijo:", pid)
        # Esperar a que termine el hijo para evitar zombies
        os.wait()

if __name__ == "__main__":
    main()