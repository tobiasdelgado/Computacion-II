#!/usr/bin/env python3

# Ejercicio 3 · Nivel Intermedio +
#
# Objetivo: demostrar una condición de carrera y su corrección con Lock.
#
# Enunciado: crea un contador global al que dos procesos suman 1, cincuenta mil veces cada uno. 
# Realiza primero la versión sin Lock (para evidenciar valores erróneos) y luego protégela 
# con un Lock, mostrando el resultado correcto (100,000).

from multiprocessing import Process, Value, Lock, current_process
import time

def incrementar_sin_lock(contador, n_incrementos, worker_id):
    """
    Función que incrementa un contador compartido SIN protección de Lock.
    
    Esto genera una condición de carrera (race condition):
    - Ambos procesos leen el valor actual del contador
    - Ambos incrementan su copia local
    - Ambos escriben de vuelta, perdiendo incrementos
    
    Args:
        contador: Value compartido entre procesos
        n_incrementos: Número de veces a incrementar
        worker_id: ID del worker para identificación
    """
    print(f"[Worker {worker_id} SIN LOCK] Iniciado - PID: {current_process().pid}")
    
    for i in range(n_incrementos):
        # CONDICIÓN DE CARRERA: lectura y escritura no atómica
        # Proceso 1: lee valor = 100
        # Proceso 2: lee valor = 100 (al mismo tiempo)
        # Proceso 1: escribe 101
        # Proceso 2: escribe 101 (perdió el incremento del proceso 1)
        contador.value += 1
        
        # Mostrar progreso cada 10,000 incrementos
        if (i + 1) % 10000 == 0:
            print(f"[Worker {worker_id} SIN LOCK] Progreso: {i + 1:,}/{n_incrementos:,}")
    
    print(f"[Worker {worker_id} SIN LOCK] Terminado")

def incrementar_con_lock(contador, n_incrementos, lock, worker_id):
    """
    Función que incrementa un contador compartido CON protección de Lock.
    
    El Lock garantiza exclusión mutua:
    - Solo un proceso puede acceder al contador a la vez
    - Operación atómica: leer, incrementar, escribir
    - No hay pérdida de incrementos
    
    Args:
        contador: Value compartido entre procesos
        n_incrementos: Número de veces a incrementar
        lock: Lock para sincronización
        worker_id: ID del worker para identificación
    """
    print(f"[Worker {worker_id} CON LOCK] Iniciado - PID: {current_process().pid}")
    
    for i in range(n_incrementos):
        # SECCIÓN CRÍTICA protegida por Lock
        with lock:
            # Solo un proceso puede ejecutar esta línea a la vez
            contador.value += 1
        
        # Mostrar progreso cada 10,000 incrementos
        if (i + 1) % 10000 == 0:
            print(f"[Worker {worker_id} CON LOCK] Progreso: {i + 1:,}/{n_incrementos:,}")
    
    print(f"[Worker {worker_id} CON LOCK] Terminado")

def test_sin_lock(n_incrementos):
    """
    Prueba sin Lock - demuestra condición de carrera.
    """
    print("\n" + "="*60)
    print("🔴 PRUEBA SIN LOCK - Condición de carrera")
    print("="*60)
    
    # Value('i', 0) crea un entero compartido inicializado en 0
    # 'i' indica tipo int, otros tipos: 'd' (double), 'f' (float), etc.
    contador = Value('i', 0)
    
    print(f"Valor inicial del contador: {contador.value}")
    print(f"Cada worker incrementará {n_incrementos:,} veces")
    print(f"Resultado esperado: {2 * n_incrementos:,}")
    
    inicio = time.perf_counter()
    
    # Crear dos procesos que incrementan sin sincronización
    p1 = Process(target=incrementar_sin_lock, args=(contador, n_incrementos, 1))
    p2 = Process(target=incrementar_sin_lock, args=(contador, n_incrementos, 2))
    
    # Iniciar procesos
    p1.start()
    p2.start()
    
    # Esperar que terminen
    p1.join()
    p2.join()
    
    fin = time.perf_counter()
    tiempo = fin - inicio
    
    print(f"\n📊 RESULTADOS SIN LOCK:")
    print(f"Valor final del contador: {contador.value:,}")
    print(f"Valor esperado: {2 * n_incrementos:,}")
    print(f"Incrementos perdidos: {2 * n_incrementos - contador.value:,}")
    print(f"Tiempo total: {tiempo:.3f} segundos")
    
    if contador.value == 2 * n_incrementos:
        print("✅ Resultado correcto (muy poco probable sin lock)")
    else:
        print("❌ Resultado incorrecto - condición de carrera detectada")
    
    return contador.value

def test_con_lock(n_incrementos):
    """
    Prueba con Lock - evita condición de carrera.
    """
    print("\n" + "="*60)
    print("🟢 PRUEBA CON LOCK - Sin condición de carrera")
    print("="*60)
    
    contador = Value('i', 0)
    # Lock() crea un mutex (mutual exclusion) para sincronización
    lock = Lock()
    
    print(f"Valor inicial del contador: {contador.value}")
    print(f"Cada worker incrementará {n_incrementos:,} veces")
    print(f"Resultado esperado: {2 * n_incrementos:,}")
    
    inicio = time.perf_counter()
    
    # Crear dos procesos que incrementan CON sincronización
    p1 = Process(target=incrementar_con_lock, args=(contador, n_incrementos, lock, 1))
    p2 = Process(target=incrementar_con_lock, args=(contador, n_incrementos, lock, 2))
    
    # Iniciar procesos
    p1.start()
    p2.start()
    
    # Esperar que terminen
    p1.join()
    p2.join()
    
    fin = time.perf_counter()
    tiempo = fin - inicio
    
    print(f"\n📊 RESULTADOS CON LOCK:")
    print(f"Valor final del contador: {contador.value:,}")
    print(f"Valor esperado: {2 * n_incrementos:,}")
    print(f"Incrementos perdidos: {2 * n_incrementos - contador.value:,}")
    print(f"Tiempo total: {tiempo:.3f} segundos")
    
    if contador.value == 2 * n_incrementos:
        print("✅ Resultado correcto - Lock funcionó")
    else:
        print("❌ Resultado incorrecto - algo salió mal")
    
    return contador.value

def main():
    """
    Función principal que ejecuta ambas pruebas y compara resultados.
    """
    print("=== Ejercicio 3: Condición de carrera y corrección con Lock ===")
    
    # Configuración
    N = 50_000  # Número de incrementos por proceso
    
    print(f"Configuración:")
    print(f"- Incrementos por proceso: {N:,}")
    print(f"- Total de procesos: 2")
    print(f"- Total incrementos esperados: {2 * N:,}")
    
    # Ejecutar prueba sin Lock
    resultado_sin_lock = test_sin_lock(N)
    
    # Ejecutar prueba con Lock
    resultado_con_lock = test_con_lock(N)
    
    # Comparación final
    print("\n" + "="*60)
    print("📊 COMPARACIÓN FINAL")
    print("="*60)
    
    esperado = 2 * N
    
    print(f"Resultado esperado:    {esperado:,}")
    print(f"Sin Lock:             {resultado_sin_lock:,} ({'✅ Correcto' if resultado_sin_lock == esperado else '❌ Incorrecto'})")
    print(f"Con Lock:             {resultado_con_lock:,} ({'✅ Correcto' if resultado_con_lock == esperado else '❌ Incorrecto'})")
    
    perdidos_sin_lock = esperado - resultado_sin_lock
    perdidos_con_lock = esperado - resultado_con_lock
    
    print(f"\nIncrementos perdidos:")
    print(f"Sin Lock: {perdidos_sin_lock:,} ({(perdidos_sin_lock/esperado)*100:.2f}%)")
    print(f"Con Lock: {perdidos_con_lock:,} ({(perdidos_con_lock/esperado)*100:.2f}%)")
    
    print(f"\n🎯 CONCLUSIÓN:")
    if perdidos_sin_lock > 0:
        print("- Sin Lock: Se perdieron incrementos debido a condición de carrera")
    if perdidos_con_lock == 0:
        print("- Con Lock: No se perdieron incrementos, sincronización exitosa")
    
    print("\n💡 LECCIÓN APRENDIDA:")
    print("Los Locks son esenciales para proteger recursos compartidos en concurrencia")

if __name__ == '__main__':
    main()