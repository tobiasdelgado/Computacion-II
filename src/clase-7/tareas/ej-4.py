#!/usr/bin/env python3

# Ejercicio 4: Control multihilo con señales externas
#
# Objetivo: Integrar señales con hilos y control de ejecución.
#
# Enunciado:
# Crea un programa multihilo donde un hilo cuenta regresivamente desde 30. Usa una variable 
# global con threading.Lock() para permitir que otro proceso externo, al enviar una señal 
# (SIGUSR1), pause la cuenta y otra señal (SIGUSR2) la reinicie. El hilo principal debe 
# instalar los handlers y proteger correctamente el estado compartido.

import signal
import threading
import time
import os
import sys

# Variables globales compartidas entre hilos
contador = 30
pausado = False
terminado = False

# Lock para proteger el acceso concurrente a las variables globales
lock = threading.Lock()

def handler_pausar(signum, frame):
    """
    Handler para SIGUSR1 - pausa el contador.
    
    Las señales en Python solo pueden ser recibidas por el hilo principal.
    Por eso instalamos los handlers en main() y usamos variables globales
    con locks para comunicarnos con el hilo contador.
    """
    global pausado
    
    with lock:  # Proteger acceso concurrente
        if not pausado:
            pausado = True
            print(f"\n⏸️  [SEÑAL] SIGUSR1 recibida - PAUSANDO contador")
            print(f"⏸️  [SEÑAL] Contador pausado en: {contador}")
        else:
            print(f"\n⏸️  [SEÑAL] SIGUSR1 recibida - contador ya estaba pausado")

def handler_reanudar(signum, frame):
    """
    Handler para SIGUSR2 - reanuda el contador.
    """
    global pausado
    
    with lock:  # Proteger acceso concurrente
        if pausado:
            pausado = False
            print(f"\n▶️  [SEÑAL] SIGUSR2 recibida - REANUDANDO contador")
            print(f"▶️  [SEÑAL] Continuando desde: {contador}")
        else:
            print(f"\n▶️  [SEÑAL] SIGUSR2 recibida - contador ya estaba activo")

def handler_terminar(signum, frame):
    """
    Handler para SIGTERM - termina el programa.
    """
    global terminado
    
    with lock:
        terminado = True
        print(f"\n🛑 [SEÑAL] SIGTERM recibida - TERMINANDO programa")

def hilo_contador():
    """
    Hilo que ejecuta la cuenta regresiva desde 30.
    
    Este hilo:
    1. Cuenta regresivamente de 30 a 0
    2. Respeta el estado de pausa controlado por señales
    3. Termina cuando llega a 0 o recibe señal de terminación
    """
    global contador, pausado, terminado
    
    print("🧵 [HILO] Hilo contador iniciado")
    
    while contador > 0:
        # Verificar si debemos terminar
        with lock:
            if terminado:
                print("🧵 [HILO] Terminación solicitada, saliendo...")
                break
        
        # Verificar si estamos pausados
        with lock:
            esta_pausado = pausado
        
        if not esta_pausado:
            # Decrementar contador de forma thread-safe
            with lock:
                contador -= 1
                valor_actual = contador
            
            print(f"🔢 [CONTADOR] {valor_actual}")
            
            # Verificar si llegamos a cero
            if valor_actual == 0:
                print("🎉 [CONTADOR] ¡Cuenta regresiva completada!")
                break
        else:
            # Si está pausado, solo mostrar estado cada segundo
            with lock:
                valor_actual = contador
            print(f"⏸️  [CONTADOR] PAUSADO en {valor_actual}")
        
        time.sleep(1)  # Esperar 1 segundo entre iteraciones
    
    print("🧵 [HILO] Hilo contador terminado")

def main():
    """
    Hilo principal que instala handlers y lanza el hilo contador.
    """
    global terminado
    
    print("=== Ejercicio 4: Control multihilo con señales externas ===")
    print(f"PID del proceso: {os.getpid()}")
    
    # Instalar handlers de señales (solo el hilo principal puede hacer esto)
    signal.signal(signal.SIGUSR1, handler_pausar)
    signal.signal(signal.SIGUSR2, handler_reanudar)
    signal.signal(signal.SIGTERM, handler_terminar)
    
    print("✅ Handlers instalados:")
    print("   SIGUSR1 (10) -> Pausar contador")
    print("   SIGUSR2 (12) -> Reanudar contador") 
    print("   SIGTERM (15) -> Terminar programa")
    
    print(f"\n📋 Instrucciones para probar desde otra terminal:")
    print(f"   Pausar:   kill -USR1 {os.getpid()}")
    print(f"   Reanudar: kill -USR2 {os.getpid()}")
    print(f"   Terminar: kill -TERM {os.getpid()}")
    print(f"   También:  kill {os.getpid()}")
    
    # Crear e iniciar el hilo contador
    hilo = threading.Thread(target=hilo_contador, daemon=True)
    hilo.start()
    print(f"\n🚀 Hilo contador iniciado - cuenta regresiva desde {contador}")
    
    try:
        # El hilo principal espera a que termine el hilo contador
        while hilo.is_alive():
            time.sleep(0.1)  # Pequeña pausa para no consumir CPU
            
            # Verificar si se solicitó terminación
            with lock:
                if terminado:
                    break
        
        # Esperar a que el hilo termine completamente
        hilo.join(timeout=2)
        
        print("\n✅ Programa completado")
        
    except KeyboardInterrupt:
        print(f"\n⌨️  Programa interrumpido con Ctrl+C")
        with lock:
            terminado = True
        hilo.join(timeout=2)

if __name__ == "__main__":
    main()