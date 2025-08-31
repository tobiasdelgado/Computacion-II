#!/usr/bin/env python3

# Ejercicio 4 · Nivel Avanzado
#
# Objetivo: medir el impacto del GIL versus multiprocessing en tareas CPU-bound.
#
# Enunciado: implementa la función fibonacci(n) de forma recursiva e imprímela para n = 35. 
# Mide primero el tiempo usando hilos (threading.Thread) con 4 hilos y luego con 4 procesos 
# (multiprocessing.Process). Compara y explica la diferencia.

import time
import threading
from multiprocessing import Process, current_process, Queue
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def fibonacci(n):
    """
    Implementación recursiva de Fibonacci (intencionalmente ineficiente).
    
    Esta función es CPU-intensiva y recursiva, perfecta para demostrar 
    la diferencia entre threading (limitado por GIL) y multiprocessing.
    
    Para n=35, hace aproximadamente 29 millones de llamadas recursivas.
    """
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def fibonacci_worker_thread(n, result_dict, thread_id):
    """
    Worker para threading que calcula Fibonacci y guarda resultado.
    
    En threading, los hilos comparten memoria pero están limitados por el GIL.
    Solo un hilo puede ejecutar código Python a la vez.
    """
    print(f"[Thread {thread_id}] Calculando fibonacci({n})...")
    inicio = time.perf_counter()
    resultado = fibonacci(n)
    fin = time.perf_counter()
    
    result_dict[thread_id] = {
        'resultado': resultado,
        'tiempo': fin - inicio,
        'n': n
    }
    print(f"[Thread {thread_id}] Resultado: {resultado}, Tiempo: {fin - inicio:.3f}s")

def fibonacci_worker_process(n, queue, process_id):
    """
    Worker para multiprocessing que calcula Fibonacci y envía resultado por Queue.
    
    En multiprocessing, cada proceso tiene su propio intérprete Python
    sin limitaciones del GIL.
    """
    print(f"[Process {process_id}] PID: {current_process().pid}, Calculando fibonacci({n})...")
    inicio = time.perf_counter()
    resultado = fibonacci(n)
    fin = time.perf_counter()
    
    queue.put({
        'process_id': process_id,
        'resultado': resultado,
        'tiempo': fin - inicio,
        'n': n,
        'pid': current_process().pid
    })
    print(f"[Process {process_id}] Resultado: {resultado}, Tiempo: {fin - inicio:.3f}s")

def test_secuencial(n, repeticiones=4):
    """
    Versión secuencial como baseline para comparar.
    """
    print("\n" + "="*60)
    print("🔵 PRUEBA SECUENCIAL (Baseline)")
    print("="*60)
    
    print(f"Calculando fibonacci({n}) {repeticiones} veces secuencialmente...")
    
    inicio = time.perf_counter()
    resultados = []
    
    for i in range(repeticiones):
        print(f"[Secuencial] Cálculo {i + 1}/{repeticiones}...")
        inicio_calc = time.perf_counter()
        resultado = fibonacci(n)
        fin_calc = time.perf_counter()
        
        resultados.append({
            'resultado': resultado,
            'tiempo': fin_calc - inicio_calc
        })
        print(f"[Secuencial] Resultado {i + 1}: {resultado}, Tiempo: {fin_calc - inicio_calc:.3f}s")
    
    fin = time.perf_counter()
    tiempo_total = fin - inicio
    
    print(f"\n📊 RESULTADOS SECUENCIALES:")
    print(f"Tiempo total: {tiempo_total:.3f} segundos")
    print(f"Tiempo promedio por cálculo: {tiempo_total / repeticiones:.3f} segundos")
    print(f"Resultado fibonacci({n}): {resultados[0]['resultado']}")
    
    return tiempo_total, resultados

def test_threading(n, num_threads=4):
    """
    Prueba usando threading.Thread - limitado por GIL.
    """
    print("\n" + "="*60)
    print("🟡 PRUEBA CON THREADING (Limitado por GIL)")
    print("="*60)
    
    print(f"Calculando fibonacci({n}) con {num_threads} hilos...")
    
    # Diccionario compartido para resultados (threads comparten memoria)
    resultados = {}
    threads = []
    
    inicio = time.perf_counter()
    
    # Crear y lanzar hilos
    for i in range(num_threads):
        thread = threading.Thread(
            target=fibonacci_worker_thread, 
            args=(n, resultados, i + 1)
        )
        threads.append(thread)
        thread.start()
    
    # Esperar que todos los hilos terminen
    for thread in threads:
        thread.join()
    
    fin = time.perf_counter()
    tiempo_total = fin - inicio
    
    print(f"\n📊 RESULTADOS THREADING:")
    print(f"Tiempo total: {tiempo_total:.3f} segundos")
    print(f"Número de hilos: {num_threads}")
    
    tiempos = [r['tiempo'] for r in resultados.values()]
    print(f"Tiempo promedio por hilo: {sum(tiempos) / len(tiempos):.3f} segundos")
    print(f"Resultado fibonacci({n}): {list(resultados.values())[0]['resultado']}")
    
    return tiempo_total, resultados

def test_multiprocessing(n, num_processes=4):
    """
    Prueba usando multiprocessing.Process - sin limitaciones de GIL.
    """
    print("\n" + "="*60)
    print("🟢 PRUEBA CON MULTIPROCESSING (Sin limitaciones de GIL)")
    print("="*60)
    
    print(f"Calculando fibonacci({n}) con {num_processes} procesos...")
    
    # Queue para comunicación entre procesos
    queue = Queue()
    processes = []
    
    inicio = time.perf_counter()
    
    # Crear y lanzar procesos
    for i in range(num_processes):
        process = Process(
            target=fibonacci_worker_process, 
            args=(n, queue, i + 1)
        )
        processes.append(process)
        process.start()
    
    # Recolectar resultados
    resultados = {}
    for i in range(num_processes):
        resultado = queue.get()
        resultados[resultado['process_id']] = resultado
    
    # Esperar que todos los procesos terminen
    for process in processes:
        process.join()
    
    fin = time.perf_counter()
    tiempo_total = fin - inicio
    
    print(f"\n📊 RESULTADOS MULTIPROCESSING:")
    print(f"Tiempo total: {tiempo_total:.3f} segundos")
    print(f"Número de procesos: {num_processes}")
    
    tiempos = [r['tiempo'] for r in resultados.values()]
    print(f"Tiempo promedio por proceso: {sum(tiempos) / len(tiempos):.3f} segundos")
    print(f"Resultado fibonacci({n}): {list(resultados.values())[0]['resultado']}")
    
    # Mostrar PIDs de procesos
    pids = [r['pid'] for r in resultados.values()]
    print(f"PIDs de procesos: {pids}")
    
    return tiempo_total, resultados

def main():
    """
    Función principal que ejecuta todas las pruebas y compara resultados.
    """
    print("=== Ejercicio 4: GIL vs Multiprocessing en tareas CPU-bound ===")
    
    # Configuración
    n = 35  # Fibonacci de 35 (toma varios segundos)
    num_workers = 4
    
    print(f"Configuración:")
    print(f"- Número Fibonacci: {n}")
    print(f"- Workers por método: {num_workers}")
    print(f"- Complejidad esperada: O(2^n) ≈ {2**n:,} operaciones")
    
    # Ejecutar todas las pruebas
    tiempo_secuencial, _ = test_secuencial(n, num_workers)
    tiempo_threading, _ = test_threading(n, num_workers)
    tiempo_multiprocessing, _ = test_multiprocessing(n, num_workers)
    
    # Análisis comparativo
    print("\n" + "="*80)
    print("📊 ANÁLISIS COMPARATIVO")
    print("="*80)
    
    print(f"Tiempo secuencial:     {tiempo_secuencial:.3f} segundos")
    print(f"Tiempo threading:      {tiempo_threading:.3f} segundos")
    print(f"Tiempo multiprocessing: {tiempo_multiprocessing:.3f} segundos")
    
    # Calcular speed-ups
    speedup_threading = tiempo_secuencial / tiempo_threading
    speedup_multiprocessing = tiempo_secuencial / tiempo_multiprocessing
    
    print(f"\nSpeed-up (mayor es mejor):")
    print(f"Threading:      {speedup_threading:.2f}x")
    print(f"Multiprocessing: {speedup_multiprocessing:.2f}x")
    
    # Eficiencia (speed-up / número de workers)
    eficiencia_threading = speedup_threading / num_workers
    eficiencia_multiprocessing = speedup_multiprocessing / num_workers
    
    print(f"\nEficiencia (0.0-1.0, mayor es mejor):")
    print(f"Threading:      {eficiencia_threading:.2f} ({eficiencia_threading*100:.1f}%)")
    print(f"Multiprocessing: {eficiencia_multiprocessing:.2f} ({eficiencia_multiprocessing*100:.1f}%)")
    
    # Explicación de resultados
    print(f"\n🔍 EXPLICACIÓN DE RESULTADOS:")
    print(f"\n1. THREADING (Hilos):")
    if speedup_threading < 1.5:
        print("   ❌ Poco o ningún speed-up debido al GIL (Global Interpreter Lock)")
        print("   - Solo un hilo puede ejecutar código Python a la vez")
        print("   - Los hilos se turnan para ejecutar, no hay paralelismo real")
        print("   - Útil para I/O-bound tasks, inútil para CPU-bound tasks")
    
    print(f"\n2. MULTIPROCESSING (Procesos):")
    if speedup_multiprocessing > 2.0:
        print("   ✅ Speed-up significativo sin limitaciones de GIL")
        print("   - Cada proceso tiene su propio intérprete Python")
        print("   - Paralelismo real en múltiples cores de CPU")
        print("   - Ideal para CPU-bound tasks como cálculos matemáticos")
    
    print(f"\n3. CONCLUSIONES:")
    print(f"   - Para tareas CPU-intensivas: usar multiprocessing")
    print(f"   - Para tareas I/O-intensivas: threading puede ser suficiente")
    print(f"   - El GIL es la razón principal de la diferencia de rendimiento")
    
    print(f"\n💡 LECCIÓN APRENDIDA:")
    print(f"El GIL de Python limita el paralelismo real con threads en tareas CPU-bound")

if __name__ == '__main__':
    main()