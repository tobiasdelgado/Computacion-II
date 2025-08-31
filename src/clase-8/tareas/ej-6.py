#!/usr/bin/env python3

# Ejercicio 6 · Nivel Intermedio
#
# Enunciado: Implementa un cronómetro compartido: tres procesos actualizan cada segundo 
# un valor Value('d') con el instante actual. Un cuarto proceso lee el valor cada 0,5 s 
# y registra si hay incoherencias temporales (> 1 s de salto), demostrando la necesidad 
# de sincronización.

from multiprocessing import Process, Value, current_process
import time
import random

def actualizador_tiempo(cronometro, proceso_id, duracion=10):
    """
    Proceso que actualiza el cronómetro compartido cada segundo.
    
    Value('d') crea un double/float compartido entre procesos.
    Sin Lock, múltiples procesos pueden escribir simultáneamente
    causando inconsistencias en los datos.
    
    Args:
        cronometro: Value('d') compartido que contiene timestamp
        proceso_id: ID del proceso actualizador
        duracion: Duración en segundos del proceso
    """
    print(f"[Actualizador {proceso_id}] Iniciado - PID: {current_process().pid}")
    
    fin_tiempo = time.time() + duracion
    
    while time.time() < fin_tiempo:
        # Obtener timestamp actual
        timestamp_actual = time.time()
        
        # CONDICIÓN DE CARRERA: Sin sincronización
        # Múltiples procesos pueden escribir al mismo tiempo
        cronometro.value = timestamp_actual
        
        timestamp_legible = time.strftime("%H:%M:%S", time.localtime(timestamp_actual))
        print(f"[Actualizador {proceso_id}] Actualizado: {timestamp_legible} ({timestamp_actual:.3f})")
        
        # Cada proceso actualiza con frecuencia ligeramente diferente
        # para crear más oportunidades de condición de carrera
        intervalo = 1.0 + random.uniform(-0.2, 0.2)  # 0.8 - 1.2 segundos
        time.sleep(intervalo)
    
    print(f"[Actualizador {proceso_id}] Terminado")

def monitor_tiempo(cronometro, duracion=10):
    """
    Proceso que monitorea el cronómetro y detecta incoherencias temporales.
    
    Lee el cronómetro cada 0.5s y verifica si hay saltos temporales
    mayores a 1 segundo, lo que indicaría inconsistencias.
    
    Args:
        cronometro: Value('d') compartido para leer timestamps
        duracion: Duración en segundos del monitoreo
    """
    print(f"[Monitor] Iniciado - PID: {current_process().pid}")
    
    fin_tiempo = time.time() + duracion
    timestamp_anterior = None
    lecturas = 0
    incoherencias = 0
    saltos_grandes = []
    
    while time.time() < fin_tiempo:
        # Leer timestamp del cronómetro compartido
        timestamp_leido = cronometro.value
        timestamp_actual = time.time()
        
        lecturas += 1
        
        # Convertir a formato legible
        if timestamp_leido > 0:  # Verificar que se haya inicializado
            tiempo_legible = time.strftime("%H:%M:%S", time.localtime(timestamp_leido))
            
            print(f"[Monitor] Lectura {lecturas}: {tiempo_legible} ({timestamp_leido:.3f})")
            
            # Verificar incoherencias temporales
            if timestamp_anterior is not None:
                diferencia = timestamp_leido - timestamp_anterior
                
                # Detectar saltos temporales grandes (> 1.5 segundos)
                if abs(diferencia) > 1.5:
                    incoherencias += 1
                    saltos_grandes.append({
                        'lectura': lecturas,
                        'anterior': timestamp_anterior,
                        'actual': timestamp_leido,
                        'diferencia': diferencia
                    })
                    print(f"⚠️  [Monitor] INCOHERENCIA #{incoherencias}: Salto de {diferencia:.3f}s")
                
                # Detectar tiempo "retrocediendo" (muy raro pero posible)
                elif diferencia < -0.1:
                    incoherencias += 1
                    saltos_grandes.append({
                        'lectura': lecturas,
                        'anterior': timestamp_anterior,
                        'actual': timestamp_leido,
                        'diferencia': diferencia
                    })
                    print(f"🔄 [Monitor] TIEMPO RETROCEDIÓ #{incoherencias}: {diferencia:.3f}s")
            
            timestamp_anterior = timestamp_leido
        else:
            print(f"[Monitor] Lectura {lecturas}: Cronómetro no inicializado")
        
        time.sleep(0.5)  # Monitorear cada 0.5 segundos
    
    print(f"\n[Monitor] Terminado")
    print(f"[Monitor] Total lecturas: {lecturas}")
    print(f"[Monitor] Incoherencias detectadas: {incoherencias}")
    
    # Mostrar detalles de incoherencias
    if saltos_grandes:
        print(f"\n[Monitor] Detalles de incoherencias:")
        for salto in saltos_grandes:
            anterior_str = time.strftime("%H:%M:%S", time.localtime(salto['anterior']))
            actual_str = time.strftime("%H:%M:%S", time.localtime(salto['actual']))
            print(f"  Lectura {salto['lectura']}: {anterior_str} -> {actual_str} (Δ: {salto['diferencia']:.3f}s)")
    
    return lecturas, incoherencias, saltos_grandes

def main():
    """
    Proceso principal que coordina actualizadores y monitor.
    """
    print("=== Ejercicio 6: Cronómetro compartido sin sincronización ===")
    print(f"[Principal] PID: {current_process().pid}")
    
    # Crear cronómetro compartido
    # Value('d') crea un double (float) compartido
    cronometro = Value('d', 0.0)
    
    print("[Principal] Cronómetro compartido creado")
    print("[Principal] Configuración:")
    print("  - 3 procesos actualizadores (cada ~1s)")
    print("  - 1 proceso monitor (cada 0.5s)")
    print("  - Duración: 10 segundos")
    print("  - Sin sincronización (condición de carrera esperada)")
    
    # Configuración
    duracion = 10
    
    # Crear procesos actualizadores
    actualizadores = []
    for i in range(3):
        proceso = Process(
            target=actualizador_tiempo,
            args=(cronometro, i + 1, duracion)
        )
        actualizadores.append(proceso)
    
    # Crear proceso monitor
    proceso_monitor = Process(
        target=monitor_tiempo,
        args=(cronometro, duracion)
    )
    
    print(f"\n[Principal] Iniciando procesos...")
    inicio_experimento = time.time()
    
    # Iniciar todos los procesos
    for i, proceso in enumerate(actualizadores):
        proceso.start()
        print(f"[Principal] Actualizador {i + 1} iniciado - PID: {proceso.pid}")
    
    proceso_monitor.start()
    print(f"[Principal] Monitor iniciado - PID: {proceso_monitor.pid}")
    
    print(f"\n[Principal] Experimento en progreso...")
    print("Observa las incoherencias temporales causadas por falta de sincronización")
    
    # Esperar que terminen todos los procesos
    print(f"\n[Principal] Esperando finalización de procesos...")
    
    for i, proceso in enumerate(actualizadores):
        proceso.join()
        print(f"[Principal] Actualizador {i + 1} terminado")
    
    proceso_monitor.join()
    print("[Principal] Monitor terminado")
    
    fin_experimento = time.time()
    duracion_real = fin_experimento - inicio_experimento
    
    # Resumen final
    print(f"\n" + "="*60)
    print("📊 RESUMEN DEL EXPERIMENTO")
    print("="*60)
    print(f"Duración planificada: {duracion} segundos")
    print(f"Duración real: {duracion_real:.1f} segundos")
    print(f"Valor final del cronómetro: {cronometro.value:.3f}")
    
    if cronometro.value > 0:
        tiempo_final = time.strftime("%H:%M:%S", time.localtime(cronometro.value))
        print(f"Timestamp final: {tiempo_final}")
    
    print(f"\n🔍 ANÁLISIS:")
    print("1. Sin Lock, múltiples procesos escriben simultáneamente")
    print("2. Esto puede causar lecturas inconsistentes en el monitor")
    print("3. Los 'saltos temporales' demuestran condiciones de carrera")
    print("4. En un sistema real, usarías Lock para sincronización")
    
    print(f"\n💡 SOLUCIÓN:")
    print("Usar Lock alrededor de cronometro.value para operaciones atómicas")
    print("Ejemplo: with lock: cronometro.value = timestamp")

def demo_con_lock():
    """
    Demo que muestra cómo sería con Lock (para comparar).
    """
    from multiprocessing import Lock
    
    print(f"\n" + "="*60)
    print("🔒 DEMO CON LOCK (para comparar)")
    print("="*60)
    
    cronometro = Value('d', 0.0)
    lock = Lock()
    
    def actualizador_seguro(cronometro, lock, proceso_id, duracion=5):
        fin_tiempo = time.time() + duracion
        while time.time() < fin_tiempo:
            timestamp_actual = time.time()
            
            # Operación atómica con Lock
            with lock:
                cronometro.value = timestamp_actual
            
            timestamp_legible = time.strftime("%H:%M:%S", time.localtime(timestamp_actual))
            print(f"[Actualizador Seguro {proceso_id}] Actualizado: {timestamp_legible}")
            time.sleep(1)
    
    # Crear procesos con Lock
    procesos = []
    for i in range(2):
        p = Process(target=actualizador_seguro, args=(cronometro, lock, i + 1))
        procesos.append(p)
        p.start()
    
    # Monitor simple
    for _ in range(10):
        with lock:
            valor = cronometro.value
        if valor > 0:
            tiempo = time.strftime("%H:%M:%S", time.localtime(valor))
            print(f"[Monitor Seguro] Leído: {tiempo}")
        time.sleep(0.5)
    
    for p in procesos:
        p.join()
    
    print("✅ Con Lock: No se detectaron incoherencias")

if __name__ == '__main__':
    main()
    
    print(f"\n" + "="*80)
    respuesta = input("¿Ejecutar demo con Lock para comparar? (s/n): ")
    if respuesta.lower() in ['s', 'si', 'y', 'yes']:
        demo_con_lock()