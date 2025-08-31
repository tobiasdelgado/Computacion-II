#!/usr/bin/env python3
"""
Ejercicio 5: Producir y observar un proceso zombi
Objetivo: Generar un proceso zombi temporal para su inspección
IMPORTANTE: Ejecuta 'ps -el | grep Z' en otra terminal durante la pausa
"""
import os
import time

def main():
    print("=== Ejercicio 5: Creando un proceso zombi ===")
    print("INSTRUCCIONES:")
    print("1. Ejecuta este script")
    print("2. En otra terminal, ejecuta: ps -el | grep Z")
    print("3. Busca procesos con estado 'Z' (zombie)")
    print()
    
    pid = os.fork()
    
    if pid == 0:
        # Proceso hijo termina rápidamente
        print("[HIJO] PID:", os.getpid())
        print("[HIJO] Finalizando...")
        os._exit(0)  # El hijo termina pero queda como zombie
    else:
        # Proceso padre NO llama a wait() inmediatamente
        print("[PADRE] No llamaré a wait() aún.")
        print(f"[PADRE] El hijo {pid} se convertirá en zombie")
        print("[PADRE] Verifica con 'ps -el | grep Z' en otra terminal")
        
        # Pausa para poder observar el zombie
        for i in range(15, 0, -1):
            print(f"[PADRE] Esperando {i} segundos...")
            time.sleep(1)
        
        # Finalmente limpiar el zombie
        print("[PADRE] Limpiando zombie con wait()...")
        os.wait()
        print("[PADRE] Zombie eliminado")

if __name__ == "__main__":
    main()