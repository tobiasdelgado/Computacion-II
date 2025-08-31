#!/usr/bin/env python3

# Ejercicio 9 · Nivel Avanzado +
#
# Enunciado: Construye una simulación de banco: múltiples cajeros (procesos) atienden clientes 
# retirando y depositando sobre un mismo balance compartido (Value). Implementa una política 
# de back-off exponencial para reintentos cuando el Lock esté ocupado y registra métricas 
# de contención.

from multiprocessing import Process, Value, Lock, current_process, Queue
import time
import random

class MetricasContention:
    """
    Clase para almacenar métricas de contención del Lock.
    """
    def __init__(self):
        self.intentos_lock = 0
        self.tiempo_esperando = 0.0
        self.reintentos = 0
        self.backoff_aplicado = 0

def cajero_banco(balance, lock, metricas_queue, cajero_id, num_transacciones, clientes_por_cajero):
    """
    Proceso cajero que maneja transacciones bancarias con back-off exponencial.
    
    Back-off exponencial: Si no puede obtener el lock inmediatamente,
    espera tiempo creciente: 0.001s, 0.002s, 0.004s, 0.008s, etc.
    Esto reduce contención cuando hay muchos procesos compitiendo.
    
    Args:
        balance: Value compartido con el balance del banco
        lock: Lock para proteger acceso al balance
        metricas_queue: Queue para enviar métricas de contención
        cajero_id: ID del cajero
        num_transacciones: Número de transacciones a procesar
        clientes_por_cajero: Clientes promedio por cajero
    """
    pid = current_process().pid
    print(f"[Cajero {cajero_id}] Iniciado - PID: {pid}")
    
    # Métricas locales del cajero
    metricas = MetricasContention()
    transacciones_exitosas = 0
    transacciones_rechazadas = 0
    tiempo_total_cajero = time.perf_counter()
    
    for i in range(num_transacciones):
        # Generar transacción aleatoria
        tipo = random.choice(['deposito', 'retiro'])
        monto = random.randint(10, 500)
        cliente_id = random.randint(1, clientes_por_cajero * 3)  # Algunos clientes van a múltiples cajeros
        
        print(f"[Cajero {cajero_id}] Transacción {i+1}: {tipo} ${monto} (Cliente {cliente_id})")
        
        # Intentar obtener lock con back-off exponencial
        exito_transaccion = procesar_transaccion_con_backoff(
            balance, lock, tipo, monto, cajero_id, metricas
        )
        
        if exito_transaccion:
            transacciones_exitosas += 1
            print(f"[Cajero {cajero_id}] ✅ {tipo} ${monto} exitoso")
        else:
            transacciones_rechazadas += 1
            print(f"[Cajero {cajero_id}] ❌ {tipo} ${monto} rechazado (fondos insuficientes)")
        
        # Simular tiempo entre transacciones
        time.sleep(random.uniform(0.1, 0.3))
    
    tiempo_total_cajero = time.perf_counter() - tiempo_total_cajero
    
    # Enviar métricas finales
    resultado = {
        'cajero_id': cajero_id,
        'pid': pid,
        'transacciones_exitosas': transacciones_exitosas,
        'transacciones_rechazadas': transacciones_rechazadas,
        'tiempo_total': tiempo_total_cajero,
        'intentos_lock': metricas.intentos_lock,
        'tiempo_esperando': metricas.tiempo_esperando,
        'reintentos': metricas.reintentos,
        'backoff_aplicado': metricas.backoff_aplicado
    }
    
    metricas_queue.put(resultado)
    print(f"[Cajero {cajero_id}] Terminado - {transacciones_exitosas} exitosas, {transacciones_rechazadas} rechazadas")

def procesar_transaccion_con_backoff(balance, lock, tipo, monto, cajero_id, metricas):
    """
    Procesa una transacción usando back-off exponencial para manejar contención.
    
    Back-off exponencial ayuda a reducir "thundering herd" - situación donde
    muchos procesos intentan obtener el mismo recurso simultáneamente.
    
    Args:
        balance: Value compartido
        lock: Lock para sincronización  
        tipo: 'deposito' o 'retiro'
        monto: Cantidad de dinero
        cajero_id: ID del cajero
        metricas: Objeto para registrar métricas
    
    Returns:
        bool: True si la transacción fue exitosa
    """
    max_intentos = 5
    delay_base = 0.001  # 1ms inicial
    
    for intento in range(max_intentos):
        metricas.intentos_lock += 1
        inicio_intento = time.perf_counter()
        
        # Intentar obtener lock con timeout
        adquirido = lock.acquire(timeout=0.01)  # Timeout muy corto
        
        if adquirido:
            try:
                # SECCIÓN CRÍTICA
                balance_actual = balance.value
                
                if tipo == 'deposito':
                    balance.value += monto
                    return True
                elif tipo == 'retiro':
                    if balance_actual >= monto:
                        balance.value -= monto
                        return True
                    else:
                        return False  # Fondos insuficientes
                
            finally:
                lock.release()
                fin_intento = time.perf_counter()
                metricas.tiempo_esperando += fin_intento - inicio_intento
                return True
        
        else:
            # No se pudo obtener lock, aplicar back-off exponencial
            metricas.reintentos += 1
            
            if intento < max_intentos - 1:  # No hacer back-off en el último intento
                # Calcular delay exponencial con jitter
                delay = delay_base * (2 ** intento)
                jitter = random.uniform(0, delay * 0.1)  # 10% de jitter para evitar sincronización
                delay_total = delay + jitter
                
                metricas.backoff_aplicado += 1
                print(f"[Cajero {cajero_id}] Lock ocupado, back-off {delay_total*1000:.1f}ms (intento {intento+1})")
                
                time.sleep(delay_total)
    
    # Después de max_intentos, registrar el tiempo total de espera
    fin_intento = time.perf_counter()
    metricas.tiempo_esperando += fin_intento - inicio_intento
    
    print(f"[Cajero {cajero_id}] ⚠️  No se pudo obtener lock después de {max_intentos} intentos")
    return False

def monitor_balance(balance, duracion, intervalo=1.0):
    """
    Proceso que monitorea el balance del banco periódicamente.
    
    Args:
        balance: Value compartido con el balance
        duracion: Tiempo en segundos a monitorear  
        intervalo: Intervalo entre lecturas en segundos
    """
    print(f"[Monitor] Iniciado - monitoreando balance cada {intervalo}s por {duracion}s")
    
    fin_tiempo = time.time() + duracion
    lecturas = []
    
    while time.time() < fin_tiempo:
        timestamp = time.time()
        balance_actual = balance.value
        
        lecturas.append({
            'timestamp': timestamp,
            'balance': balance_actual,
            'tiempo': time.strftime("%H:%M:%S", time.localtime(timestamp))
        })
        
        print(f"[Monitor] {time.strftime('%H:%M:%S')}: Balance = ${balance_actual:,}")
        time.sleep(intervalo)
    
    print(f"[Monitor] Terminado - {len(lecturas)} lecturas realizadas")
    return lecturas

def main():
    """
    Simulación principal del banco con múltiples cajeros.
    """
    print("=== Ejercicio 9: Simulación de banco con back-off exponencial ===")
    
    # Configuración de la simulación
    balance_inicial = 10000
    num_cajeros = 6
    transacciones_por_cajero = 10
    clientes_por_cajero = 5
    duracion_simulacion = 15  # segundos
    
    print(f"Configuración de la simulación:")
    print(f"  Balance inicial: ${balance_inicial:,}")
    print(f"  Cajeros: {num_cajeros}")
    print(f"  Transacciones por cajero: {transacciones_por_cajero}")
    print(f"  Clientes por cajero: ~{clientes_por_cajero}")
    print(f"  Duración: {duracion_simulacion} segundos")
    
    # Crear recursos compartidos
    balance = Value('d', balance_inicial)  # 'd' para double/float
    lock = Lock()
    metricas_queue = Queue()
    
    print(f"\n🏦 Iniciando simulación bancaria...")
    inicio_simulacion = time.perf_counter()
    
    # Crear procesos cajeros
    cajeros = []
    for i in range(num_cajeros):
        proceso = Process(
            target=cajero_banco,
            args=(balance, lock, metricas_queue, i + 1, transacciones_por_cajero, clientes_por_cajero)
        )
        cajeros.append(proceso)
        proceso.start()
        print(f"[Banco] Cajero {i + 1} iniciado - PID: {proceso.pid}")
    
    # Crear proceso monitor
    monitor = Process(
        target=monitor_balance,
        args=(balance, duracion_simulacion, 1.0)
    )
    monitor.start()
    print(f"[Banco] Monitor iniciado - PID: {monitor.pid}")
    
    # Esperar que terminen todos los cajeros
    print(f"\n[Banco] Esperando finalización de cajeros...")
    for i, cajero in enumerate(cajeros):
        cajero.join()
        print(f"[Banco] Cajero {i + 1} terminado")
    
    # Esperar monitor
    monitor.join()
    print("[Banco] Monitor terminado")
    
    fin_simulacion = time.perf_counter()
    duracion_real = fin_simulacion - inicio_simulacion
    
    # Recolectar métricas de todos los cajeros
    metricas_cajeros = []
    for _ in range(num_cajeros):
        metricas = metricas_queue.get()
        metricas_cajeros.append(metricas)
    
    # Generar reporte final
    generar_reporte_banco(metricas_cajeros, balance, balance_inicial, duracion_real)

def generar_reporte_banco(metricas_cajeros, balance, balance_inicial, duracion):
    """
    Genera reporte detallado de la simulación bancaria.
    
    Args:
        metricas_cajeros: Lista con métricas de cada cajero
        balance: Value con balance final
        balance_inicial: Balance inicial del banco
        duracion: Duración real de la simulación
    """
    print(f"\n" + "="*80)
    print("📊 REPORTE DE SIMULACIÓN BANCARIA")
    print("="*80)
    
    balance_final = balance.value
    
    # Estadísticas generales
    total_transacciones = sum(m['transacciones_exitosas'] + m['transacciones_rechazadas'] for m in metricas_cajeros)
    total_exitosas = sum(m['transacciones_exitosas'] for m in metricas_cajeros)
    total_rechazadas = sum(m['transacciones_rechazadas'] for m in metricas_cajeros)
    
    print(f"💰 ESTADO FINANCIERO:")
    print(f"  Balance inicial: ${balance_inicial:,}")
    print(f"  Balance final: ${balance_final:,}")
    print(f"  Cambio neto: ${balance_final - balance_inicial:+,}")
    
    print(f"\n📊 TRANSACCIONES:")
    print(f"  Total procesadas: {total_transacciones:,}")
    print(f"  Exitosas: {total_exitosas:,} ({total_exitosas/total_transacciones*100:.1f}%)")
    print(f"  Rechazadas: {total_rechazadas:,} ({total_rechazadas/total_transacciones*100:.1f}%)")
    print(f"  Duración: {duracion:.2f} segundos")
    print(f"  Throughput: {total_transacciones/duracion:.1f} transacciones/segundo")
    
    # Métricas de contención
    total_intentos_lock = sum(m['intentos_lock'] for m in metricas_cajeros)
    total_reintentos = sum(m['reintentos'] for m in metricas_cajeros)
    total_backoff = sum(m['backoff_aplicado'] for m in metricas_cajeros)
    total_tiempo_espera = sum(m['tiempo_esperando'] for m in metricas_cajeros)
    
    print(f"\n🔒 MÉTRICAS DE CONTENCIÓN (Back-off exponencial):")
    print(f"  Total intentos de lock: {total_intentos_lock:,}")
    print(f"  Reintentos necesarios: {total_reintentos:,} ({total_reintentos/total_intentos_lock*100:.1f}%)")
    print(f"  Back-off aplicados: {total_backoff:,}")
    print(f"  Tiempo total esperando: {total_tiempo_espera:.3f} segundos")
    print(f"  Tiempo promedio de espera: {total_tiempo_espera/total_intentos_lock*1000:.2f}ms por intento")
    
    # Detalles por cajero
    print(f"\n👥 RENDIMIENTO POR CAJERO:")
    for metricas in sorted(metricas_cajeros, key=lambda x: x['cajero_id']):
        tasa_exito = metricas['transacciones_exitosas'] / (metricas['transacciones_exitosas'] + metricas['transacciones_rechazadas']) * 100
        contention_rate = metricas['reintentos'] / metricas['intentos_lock'] * 100
        
        print(f"  Cajero {metricas['cajero_id']} (PID {metricas['pid']}):")
        print(f"    Transacciones: {metricas['transacciones_exitosas']}✅ + {metricas['transacciones_rechazadas']}❌ ({tasa_exito:.1f}% éxito)")
        print(f"    Contención: {metricas['reintentos']}/{metricas['intentos_lock']} ({contention_rate:.1f}%)")
        print(f"    Back-off: {metricas['backoff_aplicado']} aplicaciones")
        print(f"    Tiempo espera: {metricas['tiempo_esperando']*1000:.1f}ms")
    
    # Análisis de eficiencia
    print(f"\n🔍 ANÁLISIS DE EFICIENCIA:")
    if total_reintentos / total_intentos_lock < 0.1:
        print("  ✅ Baja contención: Back-off exponencial funcionó bien")
    elif total_reintentos / total_intentos_lock < 0.3:
        print("  ⚠️  Contención moderada: Sistema funcionando adecuadamente")
    else:
        print("  ❌ Alta contención: Considerar optimizaciones (más granularidad, menos cajeros)")
    
    if total_rechazadas / total_transacciones > 0.2:
        print("  💡 Alto porcentaje de rechazos: Considerar balance inicial mayor")
    
    print(f"\n💡 CONCEPTOS DEMOSTRADOS:")
    print("  1. Back-off exponencial para reducir contención")
    print("  2. Métricas de rendimiento en sistemas concurrentes")
    print("  3. Simulación realista de sistema bancario")
    print("  4. Manejo de recursos compartidos con múltiples escritores")
    print("  5. Análisis de throughput y latencia en concurrencia")
    
    print("="*80)

if __name__ == '__main__':
    # Semilla para reproducibilidad
    random.seed(42)
    main()