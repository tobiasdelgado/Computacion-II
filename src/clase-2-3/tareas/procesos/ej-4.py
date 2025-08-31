#!/usr/bin/env python3
"""
Ejercicio 4: Crear procesos secuenciales
Objetivo: Lanzar un hijo, esperar su finalización, y luego crear otro
"""
import os
import time

def crear_hijo(nombre):
    """Crea un proceso hijo con un nombre específico"""
    print(f"[PADRE] Creando hijo {nombre}...")
    
    pid = os.fork()
    
    if pid == 0:
        # Proceso hijo
        print(f"[HIJO {nombre}] PID: {os.getpid()}")
        print(f"[HIJO {nombre}] Trabajando...")
        time.sleep(1)  # Simular trabajo
        print(f"[HIJO {nombre}] Terminando")
        os._exit(0)
    else:
        # Proceso padre espera al hijo antes de continuar
        os.wait()
        print(f"[PADRE] Hijo {nombre} completado\n")

def main():
    print("=== Ejercicio 4: Procesos secuenciales ===")
    
    # Crear hijos uno después del otro (secuencial)
    crear_hijo("A")
    crear_hijo("B")
    crear_hijo("C")
    
    print("[PADRE] Todos los procesos completados")

if __name__ == "__main__":
    main()