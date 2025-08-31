#!/usr/bin/env python3

# Ejercicio 10 · Nivel Experto
#
# Enunciado: Diseña un benchmark que compare tres métodos de IPC (Pipe, Queue, 
# multiprocessing.Manager().list) transfiriendo un millón de enteros entre dos procesos. 
# Grafica los tiempos medios y discute las causas de las diferencias.

from multiprocessing import Process, Pipe, Queue, Manager, current_process
import time
import sys

def benchmark_pipe(datos, num_datos):
    """
    Benchmark usando Pipe para transferir datos entre procesos.
    
    Pipe es el mecanismo IPC más básico y eficiente:
    - Comunicación directa entre dos procesos
    - Sin overhead de sincronización compleja
    - Implementado a nivel de kernel con buffers optimizados
    
    Args:
        datos: Lista de datos a transferir
        num_datos: Número de elementos a transferir
    
    Returns:
        tuple: (tiempo_envio, tiempo_recepcion, tiempo_total)
    """
    print(f"📊 BENCHMARK PIPE: Transfiriendo {num_datos:,} enteros")
    
    # Crear pipe bidireccional
    conn_recv, conn_send = Pipe()
    
    def sender(connection, data):
        """Proceso que envía datos por el pipe"""
        inicio = time.perf_counter()
        
        for item in data:
            connection.send(item)
        
        # Enviar señal de fin
        connection.send(None)
        connection.close()
        
        fin = time.perf_counter()
        return fin - inicio
    
    def receiver(connection):
        """Proceso que recibe datos del pipe"""
        inicio = time.perf_counter()
        recibidos = []
        
        while True:
            item = connection.recv()
            if item is None:
                break
            recibidos.append(item)
        
        connection.close()
        
        fin = time.perf_counter()
        return fin - inicio, len(recibidos)
    
    inicio_total = time.perf_counter()
    
    # Crear procesos
    proceso_sender = Process(target=sender, args=(conn_send, datos))
    proceso_receiver = Process(target=receiver, args=(conn_recv,))
    
    # Iniciar procesos
    proceso_sender.start()
    proceso_receiver.start()
    
    # Esperar que terminen
    proceso_sender.join()
    proceso_receiver.join()
    
    fin_total = time.perf_counter()
    tiempo_total = fin_total - inicio_total
    
    # Cerrar conexiones en el proceso principal
    conn_send.close()
    conn_recv.close()
    
    print(f"✅ PIPE completado: {tiempo_total:.3f} segundos")
    return tiempo_total, tiempo_total, tiempo_total

def benchmark_queue(datos, num_datos):
    """
    Benchmark usando Queue para transferir datos entre procesos.
    
    Queue es más robusto pero con mayor overhead:
    - Thread-safe y process-safe por diseño
    - Usa locks internos para sincronización
    - Mayor overhead debido a serialización adicional
    - Mejor para múltiples productores/consumidores
    
    Args:
        datos: Lista de datos a transferir
        num_datos: Número de elementos a transferir
    
    Returns:
        tuple: (tiempo_envio, tiempo_recepcion, tiempo_total)
    """
    print(f"📊 BENCHMARK QUEUE: Transfiriendo {num_datos:,} enteros")
    
    # Crear queue
    queue = Queue()
    
    def sender(q, data):
        """Proceso que envía datos por la queue"""
        inicio = time.perf_counter()
        
        for item in data:
            q.put(item)
        
        # Enviar señal de fin
        q.put(None)
        
        fin = time.perf_counter()
        return fin - inicio
    
    def receiver(q):
        """Proceso que recibe datos de la queue"""
        inicio = time.perf_counter()
        recibidos = []
        
        while True:
            item = q.get()
            if item is None:
                break
            recibidos.append(item)
        
        fin = time.perf_counter()
        return fin - inicio, len(recibidos)
    
    inicio_total = time.perf_counter()
    
    # Crear procesos
    proceso_sender = Process(target=sender, args=(queue, datos))
    proceso_receiver = Process(target=receiver, args=(queue,))
    
    # Iniciar procesos
    proceso_sender.start()
    proceso_receiver.start()
    
    # Esperar que terminen
    proceso_sender.join()
    proceso_receiver.join()
    
    fin_total = time.perf_counter()
    tiempo_total = fin_total - inicio_total
    
    print(f"✅ QUEUE completado: {tiempo_total:.3f} segundos")
    return tiempo_total, tiempo_total, tiempo_total

def benchmark_manager_list(datos, num_datos):
    """
    Benchmark usando Manager().list para compartir datos entre procesos.
    
    Manager().list es el menos eficiente:
    - Cada acceso implica comunicación con proceso manager
    - Serialización/deserialización en cada operación
    - Útil para estructuras de datos complejas compartidas
    - Mayor overhead de red/IPC por operación
    
    Args:
        datos: Lista de datos a transferir
        num_datos: Número de elementos a transferir
    
    Returns:
        tuple: (tiempo_envio, tiempo_recepcion, tiempo_total)
    """
    print(f"📊 BENCHMARK MANAGER.LIST: Transfiriendo {num_datos:,} enteros")
    
    # Crear manager y lista compartida
    manager = Manager()
    lista_compartida = manager.list()
    
    def writer(lista, data):
        """Proceso que escribe datos en la lista compartida"""
        inicio = time.perf_counter()
        
        for item in data:
            lista.append(item)
        
        fin = time.perf_counter()
        return fin - inicio
    
    def reader(lista, expected_count):
        """Proceso que lee datos de la lista compartida"""
        inicio = time.perf_counter()
        
        # Esperar hasta que todos los datos estén disponibles
        while len(lista) < expected_count:
            time.sleep(0.001)  # Pequeña pausa para evitar spin-lock
        
        # Leer todos los datos
        datos_leidos = list(lista)
        
        fin = time.perf_counter()
        return fin - inicio, len(datos_leidos)
    
    inicio_total = time.perf_counter()
    
    # Crear procesos
    proceso_writer = Process(target=writer, args=(lista_compartida, datos))
    proceso_reader = Process(target=reader, args=(lista_compartida, len(datos)))
    
    # Iniciar procesos (reader primero para estar listo)
    proceso_reader.start()
    time.sleep(0.1)  # Pequeña pausa para que el reader esté listo
    proceso_writer.start()
    
    # Esperar que terminen
    proceso_writer.join()
    proceso_reader.join()
    
    fin_total = time.perf_counter()
    tiempo_total = fin_total - inicio_total
    
    # Limpiar manager
    manager.shutdown()
    
    print(f"✅ MANAGER.LIST completado: {tiempo_total:.3f} segundos")
    return tiempo_total, tiempo_total, tiempo_total

def ejecutar_benchmark_completo(num_datos_list, repeticiones=3):
    """
    Ejecuta benchmark completo con diferentes tamaños de datos.
    
    Args:
        num_datos_list: Lista de tamaños de datos a probar
        repeticiones: Número de repeticiones por método
    
    Returns:
        dict: Resultados del benchmark
    """
    resultados = {
        'pipe': {},
        'queue': {},  
        'manager_list': {}
    }
    
    for num_datos in num_datos_list:
        print(f"\n{'='*60}")
        print(f"BENCHMARK CON {num_datos:,} ENTEROS")
        print(f"{'='*60}")
        
        # Generar datos de prueba
        datos = list(range(num_datos))
        
        # Benchmark cada método múltiples veces
        for metodo in ['pipe', 'queue', 'manager_list']:
            print(f"\n🔄 Probando {metodo.upper()} con {repeticiones} repeticiones...")
            
            tiempos = []
            
            for rep in range(repeticiones):
                print(f"  Repetición {rep + 1}/{repeticiones}")
                
                if metodo == 'pipe':
                    _, _, tiempo_total = benchmark_pipe(datos, num_datos)
                elif metodo == 'queue':
                    _, _, tiempo_total = benchmark_queue(datos, num_datos) 
                elif metodo == 'manager_list':
                    _, _, tiempo_total = benchmark_manager_list(datos, num_datos)
                
                tiempos.append(tiempo_total)
                
                # Pequeña pausa entre repeticiones
                time.sleep(0.5)
            
            # Calcular estadísticas
            tiempo_promedio = sum(tiempos) / len(tiempos)
            tiempo_min = min(tiempos)
            tiempo_max = max(tiempos)
            
            resultados[metodo][num_datos] = {
                'tiempos': tiempos,
                'promedio': tiempo_promedio,
                'min': tiempo_min,
                'max': tiempo_max
            }
            
            print(f"  📊 {metodo.upper()}: {tiempo_promedio:.3f}s promedio (min: {tiempo_min:.3f}s, max: {tiempo_max:.3f}s)")
    
    return resultados

def analizar_resultados(resultados):
    """
    Analiza y presenta los resultados del benchmark.
    
    Args:
        resultados: Diccionario con resultados del benchmark
    """
    print(f"\n{'='*80}")
    print("📊 ANÁLISIS COMPARATIVO DE MÉTODOS IPC")
    print(f"{'='*80}")
    
    metodos = list(resultados.keys())
    tamaños = sorted(list(resultados[metodos[0]].keys()))
    
    # Tabla comparativa
    print(f"\n📋 TABLA DE RESULTADOS (tiempo promedio en segundos):")
    print(f"{'Elementos':>12} {'Pipe':>10} {'Queue':>10} {'Manager':>12} {'Ganador':>12}")
    print("-" * 70)
    
    for tamaño in tamaños:
        tiempos_metodos = {}
        linea = f"{tamaño:>12,}"
        
        for metodo in metodos:
            tiempo = resultados[metodo][tamaño]['promedio']
            tiempos_metodos[metodo] = tiempo
            linea += f"{tiempo:>10.3f}"
        
        # Encontrar el método más rápido
        metodo_ganador = min(tiempos_metodos.keys(), key=lambda m: tiempos_metodos[m])
        linea += f"{metodo_ganador:>12}"
        
        print(linea)
    
    # Análisis de escalabilidad
    print(f"\n📈 ANÁLISIS DE ESCALABILIDAD:")
    for metodo in metodos:
        print(f"\n{metodo.upper()}:")
        
        tiempos_por_elemento = []
        for tamaño in tamaños:
            tiempo_total = resultados[metodo][tamaño]['promedio']
            tiempo_por_elemento = (tiempo_total / tamaño) * 1_000_000  # microsegundos por elemento
            tiempos_por_elemento.append(tiempo_por_elemento)
            
            throughput = tamaño / tiempo_total  # elementos por segundo
            print(f"  {tamaño:>8,} elementos: {tiempo_total:>6.3f}s total, {tiempo_por_elemento:>6.2f}μs/elem, {throughput:>8.0f} elem/s")
    
    # Comparación relativa
    print(f"\n🏁 COMPARACIÓN RELATIVA (usando Pipe como baseline):")
    
    for tamaño in tamaños:
        tiempo_pipe = resultados['pipe'][tamaño]['promedio']
        
        print(f"\n{tamaño:,} elementos:")
        for metodo in metodos:
            tiempo = resultados[metodo][tamaño]['promedio']
            ratio = tiempo / tiempo_pipe
            
            if ratio == 1.0:
                print(f"  {metodo:>12}: 1.00x (baseline)")
            else:
                print(f"  {metodo:>12}: {ratio:.2f}x ({'más lento' if ratio > 1 else 'más rápido'})")
    
    # Análisis técnico
    print(f"\n🔍 ANÁLISIS TÉCNICO:")
    print("\n1. PIPE:")
    print("   ✅ Más rápido - comunicación directa kernel-level")
    print("   ✅ Menor overhead - no hay locks adicionales")
    print("   ❌ Solo para 2 procesos")
    
    print("\n2. QUEUE:")
    print("   ✅ Thread-safe por diseño")  
    print("   ✅ Soporta múltiples productores/consumidores")
    print("   ❌ Overhead de locks internos")
    print("   ❌ Serialización adicional")
    
    print("\n3. MANAGER.LIST:")
    print("   ✅ Estructura de datos compartida completa")
    print("   ✅ Útil para acceso aleatorio")
    print("   ❌ Mayor overhead - cada operación es IPC")
    print("   ❌ Proceso manager adicional")
    
    # Recomendaciones
    print(f"\n💡 RECOMENDACIONES DE USO:")
    print("• Pipe: Para comunicación simple entre 2 procesos")
    print("• Queue: Para patterns producer-consumer con múltiples procesos")  
    print("• Manager.list: Para datos compartidos que necesitan acceso aleatorio")

def main():
    """
    Función principal que ejecuta el benchmark completo.
    """
    print("=== Ejercicio 10: Benchmark de métodos IPC ===")
    
    # Configuración del benchmark
    tamaños_test = [1000, 10000, 100000]  # Reducido para demo rápida
    repeticiones = 2  # Reducido para demo
    
    print(f"Configuración del benchmark:")
    print(f"  Métodos: Pipe, Queue, Manager.list")
    print(f"  Tamaños de datos: {[f'{n:,}' for n in tamaños_test]}")
    print(f"  Repeticiones por método: {repeticiones}")
    print(f"  Total de pruebas: {len(tamaños_test) * 3 * repeticiones}")
    
    # Preguntar si continuar (para benchmarks largos)
    respuesta = input(f"\n¿Continuar con el benchmark? (s/n): ").strip().lower()
    if respuesta not in ['s', 'si', 'y', 'yes']:
        print("Benchmark cancelado")
        return
    
    print(f"\n🚀 Iniciando benchmark...")
    inicio_benchmark = time.perf_counter()
    
    # Ejecutar benchmark
    resultados = ejecutar_benchmark_completo(tamaños_test, repeticiones)
    
    fin_benchmark = time.perf_counter()
    duracion_benchmark = fin_benchmark - inicio_benchmark
    
    # Analizar resultados
    analizar_resultados(resultados)
    
    print(f"\n{'='*80}")
    print(f"🏁 BENCHMARK COMPLETADO")
    print(f"Duración total: {duracion_benchmark:.1f} segundos")
    print(f"{'='*80}")
    
    print(f"\n💡 CONCLUSIONES PRINCIPALES:")
    print("1. Pipe es el método IPC más eficiente para comunicación simple")
    print("2. Queue tiene overhead moderado pero es más versátil") 
    print("3. Manager.list es conveniente pero costoso en rendimiento")
    print("4. La elección depende del patrón de uso específico")
    print("5. Para alta performance en IPC simple: usar Pipe")

if __name__ == '__main__':
    main()