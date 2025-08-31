#!/usr/bin/env python3

# Ejercicio 8 · Nivel Avanzado
#
# Enunciado: Crea un programa que lance N = 8 procesos calculando números primos en rangos 
# disjuntos. Sincroniza el acceso a un archivo común primos.txt usando Lock para añadir 
# los resultados sin colisiones. Mide el speed-up frente a la versión secuencial.

from multiprocessing import Process, Lock, current_process
import time
import os

def es_primo(n):
    """
    Función para verificar si un número es primo.
    
    Implementación simple pero efectiva para números no muy grandes.
    Para números muy grandes se usarían algoritmos más sofisticados.
    
    Args:
        n: Número a verificar
    
    Returns:
        bool: True si es primo, False si no lo es
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    # Solo verificar divisores impares hasta sqrt(n)
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

def encontrar_primos_rango(inicio, fin):
    """
    Encuentra todos los números primos en un rango dado.
    
    Args:
        inicio: Número inicial del rango (inclusivo)
        fin: Número final del rango (exclusivo)
    
    Returns:
        list: Lista de números primos en el rango
    """
    primos = []
    for num in range(inicio, fin):
        if es_primo(num):
            primos.append(num)
    return primos

def worker_primos(inicio, fin, lock, archivo_salida, worker_id):
    """
    Proceso worker que encuentra primos en un rango y los escribe al archivo.
    
    Usa Lock para sincronizar el acceso al archivo compartido.
    Sin Lock, múltiples procesos escribiendo simultáneamente causarían:
    - Corrupción de datos
    - Pérdida de información
    - Escrituras intercaladas
    
    Args:
        inicio: Inicio del rango (inclusivo)
        fin: Fin del rango (exclusivo)
        lock: Lock para sincronizar acceso al archivo
        archivo_salida: Nombre del archivo donde escribir
        worker_id: ID del worker
    """
    pid = current_process().pid
    print(f"[Worker {worker_id}] Iniciado - PID: {pid}")
    print(f"[Worker {worker_id}] Buscando primos en rango [{inicio}, {fin})")
    
    inicio_tiempo = time.perf_counter()
    
    # Encontrar primos en el rango asignado
    primos = encontrar_primos_rango(inicio, fin)
    
    fin_tiempo = time.perf_counter()
    duracion = fin_tiempo - inicio_tiempo
    
    print(f"[Worker {worker_id}] Encontrados {len(primos)} primos en {duracion:.2f}s")
    
    # SECCIÓN CRÍTICA: Escribir al archivo con Lock
    with lock:
        print(f"[Worker {worker_id}] Escribiendo {len(primos)} primos al archivo...")
        
        with open(archivo_salida, 'a', encoding='utf-8') as f:
            # Escribir encabezado del worker
            f.write(f"# Worker {worker_id} (PID {pid}) - Rango [{inicio}, {fin}) - {len(primos)} primos - {duracion:.3f}s\n")
            
            # Escribir primos (10 por línea para legibilidad)
            for i, primo in enumerate(primos):
                f.write(str(primo))
                if (i + 1) % 10 == 0:
                    f.write('\n')
                else:
                    f.write(', ')
            
            if primos:
                f.write('\n\n')  # Línea en blanco después de cada worker
        
        print(f"[Worker {worker_id}] Escritura completada")
    
    return len(primos), duracion

def calcular_primos_paralelo(rango_total, num_workers, archivo_salida):
    """
    Calcula primos usando múltiples procesos con archivo compartido sincronizado.
    
    Args:
        rango_total: Tupla (inicio, fin) del rango total
        num_workers: Número de procesos workers
        archivo_salida: Archivo donde escribir los resultados
    
    Returns:
        tuple: (total_primos, tiempo_total)
    """
    print(f"=== CÁLCULO PARALELO ===")
    print(f"Rango total: [{rango_total[0]}, {rango_total[1]})")
    print(f"Workers: {num_workers}")
    print(f"Archivo: {archivo_salida}")
    
    inicio_total, fin_total = rango_total
    tamano_total = fin_total - inicio_total
    tamano_por_worker = tamano_total // num_workers
    
    # Limpiar archivo de salida
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        f.write(f"# Números primos encontrados - {num_workers} procesos paralelos\n")
        f.write(f"# Rango total: [{inicio_total}, {fin_total})\n")
        f.write(f"# Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    # Crear Lock para sincronización de archivo
    lock = Lock()
    
    # Dividir rango entre workers
    rangos = []
    for i in range(num_workers):
        inicio_worker = inicio_total + i * tamano_por_worker
        if i == num_workers - 1:
            # Último worker toma cualquier resto
            fin_worker = fin_total
        else:
            fin_worker = inicio_total + (i + 1) * tamano_por_worker
        
        rangos.append((inicio_worker, fin_worker))
        print(f"Worker {i + 1}: rango [{inicio_worker}, {fin_worker}) = {fin_worker - inicio_worker} números")
    
    print(f"\nIniciando {num_workers} procesos...")
    inicio_tiempo = time.perf_counter()
    
    # Crear y lanzar workers
    procesos = []
    for i, (inicio_w, fin_w) in enumerate(rangos):
        proceso = Process(
            target=worker_primos,
            args=(inicio_w, fin_w, lock, archivo_salida, i + 1)
        )
        procesos.append(proceso)
        proceso.start()
    
    # Esperar que todos terminen
    for i, proceso in enumerate(procesos):
        proceso.join()
        print(f"Worker {i + 1} terminado")
    
    fin_tiempo = time.perf_counter()
    tiempo_total = fin_tiempo - inicio_tiempo
    
    # Contar primos totales del archivo
    total_primos = contar_primos_archivo(archivo_salida)
    
    print(f"\nResultados paralelos:")
    print(f"  Tiempo total: {tiempo_total:.3f} segundos")
    print(f"  Primos encontrados: {total_primos:,}")
    print(f"  Archivo generado: {archivo_salida}")
    
    return total_primos, tiempo_total

def calcular_primos_secuencial(rango_total):
    """
    Calcula primos secuencialmente (para comparar speed-up).
    
    Args:
        rango_total: Tupla (inicio, fin) del rango total
    
    Returns:
        tuple: (total_primos, tiempo_total)
    """
    print(f"=== CÁLCULO SECUENCIAL ===")
    print(f"Rango: [{rango_total[0]}, {rango_total[1]})")
    
    inicio_tiempo = time.perf_counter()
    primos = encontrar_primos_rango(rango_total[0], rango_total[1])
    fin_tiempo = time.perf_counter()
    
    tiempo_total = fin_tiempo - inicio_tiempo
    
    print(f"Resultados secuenciales:")
    print(f"  Tiempo total: {tiempo_total:.3f} segundos")
    print(f"  Primos encontrados: {len(primos):,}")
    
    return len(primos), tiempo_total

def contar_primos_archivo(archivo):
    """
    Cuenta el número total de primos en el archivo generado.
    
    Args:
        archivo: Ruta al archivo de primos
    
    Returns:
        int: Número total de primos
    """
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Contar números (excluir líneas de comentario)
        lineas = contenido.split('\n')
        total = 0
        
        for linea in lineas:
            if not linea.startswith('#') and linea.strip():
                # Contar comas + último número si no termina en coma
                numeros_en_linea = linea.count(',')
                if linea.strip() and not linea.strip().endswith(','):
                    numeros_en_linea += 1
                total += numeros_en_linea
        
        return total
    except Exception as e:
        print(f"Error contando primos: {e}")
        return 0

def main():
    """
    Función principal que ejecuta ambas versiones y compara resultados.
    """
    print("=== Ejercicio 8: Cálculo paralelo de números primos ===")
    
    # Configuración
    rango = (1000, 20000)   # Rango para buscar primos
    num_workers = 8
    archivo_salida = "primos.txt"
    
    print(f"Configuración:")
    print(f"  Rango: [{rango[0]}, {rango[1]}) = {rango[1] - rango[0]:,} números")
    print(f"  Workers paralelos: {num_workers}")
    print(f"  Archivo de salida: {archivo_salida}")
    
    # Eliminar archivo anterior si existe
    if os.path.exists(archivo_salida):
        os.remove(archivo_salida)
        print(f"  Archivo anterior eliminado")
    
    # Ejecutar versión secuencial
    print(f"\n{'='*60}")
    total_sec, tiempo_sec = calcular_primos_secuencial(rango)
    
    # Ejecutar versión paralela
    print(f"\n{'='*60}")
    total_par, tiempo_par = calcular_primos_paralelo(rango, num_workers, archivo_salida)
    
    # Análisis comparativo
    print(f"\n{'='*60}")
    print("📊 ANÁLISIS COMPARATIVO")
    print("="*60)
    
    print(f"Resultados:")
    print(f"  Secuencial: {total_sec:,} primos en {tiempo_sec:.3f}s")
    print(f"  Paralelo:   {total_par:,} primos en {tiempo_par:.3f}s")
    
    # Verificar consistencia
    if total_sec == total_par:
        print(f"  ✅ Resultados consistentes")
    else:
        print(f"  ❌ Inconsistencia: {abs(total_sec - total_par)} primos de diferencia")
    
    # Speed-up
    if tiempo_sec > 0:
        speedup = tiempo_sec / tiempo_par
        eficiencia = speedup / num_workers
        
        print(f"\nRendimiento:")
        print(f"  Speed-up: {speedup:.2f}x")
        print(f"  Eficiencia: {eficiencia:.2f} ({eficiencia * 100:.1f}%)")
        
        if speedup > 1:
            print(f"  ✅ Aceleración del {((speedup - 1) * 100):.1f}%")
        else:
            print(f"  ❌ No hay aceleración (overhead de paralelización)")
    
    # Mostrar primeros primos del archivo
    print(f"\n📄 Contenido del archivo {archivo_salida}:")
    try:
        with open(archivo_salida, 'r', encoding='utf-8') as f:
            lineas = f.readlines()[:15]  # Primeras 15 líneas
            for linea in lineas:
                print(f"  {linea.rstrip()}")
        
        if len(lineas) == 15:
            print("  ... (archivo continúa)")
            
        # Tamaño del archivo
        tamano = os.path.getsize(archivo_salida)
        print(f"\nTamaño del archivo: {tamano:,} bytes ({tamano/1024:.1f} KB)")
        
    except Exception as e:
        print(f"Error leyendo archivo: {e}")
    
    print(f"\n💡 CONCEPTOS DEMOSTRADOS:")
    print(f"1. Paralelización de tareas CPU-intensivas")
    print(f"2. Sincronización de acceso a archivo con Lock")
    print(f"3. División de trabajo en rangos disjuntos")
    print(f"4. Medición de speed-up y eficiencia")
    print(f"5. Manejo de archivos compartidos entre procesos")

if __name__ == '__main__':
    main()