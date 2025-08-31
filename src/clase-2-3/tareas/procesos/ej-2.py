#!/usr/bin/env python3
"""
Ejercicio 2: Crear dos hijos desde el mismo padre
Objetivo: Ver cómo un solo padre puede lanzar múltiples procesos hijos
"""
import os

def main():
    print("=== Ejercicio 2: Múltiples procesos hijos ===")
    
    # Crear dos procesos hijos en un bucle
    for i in range(2):
        pid = os.fork()
        
        if pid == 0:
            # Código del proceso hijo
            print(f"[HIJO {i}] PID: {os.getpid()}  Padre: {os.getppid()}")
            # os._exit(0) termina inmediatamente sin cleanup
            os._exit(0)
    
    # El padre espera a que terminen ambos hijos
    # wait() bloquea hasta que termine un hijo
    for _ in range(2):
        child_pid = os.wait()
        print(f"[PADRE] Hijo {child_pid[0]} terminó")

if __name__ == "__main__":
    main()