#!/usr/bin/env python3

# Ejercicio 2: Diferenciar señales según su origen
#
# Objetivo: Comprender cómo múltiples señales pueden ser diferenciadas en un mismo handler.
#
# Enunciado:
# El proceso principal debe lanzar tres procesos hijos. Cada hijo, luego de un pequeño retardo 
# aleatorio, debe enviar una señal distinta al padre (SIGUSR1, SIGUSR2, SIGTERM). 
# El padre debe manejar todas las señales con un solo handler y registrar cuál hijo envió qué señal, 
# usando os.getpid() y os.getppid().

import signal
import os
import sys
import time
import random

# Variables globales para rastrear señales recibidas
seniales_recibidas = []
hijos_completados = 0
total_hijos = 3

def handler_universal(signum, frame):
    """
    Handler único que maneja múltiples tipos de señales.
    
    En sistemas UNIX, un handler puede manejar diferentes señales.
    Usamos el parámetro signum para determinar qué señal fue recibida.
    
    Señales utilizadas:
    - SIGUSR1 (10): Señal definida por usuario 1
    - SIGUSR2 (12): Señal definida por usuario 2  
    - SIGTERM (15): Señal de terminación
    
    Args:
        signum: Número de la señal recibida
        frame: Frame del stack (no lo usamos aquí)
    """
    global seniales_recibidas, hijos_completados
    
    # Mapeo de números de señal a nombres para mostrar
    nombres_seniales = {
        signal.SIGUSR1: "SIGUSR1",
        signal.SIGUSR2: "SIGUSR2", 
        signal.SIGTERM: "SIGTERM"
    }
    
    nombre_senial = nombres_seniales.get(signum, f"SEÑAL_{signum}")
    timestamp = time.strftime("%H:%M:%S")
    
    print(f"📡 [{timestamp}] PADRE recibió {nombre_senial} (#{signum})")
    
    # Registrar la señal recibida
    seniales_recibidas.append({
        'senial': nombre_senial,
        'numero': signum,
        'timestamp': timestamp
    })
    
    hijos_completados += 1
    
    # Si recibimos SIGTERM, terminar el proceso padre
    if signum == signal.SIGTERM:
        print(f"💀 PADRE: Recibida SIGTERM, terminando...")
        mostrar_resumen()
        sys.exit(0)

def hijo_proceso(hijo_id, senial_a_enviar):
    """
    Función que ejecuta cada proceso hijo.
    
    Cada hijo:
    1. Espera un tiempo aleatorio (simula trabajo)
    2. Envía una señal específica al proceso padre
    3. Termina
    
    Args:
        hijo_id: Identificador del hijo (1, 2, o 3)
        senial_a_enviar: Señal que debe enviar al padre
    """
    # Obtener PIDs
    mi_pid = os.getpid()
    padre_pid = os.getppid()
    
    print(f"👶 HIJO-{hijo_id} (PID:{mi_pid}) iniciado, padre PID:{padre_pid}")
    
    # Retardo aleatorio entre 1 y 3 segundos
    delay = random.uniform(1, 3)
    print(f"👶 HIJO-{hijo_id}: Esperando {delay:.1f}s antes de enviar señal...")
    time.sleep(delay)
    
    # Mapeo para mostrar nombre de señal
    nombres = {
        signal.SIGUSR1: "SIGUSR1",
        signal.SIGUSR2: "SIGUSR2",
        signal.SIGTERM: "SIGTERM"
    }
    
    nombre_senial = nombres.get(senial_a_enviar, f"SEÑAL_{senial_a_enviar}")
    
    print(f"📤 HIJO-{hijo_id}: Enviando {nombre_senial} al padre (PID:{padre_pid})")
    
    # Enviar señal al padre usando os.kill()
    os.kill(padre_pid, senial_a_enviar)
    
    print(f"✅ HIJO-{hijo_id}: Señal enviada, terminando")
    sys.exit(0)

def mostrar_resumen():
    """
    Muestra un resumen de todas las señales recibidas
    """
    print("\n" + "="*50)
    print("📊 RESUMEN DE SEÑALES RECIBIDAS")
    print("="*50)
    
    if not seniales_recibidas:
        print("❌ No se recibieron señales")
        return
    
    for i, info in enumerate(seniales_recibidas, 1):
        print(f"{i}. [{info['timestamp']}] {info['senial']} (#{info['numero']})")
    
    print(f"\nTotal señales recibidas: {len(seniales_recibidas)}")
    print("="*50)

def main():
    """
    Proceso principal que crea hijos y espera señales
    """
    print("=== Ejercicio 2: Diferenciar señales según su origen ===")
    print(f"PADRE PID: {os.getpid()}")
    
    # Registrar el handler universal para las tres señales
    signal.signal(signal.SIGUSR1, handler_universal)
    signal.signal(signal.SIGUSR2, handler_universal)
    signal.signal(signal.SIGTERM, handler_universal)
    
    print("✅ Handler universal registrado para SIGUSR1, SIGUSR2, SIGTERM")
    
    # Definir qué señal enviará cada hijo
    seniales_por_hijo = [
        signal.SIGUSR1,  # Hijo 1
        signal.SIGUSR2,  # Hijo 2  
        signal.SIGTERM   # Hijo 3
    ]
    
    print(f"\n🚀 Creando {total_hijos} procesos hijos...")
    
    # Crear los procesos hijos
    for i in range(total_hijos):
        pid = os.fork()
        
        if pid == 0:
            # Código del proceso hijo
            hijo_proceso(i + 1, seniales_por_hijo[i])
        elif pid > 0:
            print(f"✅ HIJO-{i + 1} creado con PID: {pid}")
        else:
            print(f"❌ Error creando HIJO-{i + 1}")
            sys.exit(1)
    
    print(f"\n⏳ PADRE esperando señales de {total_hijos} hijos...")
    
    try:
        # Esperar hasta recibir todas las señales o SIGTERM
        while hijos_completados < total_hijos:
            # Usar signal.pause() para esperar señales de manera eficiente
            # pause() suspende el proceso hasta que llegue una señal
            signal.pause()
            
        print(f"\n✅ PADRE: Recibidas todas las señales de {total_hijos} hijos")
        
    except KeyboardInterrupt:
        print(f"\n⌨️  PADRE: Interrumpido por Ctrl+C")
    
    # Esperar a que todos los hijos terminen (evitar procesos zombie)
    print("\n🧟 PADRE: Esperando terminación de procesos hijos...")
    for _ in range(total_hijos):
        try:
            pid, status = os.wait()
            print(f"🪦 Hijo PID:{pid} terminó con código {status}")
        except OSError:
            # No hay más hijos
            break
    
    mostrar_resumen()
    print("\n✅ PADRE: Programa completado")

if __name__ == "__main__":
    main()