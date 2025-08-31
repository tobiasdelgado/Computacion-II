#!/usr/bin/env python3

# Ejercicio 1 · Nivel Básico
#
# Objetivo: comprobar la creación de procesos y la correcta espera del padre.
#
# Enunciado: escribe un programa que cree dos procesos hijo mediante multiprocessing.Process, 
# cada uno imprimiendo su propio pid. El proceso padre debe esperar a que ambos terminen 
# y luego imprimir un mensaje de cierre.

from multiprocessing import Process, current_process
import os
import time

def hijo(numero):
    """
    Función que ejecutará cada proceso hijo.
    
    En multiprocessing, cada Process() crea un proceso completamente separado
    con su propio espacio de memoria, a diferencia de threading donde comparten memoria.
    
    current_process().pid nos da el PID real del proceso del sistema operativo.
    """
    # Obtener información del proceso actual
    pid_proceso = current_process().pid
    pid_os = os.getpid()  # Alternativa usando os.getpid()
    
    print(f"[Hijo {numero}] PID desde multiprocessing: {pid_proceso}")
    print(f"[Hijo {numero}] PID desde os.getpid(): {pid_os}")
    print(f"[Hijo {numero}] Nombre del proceso: {current_process().name}")
    
    # Simular algo de trabajo
    time.sleep(numero+4)
    print(f"[Hijo {numero}] Terminando...")

def main():
    """
    Proceso principal que crea y maneja los procesos hijos.
    """
    print("=== Ejercicio 1: Creación básica de procesos ===")
    print(f"[Padre] PID del proceso padre: {current_process().pid}")
    print(f"[Padre] PID desde os.getpid(): {os.getpid()}")
    
    # Crear dos procesos hijo
    # Process(target=funcion, args=tupla_argumentos)
    procesos = []
    for i in range(2):
        proceso = Process(target=hijo, args=(i + 1,))
        procesos.append(proceso)
        print(f"[Padre] Proceso hijo {i + 1} creado")
    
    print("\n[Padre] Iniciando procesos hijos...")
    
    # Iniciar todos los procesos
    # start() lanza el proceso en paralelo, no bloquea
    for proceso in procesos:
        proceso.start()
        print(f"[Padre] Proceso {proceso.name} iniciado con PID {proceso.pid}")
    
    print("\n[Padre] Esperando a que terminen los hijos...")
    
    # Esperar a que todos los procesos terminen
    # join() bloquea hasta que el proceso termine (equivalente a wait() en C)
    for i, proceso in enumerate(procesos):
        print(f"[Padre] Esperando al hijo {i + 1}...")
        proceso.join()  # Esperar a que termine
        print(f"[Padre] Hijo {i + 1} terminado")
    
    print(f"\n[Padre] Todos los hijos han terminado")
    print(f"[Padre] PID padre: {current_process().pid}")
    print("[Padre] Programa completado ✅")

if __name__ == '__main__':
    # La protección if __name__ == '__main__' es OBLIGATORIA en multiprocessing
    # Sin ella, los procesos hijos intentarían ejecutar todo el script recursivamente
    main()