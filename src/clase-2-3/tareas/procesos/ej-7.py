#!/usr/bin/env python3
"""
Ejercicio 7: Crear múltiples procesos simultáneos
Objetivo: Observar la expansión del árbol de procesos y ejecución paralela
"""
import os
import time
import random

def main():
    print("=== Ejercicio 7: Múltiples procesos simultáneos ===")
    print("Creando 3 procesos hijos que trabajarán en paralelo...")
    print()
    
    num_hijos = 3
    
    # Crear múltiples procesos hijos
    for i in range(num_hijos):
        pid = os.fork()
        
        if pid == 0:
            # Código del proceso hijo
            tiempo_trabajo = random.randint(1, 4)  # Trabajo aleatorio entre 1-4 seg
            
            print(f"[HIJO {i}] PID: {os.getpid()}  Padre: {os.getppid()}")
            print(f"[HIJO {i}] Trabajaré por {tiempo_trabajo} segundos")
            
            # Simular trabajo con duración aleatoria
            for j in range(tiempo_trabajo):
                print(f"[HIJO {i}] Trabajando... {j+1}/{tiempo_trabajo}")
                time.sleep(1)
            
            print(f"[HIJO {i}] ¡Trabajo completado!")
            os._exit(i)  # Terminar con código de salida único
    
    # Proceso padre espera a todos los hijos
    print("[PADRE] Todos los hijos creados. Esperando que terminen...")
    
    # Recoger a todos los hijos
    for i in range(num_hijos):
        pid, status = os.wait()
        exit_code = os.WEXITSTATUS(status)
        print(f"[PADRE] Hijo {pid} terminó con código {exit_code}")
    
    print("[PADRE] Todos los procesos hijos completados")

if __name__ == "__main__":
    main()