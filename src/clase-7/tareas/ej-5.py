#!/usr/bin/env python3

# Ejercicio 5: Simulación de cola de trabajos con señales
#
# Objetivo: Simular un sistema productor-consumidor asíncrono usando señales.
#
# Enunciado:
# Desarrolla dos procesos: uno productor y uno consumidor. El productor genera trabajos 
# (simulados por mensajes con timestamp) y, al generarlos, envía SIGUSR1 al consumidor. 
# El consumidor debe recibir la señal, registrar el timestamp de recepción y "procesar" 
# el trabajo (simulado con un sleep()). Implementa una protección contra pérdida de señales: 
# si se reciben varias en rápida sucesión, deben encolarse en una estructura temporal para 
# ser procesadas una por una.

import signal
import os
import sys
import time
import json
from datetime import datetime
from collections import deque

# Cola global para trabajos pendientes
cola_trabajos = deque()
trabajos_procesados = 0
trabajos_generados = 0

# Archivo temporal para comunicación entre procesos
ARCHIVO_TRABAJOS = "/tmp/trabajos_cola.txt"

def signal_handler_consumidor(signum, frame):
    """
    Handler del consumidor que se ejecuta cuando recibe SIGUSR1.
    
    Problema de las señales: Si llegan múltiples señales del mismo tipo
    muy rápido, algunas pueden "perderse" (signal coalescing).
    
    Solución: Leer todos los trabajos disponibles cuando llega la señal,
    no solo uno.
    """
    global cola_trabajos
    
    print(f"\n🔔 [CONSUMIDOR] Señal SIGUSR1 recibida")
    
    # Leer todos los trabajos disponibles del archivo
    try:
        with open(ARCHIVO_TRABAJOS, 'r') as f:
            lineas = f.readlines()
        
        # Limpiar archivo después de leer
        with open(ARCHIVO_TRABAJOS, 'w') as f:
            f.write("")
        
        # Agregar trabajos a la cola
        for linea in lineas:
            if linea.strip():
                try:
                    trabajo = json.loads(linea.strip())
                    cola_trabajos.append(trabajo)
                    print(f"📥 [CONSUMIDOR] Trabajo encolado: {trabajo['id']}")
                except json.JSONDecodeError:
                    print(f"❌ Error parseando trabajo: {linea}")
                    
    except FileNotFoundError:
        print("⚠️  [CONSUMIDOR] Archivo de trabajos no encontrado")

def procesar_trabajo(trabajo):
    """
    Simula el procesamiento de un trabajo.
    
    Args:
        trabajo: Dict con información del trabajo
    """
    global trabajos_procesados
    
    tiempo_recepcion = datetime.now().isoformat()
    
    print(f"⚙️  [PROCESANDO] Trabajo {trabajo['id']}")
    print(f"   Creado: {trabajo['timestamp']}")  
    print(f"   Recibido: {tiempo_recepcion}")
    
    # Simular tiempo de procesamiento variable
    tiempo_proceso = trabajo.get('duracion', 2)
    print(f"   Duración: {tiempo_proceso}s")
    
    time.sleep(tiempo_proceso)
    
    trabajos_procesados += 1
    print(f"✅ [COMPLETADO] Trabajo {trabajo['id']} terminado")
    print(f"   Total procesados: {trabajos_procesados}")

def consumidor():
    """
    Proceso consumidor que espera señales y procesa trabajos.
    """
    global cola_trabajos
    
    print("=== CONSUMIDOR - Ejercicio 5 ===")
    print(f"PID Consumidor: {os.getpid()}")
    
    # Limpiar archivo de trabajos
    with open(ARCHIVO_TRABAJOS, 'w') as f:
        f.write("")
    
    # Instalar handler para SIGUSR1
    signal.signal(signal.SIGUSR1, signal_handler_consumidor)
    print("✅ Handler instalado para SIGUSR1")
    
    print("⏳ Esperando trabajos del productor...")
    print("📋 Presiona Ctrl+C para terminar")
    
    try:
        while True:
            # Procesar todos los trabajos en cola
            while cola_trabajos:
                trabajo = cola_trabajos.popleft()
                procesar_trabajo(trabajo)
            
            # Esperar por señales
            time.sleep(0.5)  # Pequeña pausa para no consumir CPU
            
    except KeyboardInterrupt:
        print(f"\n🛑 [CONSUMIDOR] Terminado por usuario")
        print(f"📊 Total trabajos procesados: {trabajos_procesados}")

def productor(num_trabajos=10, intervalo=1.5):
    """
    Proceso productor que genera trabajos y envía señales.
    
    Args:
        num_trabajos: Cantidad de trabajos a generar
        intervalo: Tiempo entre trabajos en segundos
    """
    global trabajos_generados
    
    print("=== PRODUCTOR - Ejercicio 5 ===")
    print(f"PID Productor: {os.getpid()}")
    
    # Obtener PID del consumidor (debe estar en el archivo)
    pid_consumidor = None
    try:
        with open("/tmp/consumidor_pid.txt", 'r') as f:
            pid_consumidor = int(f.read().strip())
    except:
        print("❌ No se encontró PID del consumidor")
        print("Ejecuta primero el consumidor")
        return
    
    print(f"🎯 Enviando trabajos al consumidor PID: {pid_consumidor}")
    print(f"📊 Generando {num_trabajos} trabajos con intervalo {intervalo}s")
    
    for i in range(1, num_trabajos + 1):
        trabajos_generados += 1
        
        # Crear trabajo
        trabajo = {
            'id': f"JOB-{i:03d}",
            'timestamp': datetime.now().isoformat(),
            'datos': f"Datos del trabajo número {i}",
            'duracion': round(1 + (i % 3), 1)  # Duración variable 1-3 segundos
        }
        
        print(f"🏭 [GENERANDO] Trabajo {trabajo['id']}")
        
        # Escribir trabajo al archivo (append)
        with open(ARCHIVO_TRABAJOS, 'a') as f:
            f.write(json.dumps(trabajo) + '\n')
        
        # Enviar señal al consumidor
        try:
            os.kill(pid_consumidor, signal.SIGUSR1)
            print(f"📤 [SEÑAL] SIGUSR1 enviada a consumidor para {trabajo['id']}")
        except OSError as e:
            print(f"❌ Error enviando señal: {e}")
            break
        
        time.sleep(intervalo)
    
    print(f"✅ [PRODUCTOR] Completado - {trabajos_generados} trabajos generados")

def demo_automatica():
    """
    Demo que ejecuta productor y consumidor usando fork()
    """
    print("=== DEMO AUTOMÁTICA - Ejercicio 5 ===")
    print("Simulando productor-consumidor con señales")
    
    # Limpiar archivos previos
    try:
        os.remove(ARCHIVO_TRABAJOS)
    except:
        pass
    
    pid = os.fork()
    
    if pid > 0:  # Proceso padre (consumidor)
        # Guardar PID para que el productor nos encuentre
        with open("/tmp/consumidor_pid.txt", 'w') as f:
            f.write(str(os.getpid()))
        
        print("Proceso padre: CONSUMIDOR")
        time.sleep(0.5)  # Dar tiempo al hijo para configurarse
        
        # Instalar handler
        signal.signal(signal.SIGUSR1, signal_handler_consumidor)
        print("✅ Consumidor listo, esperando trabajos...")
        
        # Procesar trabajos por 15 segundos
        tiempo_inicio = time.time()
        trabajos_recibidos = 0
        
        try:
            while time.time() - tiempo_inicio < 15:
                # Procesar cola
                while cola_trabajos:
                    trabajo = cola_trabajos.popleft()
                    trabajos_recibidos += 1
                    print(f"⚙️  Procesando {trabajo['id']}...")
                    time.sleep(1)  # Procesamiento rápido para demo
                    print(f"✅ {trabajo['id']} completado")
                
                time.sleep(0.2)
                
        except KeyboardInterrupt:
            pass
        
        # Esperar al hijo
        os.waitpid(pid, 0)
        
        print(f"\n📊 Demo completada - {trabajos_recibidos} trabajos procesados")
        
        # Limpiar archivos
        try:
            os.remove("/tmp/consumidor_pid.txt")
            os.remove(ARCHIVO_TRABAJOS)
        except:
            pass
            
    elif pid == 0:  # Proceso hijo (productor)
        print("Proceso hijo: PRODUCTOR")
        time.sleep(1)  # Dar tiempo al padre para configurarse
        
        # Leer PID del consumidor
        with open("/tmp/consumidor_pid.txt", 'r') as f:
            pid_consumidor = int(f.read().strip())
        
        # Generar trabajos rápidamente para demo
        for i in range(1, 8):
            trabajo = {
                'id': f"DEMO-{i:02d}",
                'timestamp': datetime.now().isoformat(),
                'datos': f"Trabajo demo {i}"
            }
            
            # Escribir trabajo
            with open(ARCHIVO_TRABAJOS, 'a') as f:
                f.write(json.dumps(trabajo) + '\n')
            
            # Enviar señal
            os.kill(pid_consumidor, signal.SIGUSR1)
            print(f"📤 Productor envió: {trabajo['id']}")
            
            time.sleep(1.5)  # Intervalo entre trabajos
        
        print("✅ Productor terminado")
        sys.exit(0)

def main():
    """
    Función principal que permite elegir modo de ejecución
    """
    print("Ejercicio 5: Simulación de cola de trabajos con señales")
    print("Elige el modo:")
    print("1. Consumidor (espera trabajos)")
    print("2. Productor (genera trabajos)")  
    print("3. Demo automática (fork ambos procesos)")
    
    try:
        opcion = input("\nSelecciona (1-3): ").strip()
        
        if opcion == '1':
            # Guardar nuestro PID para el productor
            with open("/tmp/consumidor_pid.txt", 'w') as f:
                f.write(str(os.getpid()))
            print("💾 PID guardado para el productor")
            consumidor()
        elif opcion == '2':
            num = input("Número de trabajos (default 10): ").strip()
            num = int(num) if num.isdigit() else 10
            
            intervalo = input("Intervalo en segundos (default 1.5): ").strip() 
            intervalo = float(intervalo) if intervalo else 1.5
            
            productor(num, intervalo)
        elif opcion == '3':
            demo_automatica()
        else:
            print("Opción inválida")
            
    except (EOFError, KeyboardInterrupt):
        print("\nPrograma interrumpido")

if __name__ == "__main__":
    main()