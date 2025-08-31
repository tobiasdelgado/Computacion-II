#!/usr/bin/env python3

# Ejercicio 2 — FIFO como buffer entre procesos
# Objetivo: Simular un flujo de datos continuo entre dos procesos.
#
# Instrucciones:
# 1. Crear un proceso productor que escriba números del 1 al 100 en el FIFO con un sleep(0.1).
# 2. Crear un consumidor que lea esos números del FIFO y los imprima con su timestamp local.
# 3. Asegurarse de que ambos scripts se ejecuten en paralelo.
#
# Extensión: Agregar lógica en el consumidor para detectar si falta un número 
# (por ejemplo, si no es consecutivo).

import os
import sys
import time
import signal
from datetime import datetime

# Nombre del FIFO
FIFO_PATH = '/tmp/buffer_fifo'

def limpiar_fifo():
    """Función para limpiar el FIFO al salir"""
    try:
        if os.path.exists(FIFO_PATH):
            os.remove(FIFO_PATH)
            print(f"FIFO {FIFO_PATH} eliminado")
    except OSError as e:
        print(f"Error al eliminar FIFO: {e}")

def signal_handler(signum, frame):
    """Manejador para señales (Ctrl+C)"""
    print("\nInterrumpido por el usuario")
    limpiar_fifo()
    sys.exit(0)

def productor(max_num=100, delay=0.1):
    """
    Proceso productor que envía números secuenciales al FIFO.
    
    Los FIFOs actúan como buffers entre procesos:
    - Los datos se almacenan temporalmente en memoria del kernel
    - Implementan política FIFO (First-In, First-Out)
    - Permiten desacoplar la velocidad de producción y consumo
    """
    print("=== PRODUCTOR - Ejercicio 2 ===")
    print(f"Enviando números del 1 al {max_num} al FIFO: {FIFO_PATH}")
    print(f"Delay entre números: {delay}s")
    print("-" * 50)
    
    try:
        # Crear el FIFO si no existe
        if not os.path.exists(FIFO_PATH):
            os.mkfifo(FIFO_PATH)
            print(f"FIFO creado: {FIFO_PATH}")
        
        # Abrir FIFO para escritura (se bloquea hasta que haya un lector)
        print("Esperando consumidor...")
        fd = os.open(FIFO_PATH, os.O_WRONLY)
        print("✅ Consumidor conectado. Iniciando producción...")
        
        # Enviar números del 1 al max_num
        for numero in range(1, max_num + 1):
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            
            # Formato: numero,timestamp
            mensaje = f"{numero},{timestamp}\n"
            os.write(fd, mensaje.encode())
            
            print(f"📤 Enviado: {numero} [{timestamp}]")
            
            # Pausa entre envíos para simular procesamiento
            time.sleep(delay)
        
        # Enviar señal de fin
        os.write(fd, b"FIN\n")
        print("📋 Señal FIN enviada")
        
        os.close(fd)
        print(f"Productor terminado. {max_num} números enviados")
        
    except KeyboardInterrupt:
        print("\nProductor interrumpido")
    except OSError as e:
        print(f"Error en productor: {e}")

def consumidor():
    """
    Proceso consumidor que lee números del FIFO y detecta números faltantes.
    
    Características del FIFO como buffer:
    - Los datos se consumen (desaparecen una vez leídos)
    - Orden garantizado (FIFO)
    - Bloqueo automático cuando no hay datos
    """
    print("=== CONSUMIDOR - Ejercicio 2 ===")
    print(f"Leyendo números del FIFO: {FIFO_PATH}")
    print("Detectando números faltantes o fuera de secuencia")
    print("-" * 50)
    
    try:
        # Verificar que el FIFO existe
        if not os.path.exists(FIFO_PATH):
            print(f"Error: FIFO {FIFO_PATH} no existe")
            print("Primero ejecuta el productor")
            return
        
        # Abrir FIFO para lectura
        print("Conectando al productor...")
        fd = os.open(FIFO_PATH, os.O_RDONLY)
        print("✅ Conectado. Esperando datos...")
        
        esperado = 1  # Número que esperamos recibir
        total_recibidos = 0
        numeros_faltantes = []
        
        while True:
            # Leer línea del FIFO
            buffer = b""
            while True:
                char = os.read(fd, 1)
                if not char:
                    # EOF - el escritor cerró
                    break
                buffer += char
                if char == b'\n':
                    break
            
            if not buffer:
                print("📭 Productor ha cerrado la conexión")
                break
            
            linea = buffer.decode().strip()
            
            if linea == "FIN":
                print("🏁 Señal FIN recibida")
                break
            
            try:
                # Parsear: numero,timestamp
                if ',' in linea:
                    numero_str, timestamp_prod = linea.split(',', 1)
                    numero = int(numero_str)
                    timestamp_cons = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    
                    total_recibidos += 1
                    
                    # Verificar secuencia
                    if numero == esperado:
                        print(f"📨 #{numero} OK [Prod:{timestamp_prod}] [Cons:{timestamp_cons}]")
                        esperado += 1
                    elif numero > esperado:
                        # Números faltantes
                        faltantes = list(range(esperado, numero))
                        numeros_faltantes.extend(faltantes)
                        print(f"⚠️  #{numero} FUERA DE SECUENCIA [Prod:{timestamp_prod}] [Cons:{timestamp_cons}]")
                        print(f"   Números faltantes: {faltantes}")
                        esperado = numero + 1
                    else:
                        # Número duplicado o atrasado
                        print(f"🔄 #{numero} DUPLICADO/ATRASADO [Prod:{timestamp_prod}] [Cons:{timestamp_cons}]")
                else:
                    print(f"❌ Formato inválido: {linea}")
                    
            except ValueError as e:
                print(f"❌ Error parseando '{linea}': {e}")
        
        os.close(fd)
        
        # Mostrar estadísticas finales
        print("\n" + "="*60)
        print("ESTADÍSTICAS DEL CONSUMIDOR")
        print("="*60)
        print(f"Total números recibidos: {total_recibidos}")
        print(f"Último número esperado: {esperado - 1}")
        print(f"Números faltantes: {len(numeros_faltantes)}")
        if numeros_faltantes:
            print(f"Lista de faltantes: {numeros_faltantes[:10]}{'...' if len(numeros_faltantes) > 10 else ''}")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\nConsumidor interrumpido")
    except OSError as e:
        print(f"Error en consumidor: {e}")

def demo_automatica():
    """
    Demo que ejecuta productor y consumidor usando fork()
    """
    print("=== DEMO AUTOMÁTICA - Ejercicio 2 ===")
    print("Creando productor y consumidor automáticamente")
    print("-" * 50)
    
    # Limpiar FIFO previo
    if os.path.exists(FIFO_PATH):
        os.remove(FIFO_PATH)
    
    # Crear FIFO
    os.mkfifo(FIFO_PATH)
    print(f"FIFO creado: {FIFO_PATH}")
    
    pid = os.fork()
    
    if pid > 0:  # Proceso padre (consumidor)
        print("Proceso padre: CONSUMIDOR")
        time.sleep(0.5)  # Dar tiempo al hijo para configurarse
        
        try:
            # Actuar como consumidor
            fd = os.open(FIFO_PATH, os.O_RDONLY)
            
            esperado = 1
            total_recibidos = 0
            
            while True:
                # Leer línea
                buffer = b""
                while True:
                    char = os.read(fd, 1)
                    if not char:
                        break
                    buffer += char
                    if char == b'\n':
                        break
                
                if not buffer:
                    break
                
                linea = buffer.decode().strip()
                if linea == "FIN":
                    break
                
                if ',' in linea:
                    numero_str, _ = linea.split(',', 1)
                    numero = int(numero_str)
                    total_recibidos += 1
                    
                    if numero == esperado:
                        print(f"📨 Consumidor recibió: {numero}")
                        esperado += 1
                    else:
                        print(f"⚠️  Fuera de secuencia: {numero} (esperaba {esperado})")
                        esperado = numero + 1
            
            os.close(fd)
            print(f"Consumidor terminado. Total: {total_recibidos}")
            
        except OSError as e:
            print(f"Error en consumidor: {e}")
        
        # Esperar al proceso hijo
        os.waitpid(pid, 0)
        limpiar_fifo()
        
    elif pid == 0:  # Proceso hijo (productor)
        print("Proceso hijo: PRODUCTOR")
        time.sleep(0.2)
        
        try:
            # Actuar como productor
            fd = os.open(FIFO_PATH, os.O_WRONLY)
            
            # Enviar 20 números para demo rápida
            for numero in range(1, 21):
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                mensaje = f"{numero},{timestamp}\n"
                os.write(fd, mensaje.encode())
                print(f"📤 Productor envió: {numero}")
                time.sleep(0.1)
            
            # Enviar FIN
            os.write(fd, b"FIN\n")
            os.close(fd)
            print("Productor terminado")
            
        except OSError as e:
            print(f"Error en productor: {e}")
        
        sys.exit(0)
    
    else:
        print("Error en fork()")
        sys.exit(1)

def main():
    # Configurar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Ejercicio 2: FIFO como buffer entre procesos")
    print("Elige el modo de ejecución:")
    print("1. Productor (envía números 1-100)")
    print("2. Consumidor (recibe y verifica secuencia)")
    print("3. Demo automática (fork para crear ambos)")
    
    try:
        opcion = input("\nSelecciona una opción (1-3): ").strip()
        
        if opcion == '1':
            num_max = input("Cantidad de números a enviar (default 100): ").strip()
            num_max = int(num_max) if num_max.isdigit() else 100
            delay = input("Delay entre números en segundos (default 0.1): ").strip()
            delay = float(delay) if delay else 0.1
            productor(num_max, delay)
        elif opcion == '2':
            consumidor()
        elif opcion == '3':
            demo_automatica()
        else:
            print("Opción inválida")
            
    except (EOFError, KeyboardInterrupt):
        print("\nPrograma interrumpido")
        limpiar_fifo()

if __name__ == "__main__":
    main()