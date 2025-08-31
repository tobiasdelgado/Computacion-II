#!/usr/bin/env python3
"""
Ejercicio 8: Simular un servidor multiproceso
Objetivo: Simular un servidor que atiende conexiones de clientes lanzando un hijo por cada uno
Ideal para comprender cómo escalar procesos de manera controlada
"""
import os
import time
import random

def atender_cliente(numero_cliente):
    """Simula la atención de un cliente creando un proceso hijo"""
    pid = os.fork()
    
    if pid == 0:
        # Proceso hijo atiende al cliente
        tiempo_atencion = random.randint(1, 3)
        
        print(f"[SERVIDOR-{numero_cliente}] PID: {os.getpid()}")
        print(f"[SERVIDOR-{numero_cliente}] Atendiendo cliente {numero_cliente}")
        
        # Simular tiempo de procesamiento variable
        for i in range(tiempo_atencion):
            print(f"[SERVIDOR-{numero_cliente}] Procesando solicitud... {i+1}/{tiempo_atencion}")
            time.sleep(1)
        
        print(f"[SERVIDOR-{numero_cliente}] Cliente {numero_cliente} atendido correctamente")
        os._exit(0)
    
    return pid

def main():
    print("=== Ejercicio 8: Servidor multiproceso ===")
    print("Simulando servidor que atiende 5 clientes simultáneamente")
    print()
    
    num_clientes = 5
    pids_hijos = []
    
    print("[SERVIDOR PRINCIPAL] Iniciando servidor...")
    print(f"[SERVIDOR PRINCIPAL] PID: {os.getpid()}")
    print()
    
    # Simular llegada de clientes
    for cliente in range(num_clientes):
        print(f"[SERVIDOR PRINCIPAL] Cliente {cliente} conectado")
        pid_hijo = atender_cliente(cliente)
        pids_hijos.append(pid_hijo)
        
        # Pequeña pausa entre llegadas de clientes
        time.sleep(0.5)
    
    print(f"[SERVIDOR PRINCIPAL] {num_clientes} procesos de atención creados")
    print("[SERVIDOR PRINCIPAL] Esperando que terminen todas las atenciones...")
    print()
    
    # Esperar a que terminen todos los procesos de atención
    clientes_atendidos = 0
    while clientes_atendidos < num_clientes:
        pid, status = os.wait()
        clientes_atendidos += 1
        print(f"[SERVIDOR PRINCIPAL] Proceso {pid} terminó ({clientes_atendidos}/{num_clientes})")
    
    print()
    print("[SERVIDOR PRINCIPAL] Todos los clientes atendidos. Servidor finalizado.")

if __name__ == "__main__":
    main()