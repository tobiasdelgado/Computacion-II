#!/usr/bin/env python3

# Ejercicio 3: Ignorar señales temporalmente
#
# Objetivo: Controlar cuándo un programa debe responder a una señal.
#
# Enunciado:
# Crea un programa que ignore SIGINT (Ctrl+C) durante los primeros 5 segundos de ejecución. 
# Luego, el programa debe restaurar el comportamiento por defecto para esa señal y continuar 
# ejecutando indefinidamente. Verifica que Ctrl+C no interrumpe el programa durante los 
# primeros segundos, pero sí lo hace después.

import signal
import time
import os

def handler_personalizado(signum, frame):
    """
    Handler personalizado que se ejecuta cuando SIGINT es restaurado.
    
    Este handler se ejecutará después de los primeros 5 segundos
    cuando restauremos el manejo de SIGINT.
    """
    print(f"\n🛑 [HANDLER] Recibida señal SIGINT ({signum})")
    print("🛑 [HANDLER] Terminando programa de forma controlada...")
    print("🛑 [HANDLER] ¡Adiós!")
    exit(0)

def main():
    """
    Programa principal que demuestra el bloqueo temporal de señales
    """
    print("=== Ejercicio 3: Ignorar señales temporalmente ===")
    print(f"PID del proceso: {os.getpid()}")
    
    # FASE 1: Ignorar SIGINT durante 5 segundos
    print("\n📛 FASE 1: Ignorando SIGINT (Ctrl+C) por 5 segundos...")
    print("📛 Prueba presionar Ctrl+C ahora - debería ser ignorado")
    
    # signal.SIG_IGN le dice al sistema que ignore completamente la señal
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    print("✅ SIGINT configurado para ser ignorado")
    
    # Contador regresivo de 5 segundos
    for i in range(5, 0, -1):
        print(f"⏰ {i} segundos restantes (Ctrl+C ignorado)")
        time.sleep(1)
    
    print("✅ FASE 1 completada - SIGINT fue ignorado durante 5 segundos")
    
    # FASE 2: Restaurar comportamiento de SIGINT
    print("\n🔄 FASE 2: Restaurando manejo de SIGINT...")
    
    # Opción A: Restaurar comportamiento por defecto
    # signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    # Opción B: Usar un handler personalizado (más educativo)
    signal.signal(signal.SIGINT, handler_personalizado)
    print("✅ SIGINT restaurado con handler personalizado")
    
    print("\n🎯 FASE 2 activa: Ahora Ctrl+C terminará el programa")
    print("🎯 Presiona Ctrl+C para probar que ahora funciona")
    
    # Bucle infinito para demostrar que Ctrl+C ahora funciona
    contador = 0
    try:
        while True:
            contador += 1
            print(f"🔄 Ejecutando... iteración {contador} (Ctrl+C funcionará ahora)")
            time.sleep(2)
            
    except KeyboardInterrupt:
        # Este except no se ejecutará porque tenemos un handler personalizado
        # El handler personalizado se ejecutará en su lugar
        print("❌ Este mensaje no debería aparecer")

if __name__ == "__main__":
    main()