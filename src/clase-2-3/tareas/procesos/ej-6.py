#!/usr/bin/env python3
"""
Ejercicio 6: Crear un proceso huérfano
Objetivo: Observar la adopción de procesos por init/systemd
IMPORTANTE: Ejecuta 'ps -ef | grep python' para ver el cambio de PPID
"""
import os
import time

def main():
    print("=== Ejercicio 6: Creando un proceso huérfano ===")
    print("INSTRUCCIONES:")
    print("1. Ejecuta este script")
    print("2. En otra terminal, ejecuta: ps -ef | grep python")
    print("3. Observa cómo cambia el PPID del proceso hijo")
    print()
    
    pid = os.fork()
    
    if pid > 0:
        # Proceso padre termina inmediatamente
        print(f"[PADRE] PID: {os.getpid()}")
        print(f"[PADRE] Creé el hijo {pid}")
        print("[PADRE] Terminando inmediatamente...")
        os._exit(0)  # Padre muere, hijo queda huérfano
    else:
        # Proceso hijo queda huérfano
        print(f"[HIJO] PID: {os.getpid()}")
        print(f"[HIJO] Mi padre original era: {os.getppid()}")
        
        # Esperar un momento para que el padre termine
        time.sleep(2)
        
        print(f"[HIJO] Ahora soy huérfano. Mi nuevo padre es: {os.getppid()}")
        print("[HIJO] Mi nuevo padre debería ser init/systemd (PID 1)")
        
        # Mantener el proceso vivo un tiempo para observarlo
        for i in range(10, 0, -1):
            print(f"[HIJO] Huérfano viviendo {i} segundos más...")
            time.sleep(1)
        
        print("[HIJO] Proceso huérfano terminando")

if __name__ == "__main__":
    main()