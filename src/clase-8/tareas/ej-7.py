#!/usr/bin/env python3

# Ejercicio 7 · Nivel Intermedio +
#
# Enunciado: Desarrolla un load balancer simple: un proceso maestro reparte una lista de URLs 
# a descargar entre k procesos worker mediante una Queue. Cada worker registra su PID y el 
# tiempo de descarga. Al finalizar, el maestro debe generar un reporte ordenado por duración.

from multiprocessing import Process, Queue, current_process
import time
import random
import urllib.request
import urllib.error

def simular_descarga(url):
    """
    Simula la descarga de una URL con tiempo variable.
    
    En un caso real, usaríamos requests o urllib para descargas HTTP reales.
    Aquí simulamos diferentes tipos de respuesta para hacer el ejercicio más educativo.
    
    Args:
        url: URL a "descargar"
    
    Returns:
        dict: Información sobre la descarga simulada
    """
    # Simular diferentes tiempos de respuesta según el dominio
    if 'fast' in url:
        tiempo_descarga = random.uniform(0.1, 0.5)  # Sitio rápido
    elif 'slow' in url:
        tiempo_descarga = random.uniform(2.0, 4.0)   # Sitio lento
    elif 'timeout' in url:
        tiempo_descarga = random.uniform(5.0, 8.0)   # Sitio muy lento
    else:
        tiempo_descarga = random.uniform(0.5, 2.0)   # Tiempo normal
    
    # Simular el tiempo de descarga
    time.sleep(tiempo_descarga)
    
    # Simular diferentes tamaños de respuesta
    tamano_simulado = random.randint(1024, 1024*100)  # 1KB - 100KB
    
    # Simular ocasionales errores (10% de probabilidad)
    if random.random() < 0.1:
        raise urllib.error.URLError(f"Error simulado para {url}")
    
    return {
        'tamano': tamano_simulado,
        'tiempo': tiempo_descarga,
        'status': 200
    }

def worker_descargador(queue_tareas, queue_resultados, worker_id):
    """
    Proceso worker que descarga URLs de la cola de tareas.
    
    Patrón típico de worker pool:
    1. Toma tareas de una Queue compartida
    2. Procesa cada tarea
    3. Envía resultados a otra Queue
    4. Continúa hasta recibir señal de "fin"
    
    Args:
        queue_tareas: Queue con URLs para descargar
        queue_resultados: Queue para enviar resultados
        worker_id: ID único del worker
    """
    pid = current_process().pid
    print(f"[Worker {worker_id}] Iniciado - PID: {pid}")
    
    descargas_completadas = 0
    tiempo_total_worker = 0
    
    while True:
        try:
            # Obtener tarea de la cola (bloquea hasta que haya una disponible)
            # get() con timeout para evitar bloqueo infinito
            tarea = queue_tareas.get(timeout=1)
            
            # Verificar señal de fin
            if tarea is None:
                print(f"[Worker {worker_id}] Recibida señal de fin")
                break
            
            url = tarea['url']
            tarea_id = tarea['id']
            
            print(f"[Worker {worker_id}] Descargando {url}...")
            
            inicio = time.perf_counter()
            
            try:
                # Simular descarga
                info_descarga = simular_descarga(url)
                
                fin = time.perf_counter()
                duracion = fin - inicio
                tiempo_total_worker += duracion
                descargas_completadas += 1
                
                # Crear resultado exitoso
                resultado = {
                    'worker_id': worker_id,
                    'worker_pid': pid,
                    'tarea_id': tarea_id,
                    'url': url,
                    'duracion': duracion,
                    'tamano': info_descarga['tamano'],
                    'status': 'success',
                    'timestamp': time.time()
                }
                
                print(f"[Worker {worker_id}] ✅ {url} completada en {duracion:.2f}s ({info_descarga['tamano']} bytes)")
                
            except Exception as e:
                fin = time.perf_counter()
                duracion = fin - inicio
                
                # Crear resultado de error
                resultado = {
                    'worker_id': worker_id,
                    'worker_pid': pid,
                    'tarea_id': tarea_id,
                    'url': url,
                    'duracion': duracion,
                    'status': 'error',
                    'error': str(e),
                    'timestamp': time.time()
                }
                
                print(f"[Worker {worker_id}] ❌ Error en {url}: {e}")
            
            # Enviar resultado a la cola de resultados
            queue_resultados.put(resultado)
            
        except:
            # Timeout o error en get() - probablemente no hay más tareas
            print(f"[Worker {worker_id}] No hay más tareas, terminando")
            break
    
    print(f"[Worker {worker_id}] Terminado - {descargas_completadas} descargas, {tiempo_total_worker:.2f}s total")

def load_balancer_maestro(urls, num_workers=4):
    """
    Proceso maestro que distribuye tareas entre workers y recolecta resultados.
    
    Load Balancer simple que:
    1. Distribuye URLs entre workers disponibles
    2. Recolecta resultados de todos los workers
    3. Genera reporte final ordenado por duración
    
    Args:
        urls: Lista de URLs para descargar
        num_workers: Número de procesos worker a crear
    """
    print(f"=== Load Balancer Maestro ===")
    print(f"URLs a procesar: {len(urls)}")
    print(f"Workers: {num_workers}")
    
    # Crear colas para comunicación
    queue_tareas = Queue()
    queue_resultados = Queue()
    
    # Llenar cola de tareas
    print(f"\n[Maestro] Distribuyendo {len(urls)} tareas...")
    for i, url in enumerate(urls):
        tarea = {
            'id': i + 1,
            'url': url
        }
        queue_tareas.put(tarea)
        print(f"[Maestro] Tarea {i + 1}: {url}")
    
    # Agregar señales de fin (una por worker)
    for _ in range(num_workers):
        queue_tareas.put(None)
    
    print(f"\n[Maestro] Creando {num_workers} workers...")
    
    # Crear y lanzar workers
    workers = []
    inicio_total = time.perf_counter()
    
    for i in range(num_workers):
        worker = Process(
            target=worker_descargador,
            args=(queue_tareas, queue_resultados, i + 1)
        )
        workers.append(worker)
        worker.start()
        print(f"[Maestro] Worker {i + 1} iniciado - PID: {worker.pid}")
    
    print(f"\n[Maestro] Recolectando resultados...")
    
    # Recolectar resultados
    resultados = []
    for _ in range(len(urls)):  # Esperamos un resultado por URL
        resultado = queue_resultados.get()
        resultados.append(resultado)
        
        status_icon = "✅" if resultado['status'] == 'success' else "❌"
        print(f"[Maestro] {status_icon} Resultado recibido de Worker {resultado['worker_id']}: {resultado['url']}")
    
    print(f"\n[Maestro] Esperando finalización de workers...")
    
    # Esperar que terminen todos los workers
    for i, worker in enumerate(workers):
        worker.join()
        print(f"[Maestro] Worker {i + 1} terminado")
    
    fin_total = time.perf_counter()
    tiempo_total = fin_total - inicio_total
    
    # Generar reporte final
    generar_reporte(resultados, tiempo_total, num_workers)

def generar_reporte(resultados, tiempo_total, num_workers):
    """
    Genera un reporte detallado de las descargas ordenado por duración.
    
    Args:
        resultados: Lista de resultados de las descargas
        tiempo_total: Tiempo total del proceso
        num_workers: Número de workers utilizados
    """
    print(f"\n" + "="*80)
    print("📊 REPORTE DE LOAD BALANCER")
    print("="*80)
    
    # Ordenar resultados por duración (descendente)
    resultados_ordenados = sorted(resultados, key=lambda x: x['duracion'], reverse=True)
    
    # Estadísticas generales
    exitosos = [r for r in resultados if r['status'] == 'success']
    errores = [r for r in resultados if r['status'] == 'error']
    
    print(f"Total de URLs procesadas: {len(resultados)}")
    print(f"Descargas exitosas: {len(exitosos)}")
    print(f"Errores: {len(errores)}")
    print(f"Tiempo total: {tiempo_total:.2f} segundos")
    print(f"Workers utilizados: {num_workers}")
    
    if exitosos:
        duraciones = [r['duracion'] for r in exitosos]
        tamanos_total = sum(r['tamano'] for r in exitosos)
        
        print(f"\nEstadísticas de descarga:")
        print(f"  Duración promedio: {sum(duraciones) / len(duraciones):.2f}s")
        print(f"  Duración más rápida: {min(duraciones):.2f}s")
        print(f"  Duración más lenta: {max(duraciones):.2f}s")
        print(f"  Total descargado: {tamanos_total:,} bytes ({tamanos_total/1024:.1f} KB)")
    
    # Reporte por worker
    print(f"\n📋 RENDIMIENTO POR WORKER:")
    workers_stats = {}
    for resultado in resultados:
        wid = resultado['worker_id']
        if wid not in workers_stats:
            workers_stats[wid] = {
                'pid': resultado['worker_pid'],
                'total_tareas': 0,
                'tiempo_total': 0,
                'exitosas': 0,
                'errores': 0
            }
        
        workers_stats[wid]['total_tareas'] += 1
        workers_stats[wid]['tiempo_total'] += resultado['duracion']
        
        if resultado['status'] == 'success':
            workers_stats[wid]['exitosas'] += 1
        else:
            workers_stats[wid]['errores'] += 1
    
    for wid in sorted(workers_stats.keys()):
        stats = workers_stats[wid]
        eficiencia = (stats['exitosas'] / stats['total_tareas']) * 100 if stats['total_tareas'] > 0 else 0
        print(f"  Worker {wid} (PID {stats['pid']}): {stats['total_tareas']} tareas, "
              f"{stats['tiempo_total']:.2f}s total, {eficiencia:.1f}% éxito")
    
    # Top 10 descargas más lentas
    print(f"\n🐌 TOP 10 DESCARGAS MÁS LENTAS:")
    for i, resultado in enumerate(resultados_ordenados[:10], 1):
        status_icon = "✅" if resultado['status'] == 'success' else "❌"
        tamano_str = f"({resultado['tamano']:,} bytes)" if 'tamano' in resultado else ""
        print(f"  {i:2d}. {status_icon} {resultado['url'][:50]:50} "
              f"{resultado['duracion']:6.2f}s Worker-{resultado['worker_id']} {tamano_str}")
    
    # Errores si los hay
    if errores:
        print(f"\n❌ ERRORES ENCONTRADOS ({len(errores)}):")
        for error in errores:
            print(f"  • {error['url']}: {error['error']}")
    
    print("="*80)

def main():
    """
    Función principal que configura y ejecuta el load balancer.
    """
    print("=== Ejercicio 7: Load Balancer Simple ===")
    
    # Lista de URLs simuladas para descargar
    urls_test = [
        "https://fast-api.example.com/data1",
        "https://slow-server.example.com/bigfile",
        "https://normal-site.example.com/page1",
        "https://fast-cdn.example.com/image1.jpg",
        "https://timeout-prone.example.com/data",
        "https://normal-site.example.com/page2", 
        "https://fast-api.example.com/data2",
        "https://slow-server.example.com/report",
        "https://normal-site.example.com/page3",
        "https://fast-cdn.example.com/image2.jpg",
        "https://timeout-prone.example.com/slow-query",
        "https://normal-site.example.com/page4",
        "https://fast-api.example.com/data3",
        "https://slow-server.example.com/archive",
        "https://normal-site.example.com/page5"
    ]
    
    # Configuración
    num_workers = 4
    
    print(f"Configuración del Load Balancer:")
    print(f"  URLs a procesar: {len(urls_test)}")
    print(f"  Workers: {num_workers}")
    print(f"  Distribución automática de tareas")
    
    # Semilla para reproducibilidad
    random.seed(42)
    
    # Ejecutar load balancer
    load_balancer_maestro(urls_test, num_workers)
    
    print(f"\n💡 CONCEPTOS DEMOSTRADOS:")
    print(f"1. Load Balancing: Distribución automática de tareas")
    print(f"2. Worker Pool: Múltiples procesos trabajando en paralelo")
    print(f"3. Queue como mecanismo de comunicación producer-consumer")
    print(f"4. Recolección y análisis de métricas de rendimiento")
    print(f"5. Manejo de errores en entorno distribuido")

if __name__ == '__main__':
    main()