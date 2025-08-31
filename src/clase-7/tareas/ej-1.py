#!/usr/bin/env python3

# Ejercicio 1: Manejo básico con SIGTERM
#
# Objetivo: Familiarizarse con el uso de SIGTERM y funciones de limpieza al finalizar un proceso.
#
# Enunciado:
# Crea un programa que capture la señal SIGTERM y, en respuesta, muestre un mensaje de despedida. 
# Asegúrate de registrar una función con atexit para que se ejecute al terminar el proceso, 
# independientemente del motivo de finalización.

import signal
import time
import atexit
import os
import sys

# Variable global para controlar si recibimos SIGTERM
recibido_sigterm = False

def cleanup_function():
    """
    Función de limpieza que se ejecuta automáticamente al terminar el proceso.
    atexit garantiza que se ejecute sin importar cómo termine el programa:
    - Terminación normal
    - Excepción no capturada  
    - Señales que terminan el proceso
    """
    print("🧹 [CLEANUP] Función de limpieza ejecutándose...")
    print("🧹 [CLEANUP] Liberando recursos, cerrando archivos, etc.")
    print("🧹 [CLEANUP] Limpieza completada")

def sigterm_handler(signum, frame):
    """
    Handler para la señal SIGTERM.
    
    SIGTERM (15) es la señal estándar para solicitar terminación elegante:
    - Enviada por 'kill <pid>' por defecto
    - Permite al proceso hacer cleanup antes de salir
    - Diferente a SIGKILL (9) que termina inmediatamente sin cleanup
    
    Args:
        signum: Número de la señal (15 para SIGTERM)
        frame: Frame del stack donde se interrumpió la ejecución
    """
    global recibido_sigterm
    
    print(f"\n💀 [SIGTERM] Recibida señal {signum} (SIGTERM)")
    print("💀 [SIGTERM] Iniciando terminación elegante...")
    print("💀 [SIGTERM] Mensaje de despedida: ¡Adiós mundo!")
    
    recibido_sigterm = True
    
    # Salir después del mensaje (atexit se ejecutará automáticamente)
    print("💀 [SIGTERM] Terminando proceso...")
    sys.exit(0)

def main():
    """
    Función principal que demuestra el manejo básico de SIGTERM
    """
    print("=== Ejercicio 1: Manejo básico con SIGTERM ===")
    print(f"PID del proceso: {os.getpid()}")
    print("Registrando handlers...")
    
    # Registrar función de cleanup que se ejecuta al terminar
    atexit.register(cleanup_function)
    print("✅ Función cleanup registrada con atexit")
    
    # Registrar handler para SIGTERM
    signal.signal(signal.SIGTERM, sigterm_handler)
    print("✅ Handler para SIGTERM registrado")
    
    print("\n📋 Instrucciones:")
    print(f"1. En otra terminal, ejecuta: kill {os.getpid()}")
    print(f"2. O ejecuta: kill -TERM {os.getpid()}")
    print("3. Observa cómo se ejecuta el handler y luego la función cleanup")
    print("4. También puedes terminar con Ctrl+C para ver solo la función cleanup")
    
    print("\n⏳ Esperando señales... (bucle infinito)")
    print("   Ctrl+C para terminar normalmente")
    print("   kill <pid> para enviar SIGTERM")
    
    try:
        # Bucle principal - simular trabajo
        contador = 0
        while True:
            contador += 1
            print(f"⚡ Trabajando... iteración {contador}")
            time.sleep(2)
            
            # Salir si recibimos SIGTERM (aunque el handler ya termina el proceso)
            if recibido_sigterm:
                break
                
    except KeyboardInterrupt:
        print("\n⌨️  [CTRL+C] Terminación por teclado")
        print("⌨️  [CTRL+C] La función cleanup se ejecutará automáticamente")
        # No necesitamos llamar sys.exit() aquí, Python terminará normalmente
        # y atexit ejecutará cleanup_function()

if __name__ == "__main__":
    main()