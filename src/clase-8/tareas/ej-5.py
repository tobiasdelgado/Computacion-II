#!/usr/bin/env python3

# Ejercicio 5 · Nivel Experto
#
# Objetivo: diseñar un pipeline productor–consumidor usando Pipe doble.
#
# Enunciado: crea dos procesos hijos: productor genera 10 números pseudo-aleatorios y los 
# envía al padre; el padre los reenvía a un consumidor, que imprime el cuadrado de cada número. 
# Implementa el pipeline con dos Pipe(), asegurando el cierre limpio de extremos y detectando 
# fin de datos mediante envío del valor None.

from multiprocessing import Process, Pipe, current_process
import random
import time

def productor(conn_out, num_datos=10):
    """
    Proceso productor que genera números aleatorios.
    
    Pipe() crea un canal bidireccional, pero aquí solo usamos un extremo.
    conn_out es el extremo de escritura del pipe productor -> padre.
    
    Args:
        conn_out: Conexión de salida (extremo de escritura del pipe)
        num_datos: Cantidad de números a generar
    """
    print(f"[Productor] Iniciado - PID: {current_process().pid}")
    print(f"[Productor] Generando {num_datos} números aleatorios...")
    
    try:
        for i in range(num_datos):
            # Generar número aleatorio entre 1 y 100
            numero = random.randint(1, 100)
            print(f"[Productor] Generando {i+1}/{num_datos}: {numero}")
            
            # Enviar número al padre a través del pipe
            # send() serializa el objeto y lo envía
            conn_out.send(numero)
            
            # Simular tiempo de procesamiento
            time.sleep(0.2)
        
        # Enviar señal de fin - None indica que no hay más datos
        print("[Productor] Enviando señal de fin (None)")
        conn_out.send(None)
        
    except Exception as e:
        print(f"[Productor] Error: {e}")
    finally:
        # Cerrar conexión limpiamente
        conn_out.close()
        print("[Productor] Conexión cerrada, terminando")

def consumidor(conn_in):
    """
    Proceso consumidor que recibe números y calcula sus cuadrados.
    
    conn_in es el extremo de lectura del pipe padre -> consumidor.
    
    Args:
        conn_in: Conexión de entrada (extremo de lectura del pipe)
    """
    print(f"[Consumidor] Iniciado - PID: {current_process().pid}")
    print("[Consumidor] Esperando datos del pipeline...")
    
    contador = 0
    
    try:
        while True:
            # recv() bloquea hasta recibir un dato o que se cierre la conexión
            dato = conn_in.recv()
            
            # Verificar señal de fin
            if dato is None:
                print("[Consumidor] Recibida señal de fin (None)")
                break
            
            contador += 1
            cuadrado = dato ** 2
            print(f"[Consumidor] Dato {contador}: {dato} -> cuadrado = {cuadrado}")
            
            # Simular tiempo de procesamiento
            time.sleep(0.1)
    
    except EOFError:
        # Se produce cuando la conexión se cierra inesperadamente
        print("[Consumidor] Conexión cerrada por el emisor")
    except Exception as e:
        print(f"[Consumidor] Error: {e}")
    finally:
        conn_in.close()
        print(f"[Consumidor] Procesados {contador} números, terminando")

def main():
    """
    Proceso padre que coordina el pipeline productor -> padre -> consumidor.
    
    Arquitectura:
    [Productor] --pipe1--> [Padre] --pipe2--> [Consumidor]
    
    El padre actúa como intermediario que reenvía datos entre procesos.
    """
    print("=== Ejercicio 5: Pipeline productor-consumidor con Pipe doble ===")
    print(f"[Padre] PID: {current_process().pid}")
    
    # Crear dos pipes bidireccionales
    # Pipe() devuelve (conn1, conn2) donde ambos pueden leer/escribir
    # Convencionalmente: conn1 para el proceso padre, conn2 para el proceso hijo
    
    # Pipe 1: Productor -> Padre
    padre_in, productor_out = Pipe()
    
    # Pipe 2: Padre -> Consumidor  
    consumidor_in, padre_out = Pipe()
    
    print("[Padre] Pipes creados:")
    print("  - Pipe 1: Productor -> Padre")
    print("  - Pipe 2: Padre -> Consumidor")
    
    # Crear proceso productor
    proc_productor = Process(target=productor, args=(productor_out, 10))
    
    # Crear proceso consumidor
    proc_consumidor = Process(target=consumidor, args=(consumidor_in,))
    
    # Iniciar procesos
    print("\n[Padre] Iniciando procesos...")
    proc_productor.start()
    proc_consumidor.start()
    
    print(f"[Padre] Productor iniciado - PID: {proc_productor.pid}")
    print(f"[Padre] Consumidor iniciado - PID: {proc_consumidor.pid}")
    
    # El padre debe cerrar los extremos que no usa
    # Esto es importante para que los procesos hijos detecten EOF correctamente
    productor_out.close()  # El padre no escribirá a este extremo
    consumidor_in.close()   # El padre no leerá de este extremo
    
    # Proceso padre actúa como relay/intermediario
    print("\n[Padre] Actuando como intermediario en el pipeline...")
    
    datos_reenviados = 0
    
    try:
        while True:
            # Leer del productor
            dato = padre_in.recv()
            
            # Verificar señal de fin
            if dato is None:
                print("[Padre] Recibida señal de fin del productor")
                # Reenviar señal de fin al consumidor
                padre_out.send(None)
                print("[Padre] Señal de fin reenviada al consumidor")
                break
            
            datos_reenviados += 1
            print(f"[Padre] Reenviando dato {datos_reenviados}: {dato}")
            
            # Reenviar al consumidor
            padre_out.send(dato)
    
    except EOFError:
        print("[Padre] Productor cerró la conexión")
    except Exception as e:
        print(f"[Padre] Error en relay: {e}")
    finally:
        # Cerrar conexiones del padre
        padre_in.close()
        padre_out.close()
    
    print(f"\n[Padre] Pipeline completado. Datos reenviados: {datos_reenviados}")
    print("[Padre] Esperando a que terminen los procesos hijos...")
    
    # Esperar a que terminen los procesos
    proc_productor.join()
    print("[Padre] Productor terminado")
    
    proc_consumidor.join()
    print("[Padre] Consumidor terminado")
    
    print("\n✅ Pipeline completado exitosamente")
    
    # Mostrar resumen
    print(f"\n📊 RESUMEN DEL PIPELINE:")
    print(f"- Procesos creados: 3 (Padre, Productor, Consumidor)")
    print(f"- Pipes utilizados: 2 (Productor->Padre, Padre->Consumidor)")
    print(f"- Datos procesados: {datos_reenviados}")
    print(f"- Señal de fin: None")
    print(f"- Arquitectura: Productor -> Padre -> Consumidor")

def demo_simple():
    """
    Demo simplificada del pipeline sin el proceso padre como intermediario.
    Conexión directa: Productor -> Consumidor
    """
    print("\n" + "="*60)
    print("🔄 DEMO SIMPLE: Pipeline directo Productor -> Consumidor")
    print("="*60)
    
    # Un solo pipe para conexión directa
    consumidor_conn, productor_conn = Pipe()
    
    # Crear procesos
    proc_productor = Process(target=productor, args=(productor_conn, 5))
    proc_consumidor = Process(target=consumidor, args=(consumidor_conn,))
    
    # Iniciar procesos
    proc_productor.start()
    proc_consumidor.start()
    
    # Cerrar conexiones en el proceso principal
    productor_conn.close()
    consumidor_conn.close()
    
    # Esperar terminación
    proc_productor.join()
    proc_consumidor.join()
    
    print("✅ Demo simple completada")

if __name__ == '__main__':
    # Semilla para reproducibilidad
    random.seed(42)
    
    # Pipeline principal con 3 procesos
    main()
    
    # Demo adicional con pipeline directo
    print("\n" + "="*80)
    input("Presiona Enter para ejecutar demo simple...")
    random.seed(42)  # Misma semilla para comparar
    demo_simple()