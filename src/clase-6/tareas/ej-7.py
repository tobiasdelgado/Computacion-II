#!/usr/bin/env python3

# Ejercicio 7 — Monitor de temperatura simulado
# Objetivo: Simular un sensor que envía datos por FIFO y un visualizador que los muestra.
#
# Instrucciones:
# 1. Script A (simulador): cada segundo escribe en el FIFO una temperatura aleatoria entre 20 y 30.
# 2. Script B (monitor): lee las temperaturas y muestra alertas si superan los 28 grados.
#
# Variante: Agregar un log con fecha y hora.

import os
import sys
import time
import signal
import random
import json
from datetime import datetime

# Configuración
FIFO_PATH = '/tmp/temp_monitor'
LOG_FILE = 'temperature_log.txt'
TEMP_MIN = 20.0
TEMP_MAX = 30.0
TEMP_ALERTA = 28.0
TEMP_CRITICA = 29.5

def limpiar_recursos():
    """Función para limpiar recursos al salir"""
    try:
        if os.path.exists(FIFO_PATH):
            os.remove(FIFO_PATH)
            print(f"FIFO {FIFO_PATH} eliminado")
    except OSError as e:
        print(f"Error al eliminar FIFO: {e}")

def signal_handler(signum, frame):
    """Manejador para señales (Ctrl+C)"""
    print("\nMonitor de temperatura interrumpido")
    limpiar_recursos()
    sys.exit(0)

def simulador_sensor(duracion_minutos=5, intervalo_segundos=1):
    """
    Simulador de sensor de temperatura.
    
    Simula un sensor IoT que:
    - Genera temperaturas aleatorias realistas
    - Envía datos cada segundo a través de FIFO
    - Ocasionalmente genera picos de temperatura (alertas)
    - Formato JSON para facilitar parsing
    """
    print("=== SIMULADOR DE SENSOR - Ejercicio 7 ===")
    print(f"Enviando temperaturas al FIFO: {FIFO_PATH}")
    print(f"Rango: {TEMP_MIN}°C - {TEMP_MAX}°C")
    print(f"Duración: {duracion_minutos} minutos")
    print(f"Intervalo: {intervalo_segundos} segundos")
    print("-" * 50)
    
    try:
        # Crear FIFO si no existe
        if not os.path.exists(FIFO_PATH):
            os.mkfifo(FIFO_PATH)
            print(f"FIFO creado: {FIFO_PATH}")
        
        # Abrir FIFO para escritura (se bloquea hasta que haya monitor)
        print("Esperando monitor de temperatura...")
        fd = os.open(FIFO_PATH, os.O_WRONLY)
        print("✅ Monitor conectado. Iniciando simulación...")
        
        tiempo_inicio = time.time()
        tiempo_fin = tiempo_inicio + (duracion_minutos * 60)
        lectura_count = 0
        
        # Temperatura base para generar variaciones realistas
        temp_base = random.uniform(22, 26)
        
        while time.time() < tiempo_fin:
            lectura_count += 1
            timestamp = datetime.now()
            
            # Generar temperatura con variación realista
            # Usar variación gradual + ruido aleatorio
            variacion_gradual = random.uniform(-0.5, 0.5)
            ruido = random.uniform(-0.2, 0.2)
            
            # Ocasionalmente generar picos de temperatura (10% probabilidad)
            if random.random() < 0.1:
                pico = random.uniform(1.0, 3.0)
                temp_actual = min(TEMP_MAX, temp_base + pico + ruido)
            else:
                temp_base += variacion_gradual * 0.1  # Cambio gradual lento
                temp_base = max(TEMP_MIN, min(TEMP_MAX, temp_base))  # Mantener en rango
                temp_actual = temp_base + ruido
            
            # Asegurar que esté en el rango válido
            temp_actual = max(TEMP_MIN, min(TEMP_MAX, temp_actual))
            
            # Crear mensaje JSON
            lectura = {
                'timestamp': timestamp.isoformat(),
                'temperatura': round(temp_actual, 2),
                'sensor_id': 'TEMP_001',
                'lectura_num': lectura_count,
                'unidad': 'celsius'
            }
            
            # Enviar al monitor
            mensaje = json.dumps(lectura) + '\n'
            os.write(fd, mensaje.encode())
            
            # Mostrar en simulador
            estado = "🔥 ALTA" if temp_actual > TEMP_ALERTA else "✅ NORMAL"
            print(f"📊 Lectura #{lectura_count}: {temp_actual:.2f}°C [{estado}]")
            
            time.sleep(intervalo_segundos)
        
        # Enviar señal de fin
        fin_msg = json.dumps({'fin_simulacion': True, 'total_lecturas': lectura_count}) + '\n'
        os.write(fd, fin_msg.encode())
        
        os.close(fd)
        print(f"✅ Simulación completada. {lectura_count} lecturas enviadas")
        
    except KeyboardInterrupt:
        print("\nSimulador interrumpido")
    except OSError as e:
        print(f"Error en simulador: {e}")

def monitor_temperatura():
    """
    Monitor que recibe y analiza lecturas de temperatura.
    
    Funcionalidades del monitor:
    - Lee datos del sensor via FIFO
    - Detecta temperaturas de alerta y críticas
    - Genera log con timestamp
    - Muestra estadísticas en tiempo real
    - Alertas visuales y sonoras (simuladas)
    """
    print("=== MONITOR DE TEMPERATURA - Ejercicio 7 ===")
    print(f"Monitoreando FIFO: {FIFO_PATH}")
    print(f"Alerta: > {TEMP_ALERTA}°C")
    print(f"Crítica: > {TEMP_CRITICA}°C")
    print(f"Log: {LOG_FILE}")
    print("-" * 50)
    
    try:
        # Verificar que el FIFO existe
        if not os.path.exists(FIFO_PATH):
            print(f"❌ FIFO {FIFO_PATH} no existe")
            print("Primero ejecuta el simulador de sensor")
            return
        
        # Abrir archivo de log
        with open(LOG_FILE, 'w', encoding='utf-8') as log_file:
            log_file.write(f"=== Monitor de Temperatura - {datetime.now()} ===\n")
            log_file.write(f"Alerta: {TEMP_ALERTA}°C | Crítica: {TEMP_CRITICA}°C\n")
            log_file.write("-" * 60 + "\n")
            
            # Abrir FIFO para lectura
            print("Conectando al sensor...")
            fd = os.open(FIFO_PATH, os.O_RDONLY)
            print("✅ Sensor conectado. Monitoreando...")
            
            # Estadísticas
            lecturas_totales = 0
            lecturas_normales = 0
            lecturas_alerta = 0
            lecturas_criticas = 0
            temp_min = float('inf')
            temp_max = float('-inf')
            suma_temperaturas = 0
            
            while True:
                # Leer línea del FIFO
                buffer = b""
                while True:
                    try:
                        char = os.read(fd, 1)
                        if not char:
                            print("📭 Sensor desconectado")
                            break
                        buffer += char
                        if char == b'\n':
                            break
                    except OSError:
                        break
                
                if not buffer:
                    break
                
                try:
                    # Parsear JSON
                    datos = json.loads(buffer.decode('utf-8'))
                    
                    # Verificar si es mensaje de fin
                    if 'fin_simulacion' in datos:
                        print("🏁 Simulación completada por el sensor")
                        log_file.write(f"[{datetime.now()}] Fin de simulación\n")
                        break
                    
                    # Procesar lectura de temperatura
                    timestamp_sensor = datos['timestamp']
                    temperatura = datos['temperatura']
                    sensor_id = datos.get('sensor_id', 'UNKNOWN')
                    lectura_num = datos.get('lectura_num', 0)
                    
                    # Actualizar estadísticas
                    lecturas_totales += 1
                    suma_temperaturas += temperatura
                    temp_min = min(temp_min, temperatura)
                    temp_max = max(temp_max, temperatura)
                    
                    # Determinar nivel de alerta
                    timestamp_monitor = datetime.now().strftime("%H:%M:%S")
                    
                    if temperatura > TEMP_CRITICA:
                        nivel = "🚨 CRÍTICA"
                        lecturas_criticas += 1
                        color = "\033[91m"  # Rojo
                    elif temperatura > TEMP_ALERTA:
                        nivel = "⚠️  ALERTA"
                        lecturas_alerta += 1
                        color = "\033[93m"  # Amarillo
                    else:
                        nivel = "✅ NORMAL"
                        lecturas_normales += 1
                        color = "\033[92m"  # Verde
                    
                    reset_color = "\033[0m"
                    
                    # Mostrar en monitor
                    print(f"{color}[{timestamp_monitor}] {sensor_id}: {temperatura:.2f}°C {nivel}{reset_color}")
                    
                    # Escribir al log
                    log_entry = f"[{timestamp_monitor}] {sensor_id} #{lectura_num}: {temperatura:.2f}°C - {nivel}\n"
                    log_file.write(log_entry)
                    log_file.flush()  # Forzar escritura inmediata
                    
                    # Alerta especial para temperaturas críticas
                    if temperatura > TEMP_CRITICA:
                        print("🔥🔥🔥 TEMPERATURA CRÍTICA DETECTADA 🔥🔥🔥")
                        alerta_critica = f"[{timestamp_monitor}] ALERTA CRÍTICA: {temperatura:.2f}°C\n"
                        log_file.write(alerta_critica)
                
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    print(f"❌ Error procesando datos: {e}")
                    continue
            
            # Escribir estadísticas finales al log
            promedio = suma_temperaturas / lecturas_totales if lecturas_totales > 0 else 0
            
            estadisticas = f"""
=== ESTADÍSTICAS FINALES ===
Total de lecturas: {lecturas_totales}
Lecturas normales: {lecturas_normales} ({lecturas_normales/lecturas_totales*100:.1f}%)
Lecturas de alerta: {lecturas_alerta} ({lecturas_alerta/lecturas_totales*100:.1f}%)
Lecturas críticas: {lecturas_criticas} ({lecturas_criticas/lecturas_totales*100:.1f}%)
Temperatura mínima: {temp_min:.2f}°C
Temperatura máxima: {temp_max:.2f}°C
Temperatura promedio: {promedio:.2f}°C
"""
            
            print(estadisticas)
            log_file.write(estadisticas)
            
        os.close(fd)
        print(f"📋 Log guardado en: {LOG_FILE}")
        
    except KeyboardInterrupt:
        print("\nMonitor interrumpido")
    except OSError as e:
        print(f"Error en monitor: {e}")

def demo_automatica():
    """
    Demo que ejecuta simulador y monitor automáticamente
    """
    print("=== DEMO AUTOMÁTICA - Monitor de Temperatura ===")
    print("Simulando sensor y monitor automáticamente")
    print("-" * 50)
    
    # Limpiar recursos previos
    limpiar_recursos()
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    
    # Crear FIFO
    os.mkfifo(FIFO_PATH)
    print(f"FIFO creado: {FIFO_PATH}")
    
    pid = os.fork()
    
    if pid > 0:  # Proceso padre (monitor)
        print("Proceso padre: MONITOR")
        time.sleep(0.5)  # Dar tiempo al sensor
        
        try:
            # Actuar como monitor
            with open(LOG_FILE, 'w', encoding='utf-8') as log_file:
                log_file.write(f"=== Demo Monitor - {datetime.now()} ===\n")
                
                fd = os.open(FIFO_PATH, os.O_RDONLY)
                print("✅ Monitor conectado")
                
                lecturas = 0
                alertas = 0
                
                while lecturas < 20:  # Limitar para demo
                    # Leer datos
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
                    
                    try:
                        datos = json.loads(buffer.decode())
                        
                        if 'fin_simulacion' in datos:
                            break
                        
                        temp = datos['temperatura']
                        lecturas += 1
                        
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        nivel = "🚨 ALERTA" if temp > TEMP_ALERTA else "✅ NORMAL"
                        
                        if temp > TEMP_ALERTA:
                            alertas += 1
                        
                        print(f"📊 [{timestamp}] {temp:.2f}°C {nivel}")
                        log_file.write(f"[{timestamp}] {temp:.2f}°C - {nivel}\n")
                        log_file.flush()
                        
                    except json.JSONDecodeError:
                        continue
                
                os.close(fd)
                log_file.write(f"\nDemo completada: {lecturas} lecturas, {alertas} alertas\n")
            
            print(f"Monitor terminado: {lecturas} lecturas, {alertas} alertas")
            
        except OSError as e:
            print(f"Error en monitor: {e}")
        
        # Esperar al proceso hijo
        os.waitpid(pid, 0)
        limpiar_recursos()
        
        # Mostrar log final
        print(f"\n--- Contenido del log {LOG_FILE} ---")
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                print(f.read())
        except Exception as e:
            print(f"Error leyendo log: {e}")
        
    elif pid == 0:  # Proceso hijo (sensor)
        print("Proceso hijo: SENSOR")
        time.sleep(1)  # Dar tiempo al monitor
        
        try:
            # Actuar como sensor
            fd = os.open(FIFO_PATH, os.O_WRONLY)
            
            # Generar 20 lecturas para demo rápida
            for i in range(1, 21):
                # Generar temperatura con algunos picos
                if i % 7 == 0:  # Cada 7 lecturas, generar alerta
                    temp = random.uniform(28.5, 29.8)
                else:
                    temp = random.uniform(20.5, 27.5)
                
                lectura = {
                    'timestamp': datetime.now().isoformat(),
                    'temperatura': round(temp, 2),
                    'sensor_id': 'DEMO_SENSOR',
                    'lectura_num': i
                }
                
                mensaje = json.dumps(lectura) + '\n'
                os.write(fd, mensaje.encode())
                print(f"📤 Sensor envió: {temp:.2f}°C")
                
                time.sleep(0.5)
            
            # Señal de fin
            fin = json.dumps({'fin_simulacion': True}) + '\n'
            os.write(fd, fin.encode())
            
            os.close(fd)
            print("Sensor terminado")
            
        except OSError as e:
            print(f"Error en sensor: {e}")
        
        sys.exit(0)
    
    else:
        print("Error en fork()")
        sys.exit(1)

def main():
    # Configurar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Ejercicio 7: Monitor de temperatura simulado")
    print("Sistema de monitoreo IoT usando FIFOs")
    print("Elige el componente:")
    print("1. Simulador de sensor (genera temperaturas aleatorias)")
    print("2. Monitor (recibe y analiza temperaturas)")
    print("3. Demo automática (sensor + monitor)")
    
    try:
        opcion = input("\nSelecciona una opción (1-3): ").strip()
        
        if opcion == '1':
            duracion = input("Duración en minutos (default 5): ").strip()
            duracion = float(duracion) if duracion else 5.0
            
            intervalo = input("Intervalo en segundos (default 1): ").strip()
            intervalo = float(intervalo) if intervalo else 1.0
            
            simulador_sensor(duracion, intervalo)
        elif opcion == '2':
            monitor_temperatura()
        elif opcion == '3':
            demo_automatica()
        else:
            print("Opción inválida")
            
    except (EOFError, KeyboardInterrupt):
        print("\nPrograma interrumpido")
        limpiar_recursos()

if __name__ == "__main__":
    main()