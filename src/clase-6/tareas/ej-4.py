#!/usr/bin/env python3

# Ejercicio 4 — Múltiples productores
# Objetivo: Estudiar el comportamiento de múltiples escritores sobre un mismo FIFO.
#
# Instrucciones:
# 1. Crear un FIFO `/tmp/fifo_multi`.
# 2. Ejecutar tres scripts distintos que escriban mensajes periódicamente 
#    (por ejemplo, "Soy productor 1", etc.).
# 3. Un solo lector debe mostrar los mensajes.
#
# Reflexión: ¿Qué pasa si todos escriben al mismo tiempo? ¿Hay mezcla de líneas? ¿Es atómico?

import os
import sys
import time
import signal
import random
from datetime import datetime

# Configuración
FIFO_PATH = '/tmp/fifo_multi'

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

def productor(id_productor, num_mensajes=10, delay_base=1.0):
    """
    Proceso productor que envía mensajes identificados al FIFO.
    
    Con múltiples escritores en un FIFO:
    - Las escrituras pequeñas (< PIPE_BUF bytes) son atómicas
    - PIPE_BUF suele ser 4096 bytes en Linux
    - Escrituras más grandes pueden intercalarse
    - El orden de llegada depende del scheduler del kernel
    """
    print(f"=== PRODUCTOR {id_productor} - Ejercicio 4 ===")
    print(f"Enviando {num_mensajes} mensajes al FIFO: {FIFO_PATH}")
    print(f"Delay base: {delay_base}s")
    print("-" * 50)
    
    try:
        # Verificar que el FIFO existe
        if not os.path.exists(FIFO_PATH):
            print(f"❌ Error: FIFO {FIFO_PATH} no existe")
            print("Primero ejecuta el lector")
            return
        
        # Abrir FIFO para escritura
        print(f"Productor {id_productor}: Conectando...")
        fd = os.open(FIFO_PATH, os.O_WRONLY)
        print(f"✅ Productor {id_productor} conectado")
        
        for i in range(1, num_mensajes + 1):
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            
            # Mensaje con identificador único
            mensaje = f"PROD-{id_productor} MSG-{i:02d} [{timestamp}] Soy productor {id_productor}\n"
            
            # Enviar mensaje (escritura atómica si < PIPE_BUF)
            os.write(fd, mensaje.encode())
            
            print(f"📤 P{id_productor}: Enviado mensaje {i}")
            
            # Delay variable para simular diferentes velocidades
            delay = delay_base + random.uniform(-0.3, 0.3)
            time.sleep(max(0.1, delay))
        
        # Mensaje de finalización
        fin_msg = f"PROD-{id_productor} FIN [{datetime.now().strftime('%H:%M:%S')}] Productor {id_productor} terminado\n"
        os.write(fd, fin_msg.encode())
        
        os.close(fd)
        print(f"✅ Productor {id_productor} terminado ({num_mensajes} mensajes enviados)")
        
    except KeyboardInterrupt:
        print(f"\nProductor {id_productor} interrumpido")
    except OSError as e:
        print(f"Error en productor {id_productor}: {e}")

def lector():
    """
    Lector único que recibe mensajes de múltiples productores.
    
    El lector puede observar:
    - Intercalado de mensajes de diferentes productores
    - Orden no determinístico (depende del scheduler)
    - Atomicidad de escrituras pequeñas
    - Posible mezclado si las escrituras son muy grandes
    """
    print("=== LECTOR MÚLTIPLE - Ejercicio 4 ===")
    print(f"Leyendo mensajes del FIFO: {FIFO_PATH}")
    print("Esperando conexión de productores...")
    print("-" * 50)
    
    try:
        # Crear FIFO si no existe
        if not os.path.exists(FIFO_PATH):
            os.mkfifo(FIFO_PATH)
            print(f"FIFO creado: {FIFO_PATH}")
        
        # Abrir FIFO para lectura
        fd = os.open(FIFO_PATH, os.O_RDONLY)
        print("✅ FIFO abierto. Esperando mensajes...")
        
        mensajes_por_productor = {}
        total_mensajes = 0
        productores_activos = set()
        productores_terminados = set()
        
        while True:
            # Leer línea del FIFO
            buffer = b""
            while True:
                try:
                    char = os.read(fd, 1)
                    if not char:
                        # EOF - todos los escritores cerraron
                        break
                    buffer += char
                    if char == b'\n':
                        break
                except OSError:
                    break
            
            if not buffer:
                print("📭 Todos los productores se han desconectado")
                break
            
            linea = buffer.decode('utf-8', errors='replace').strip()
            
            if linea:
                total_mensajes += 1
                timestamp_llegada = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                
                # Analizar mensaje
                if linea.startswith("PROD-"):
                    try:
                        # Parsear: PROD-X MSG-Y [timestamp] mensaje
                        partes = linea.split(' ', 3)
                        prod_info = partes[0]  # PROD-X
                        msg_info = partes[1]   # MSG-Y
                        timestamp_prod = partes[2]  # [timestamp]
                        contenido = partes[3] if len(partes) > 3 else ""
                        
                        prod_id = prod_info.split('-')[1]
                        productores_activos.add(prod_id)
                        
                        # Contar mensajes por productor
                        if prod_id not in mensajes_por_productor:
                            mensajes_por_productor[prod_id] = 0
                        mensajes_por_productor[prod_id] += 1
                        
                        # Verificar si es mensaje de fin
                        if "FIN" in msg_info or "terminado" in contenido:
                            productores_terminados.add(prod_id)
                            print(f"🏁 Productor {prod_id} terminó")
                        else:
                            print(f"📨 [{timestamp_llegada}] {linea}")
                        
                    except (IndexError, ValueError):
                        print(f"📨 [{timestamp_llegada}] {linea}")
                else:
                    print(f"📨 [{timestamp_llegada}] {linea}")
        
        os.close(fd)
        
        # Mostrar estadísticas
        print("\n" + "="*70)
        print("ESTADÍSTICAS DE RECEPCIÓN - MÚLTIPLES PRODUCTORES")
        print("="*70)
        print(f"Total de mensajes recibidos: {total_mensajes}")
        print(f"Productores detectados: {len(productores_activos)}")
        print(f"Productores terminados: {len(productores_terminados)}")
        
        if mensajes_por_productor:
            print("\nMensajes por productor:")
            for prod_id in sorted(mensajes_por_productor.keys()):
                count = mensajes_por_productor[prod_id]
                status = "✅ Terminado" if prod_id in productores_terminados else "⏳ Activo"
                print(f"  Productor {prod_id}: {count} mensajes [{status}]")
        
        print("="*70)
        
        # Análisis de concurrencia
        print("\n🔍 ANÁLISIS DE CONCURRENCIA:")
        print("- Los mensajes pueden llegar en orden no determinístico")
        print("- Cada escritura completa es atómica (si es < PIPE_BUF bytes)")
        print("- El kernel maneja la sincronización entre múltiples escritores")
        print("- No hay garantía de fairness entre productores")
        
    except KeyboardInterrupt:
        print("\nLector interrumpido")
    except OSError as e:
        print(f"Error en lector: {e}")

def demo_automatica():
    """
    Demo que crea 3 productores y 1 lector automáticamente usando fork()
    """
    print("=== DEMO AUTOMÁTICA - Ejercicio 4 ===")
    print("Creando 3 productores y 1 lector automáticamente")
    print("-" * 50)
    
    # Limpiar recursos previos
    limpiar_fifo()
    
    # Crear FIFO
    os.mkfifo(FIFO_PATH)
    print(f"FIFO creado: {FIFO_PATH}")
    
    # Lista para almacenar PIDs de procesos hijos
    pids_productores = []
    
    # Crear 3 procesos productores
    for i in range(1, 4):
        pid = os.fork()
        
        if pid == 0:  # Proceso hijo (productor)
            print(f"Proceso productor {i} iniciado (PID: {os.getpid()})")
            time.sleep(0.5 + i * 0.2)  # Stagger inicial
            
            try:
                # Abrir FIFO para escritura
                fd = os.open(FIFO_PATH, os.O_WRONLY)
                
                # Enviar mensajes con diferentes velocidades
                num_msgs = 5 + i  # Productor 1: 6 msgs, Productor 2: 7 msgs, etc.
                delay_base = 0.5 + i * 0.2
                
                for j in range(1, num_msgs + 1):
                    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    mensaje = f"PROD-{i} MSG-{j:02d} [{timestamp}] Mensaje desde productor {i}\n"
                    
                    os.write(fd, mensaje.encode())
                    print(f"📤 P{i}: Enviado {j}/{num_msgs - 1}")
                    
                    # Delay variable
                    delay = delay_base + random.uniform(-0.1, 0.1)
                    time.sleep(max(0.1, delay))
                
                # Mensaje de finalización
                fin_msg = f"PROD-{i} FIN [{datetime.now().strftime('%H:%M:%S')}] Productor {i} terminado\n"
                os.write(fd, fin_msg.encode())
                
                os.close(fd)
                print(f"✅ Productor {i} terminado")
                
            except OSError as e:
                print(f"Error en productor {i}: {e}")
            
            sys.exit(0)
        
        else:  # Proceso padre
            pids_productores.append(pid)
    
    # El proceso padre actúa como lector
    print("Proceso padre: LECTOR")
    time.sleep(1)  # Dar tiempo a los productores para configurarse
    
    try:
        # Abrir FIFO para lectura
        fd = os.open(FIFO_PATH, os.O_RDONLY)
        print("✅ Lector conectado")
        
        mensajes_recibidos = 0
        productores_terminados = 0
        
        while productores_terminados < 3:  # Esperar a que terminen los 3 productores
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
            
            linea = buffer.decode('utf-8', errors='replace').strip()
            if linea:
                mensajes_recibidos += 1
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                
                if "FIN" in linea:
                    productores_terminados += 1
                    print(f"🏁 [{timestamp}] {linea}")
                else:
                    print(f"📨 [{timestamp}] {linea}")
        
        os.close(fd)
        print(f"\n✅ Demo completada. {mensajes_recibidos} mensajes recibidos")
        
    except OSError as e:
        print(f"Error en lector: {e}")
    
    # Esperar a todos los procesos productores
    for pid in pids_productores:
        try:
            os.waitpid(pid, 0)
        except OSError:
            pass  # Proceso ya terminó
    
    limpiar_fifo()

def main():
    # Configurar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Ejercicio 4: Múltiples productores")
    print("Estudia el comportamiento de múltiples escritores en un FIFO")
    print("Elige el modo de ejecución:")
    print("1. Lector (espera mensajes de múltiples productores)")
    print("2. Productor (envía mensajes identificados)")
    print("3. Demo automática (3 productores + 1 lector)")
    
    try:
        opcion = input("\nSelecciona una opción (1-3): ").strip()
        
        if opcion == '1':
            lector()
        elif opcion == '2':
            prod_id = input("ID del productor (1-9): ").strip()
            if not prod_id.isdigit():
                prod_id = "1"
            
            num_msgs = input("Número de mensajes (default 10): ").strip()
            num_msgs = int(num_msgs) if num_msgs.isdigit() else 10
            
            delay = input("Delay base en segundos (default 1.0): ").strip()
            delay = float(delay) if delay else 1.0
            
            productor(prod_id, num_msgs, delay)
        elif opcion == '3':
            demo_automatica()
        else:
            print("Opción inválida")
            
    except (EOFError, KeyboardInterrupt):
        print("\nPrograma interrumpido")
        limpiar_fifo()

if __name__ == "__main__":
    main()