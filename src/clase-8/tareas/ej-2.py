#!/usr/bin/env python3

# Ejercicio 2 · Nivel Intermedio
#
# Objetivo: usar Queue para reunir resultados de varios procesos.
#
# Enunciado: implementa un script que genere n = 4 procesos; cada proceso calcula la suma 
# de los primeros k = 1,000,000 enteros y deposita el resultado en una Queue. El padre 
# recoge los cuatro resultados y verifica que sean idénticos.

from multiprocessing import Process, Queue, current_process
import time

def worker(k, q, worker_id):
    """
    Función worker que calcula la suma de los primeros k enteros.
    
    En multiprocessing, Queue es thread-safe y process-safe.
    Permite comunicación many-to-one (múltiples procesos escriben, uno lee).
    
    Args:
        k: Número de enteros a sumar (hasta k-1 porque range(k) va de 0 a k-1)
        q: Queue compartida donde depositar el resultado
        worker_id: ID del worker para identificación
    """
    print(f"[Worker {worker_id}] Iniciado - PID: {current_process().pid}")
    
    # Medir tiempo de cálculo
    inicio = time.perf_counter()
    
    # Calcular suma: 0 + 1 + 2 + ... + (k-1)
    # sum(range(k)) es equivalente a la fórmula: k*(k-1)/2
    resultado = sum(range(k))
    
    fin = time.perf_counter()
    tiempo = fin - inicio
    
    print(f"[Worker {worker_id}] Suma calculada: {resultado}")
    print(f"[Worker {worker_id}] Tiempo: {tiempo:.3f} segundos")
    
    # Depositar resultado en la Queue
    # put() es thread-safe y process-safe
    q.put({
        'worker_id': worker_id,
        'resultado': resultado,
        'tiempo': tiempo,
        'pid': current_process().pid
    })
    
    print(f"[Worker {worker_id}] Resultado depositado en Queue")

def main():
    """
    Proceso principal que coordina los workers y recolecta resultados.
    """
    print("=== Ejercicio 2: Queue para múltiples procesos ===")
    
    # Configuración
    k = 1_000_000  # Calcular suma de 0 a 999,999
    n_procesos = 4
    
    print(f"Calculando suma de primeros {k:,} enteros con {n_procesos} procesos")
    print(f"Resultado esperado: {(k * (k - 1)) // 2:,}")
    
    # Crear Queue compartida
    # Queue de multiprocessing usa pipes y locks internamente
    q = Queue()
    
    # Crear y lanzar procesos workers
    procesos = []
    inicio_total = time.perf_counter()
    
    print(f"\n[Padre] Creando {n_procesos} procesos workers...")
    
    for i in range(n_procesos):
        proceso = Process(target=worker, args=(k, q, i + 1))
        procesos.append(proceso)
        proceso.start()
        print(f"[Padre] Worker {i + 1} iniciado")
    
    print(f"\n[Padre] Recolectando resultados de la Queue...")
    
    # Recolectar resultados de la Queue
    # get() bloquea hasta que haya un elemento disponible
    resultados = []
    for i in range(n_procesos):
        resultado = q.get()  # Bloquea hasta obtener resultado
        resultados.append(resultado)
        print(f"[Padre] Recibido resultado del Worker {resultado['worker_id']}: {resultado['resultado']:,}")
    
    print(f"\n[Padre] Esperando a que terminen todos los workers...")
    
    # Esperar a que todos los procesos terminen
    for i, proceso in enumerate(procesos):
        proceso.join()
        print(f"[Padre] Worker {i + 1} terminado")
    
    fin_total = time.perf_counter()
    tiempo_total = fin_total - inicio_total
    
    # Verificar que todos los resultados sean idénticos
    print(f"\n=== ANÁLISIS DE RESULTADOS ===")
    
    valores = [r['resultado'] for r in resultados]
    
    # Crear set para verificar unicidad
    valores_unicos = set(valores)
    
    print(f"Resultados obtenidos: {len(resultados)}")
    print(f"Valores únicos: {len(valores_unicos)}")
    
    if len(valores_unicos) == 1:
        resultado_correcto = valores[0]
        resultado_esperado = (k * (k - 1)) // 2
        
        print(f"✅ Todos los resultados son idénticos: {resultado_correcto:,}")
        
        if resultado_correcto == resultado_esperado:
            print(f"✅ El resultado es correcto (fórmula: k*(k-1)/2)")
        else:
            print(f"❌ Error: esperado {resultado_esperado:,}, obtenido {resultado_correcto:,}")
    else:
        print(f"❌ Error: Los resultados no son idénticos")
        for i, resultado in enumerate(resultados):
            print(f"   Worker {resultado['worker_id']}: {resultado['resultado']:,}")
    
    # Mostrar estadísticas de rendimiento
    print(f"\n=== ESTADÍSTICAS DE RENDIMIENTO ===")
    tiempos = [r['tiempo'] for r in resultados]
    print(f"Tiempo total: {tiempo_total:.3f} segundos")
    print(f"Tiempo promedio por worker: {sum(tiempos) / len(tiempos):.3f} segundos")
    print(f"Tiempo más rápido: {min(tiempos):.3f} segundos")
    print(f"Tiempo más lento: {max(tiempos):.3f} segundos")
    
    print(f"\n=== VERIFICACIÓN FINAL ===")
    # Verificación con assert como en el ejemplo original
    assert len(valores_unicos) == 1, "Los resultados no son idénticos"
    print(f'✅ Verificación con assert: Todos iguales: {valores[0]:,}')

if __name__ == '__main__':
    main()