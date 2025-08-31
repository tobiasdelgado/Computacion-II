#!/usr/bin/env python3

# Ejercicio 7: Sistema de Procesamiento de Transacciones
# Implementa un sistema donde múltiples procesos "generadores" crean transacciones 
# (operaciones con un ID, tipo y monto), las envían a un proceso "validador" que 
# verifica su integridad, y finalmente a un proceso "registrador" que acumula las 
# estadísticas. Usa múltiples pipes para manejar este flujo complejo y asegúrate 
# de manejar correctamente la sincronización y el cierre de la comunicación.

import os
import sys
import json
import random
import time
from datetime import datetime

class Transaccion:
    """Clase para representar una transacción"""
    def __init__(self, id_transaccion, tipo, monto, timestamp=None):
        self.id = id_transaccion
        self.tipo = tipo  # 'deposito', 'retiro', 'transferencia'
        self.monto = monto
        self.timestamp = timestamp or datetime.now().isoformat()
    
    def to_json(self):
        return json.dumps({
            'id': self.id,
            'tipo': self.tipo,
            'monto': self.monto,
            'timestamp': self.timestamp
        })
    
    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls(data['id'], data['tipo'], data['monto'], data['timestamp'])

def generador_transacciones(id_generador, pipe_salida, num_transacciones=5):
    """
    Proceso generador que crea transacciones aleatorias
    """
    print(f"Generador {id_generador}: Iniciado")
    
    tipos_transaccion = ['deposito', 'retiro', 'transferencia']
    
    for i in range(num_transacciones):
        # Crear transacción aleatoria
        id_trans = f"G{id_generador}T{i+1}"
        tipo = random.choice(tipos_transaccion)
        monto = round(random.uniform(10.0, 1000.0), 2)
        
        # Ocasionalmente crear transacciones inválidas para probar el validador
        if random.random() < 0.1:  # 10% de probabilidad
            monto = -monto  # Monto negativo (inválido)
        
        transaccion = Transaccion(id_trans, tipo, monto)
        
        print(f"Generador {id_generador}: Creando {transaccion.tipo} por ${transaccion.monto} (ID: {transaccion.id})")
        
        # Enviar al validador
        os.write(pipe_salida, transaccion.to_json().encode())
        
        # Pequeña pausa entre transacciones
        time.sleep(0.5)
    
    # Señalar fin de este generador
    mensaje_fin = json.dumps({"fin_generador": id_generador})
    os.write(pipe_salida, mensaje_fin.encode())
    print(f"Generador {id_generador}: Terminado")

def validador_transacciones(pipe_entrada, pipe_salida, num_generadores):
    """
    Proceso validador que verifica la integridad de las transacciones
    """
    print("Validador: Iniciado")
    
    transacciones_procesadas = 0
    transacciones_validas = 0
    transacciones_invalidas = 0
    generadores_terminados = 0
    
    while generadores_terminados < num_generadores:
        try:
            # Leer datos del pipe
            datos = os.read(pipe_entrada, 1024).decode().strip()
            if not datos:
                continue
            
            # Verificar si es un mensaje de fin de generador
            try:
                mensaje = json.loads(datos)
                if "fin_generador" in mensaje:
                    generadores_terminados += 1
                    print(f"Validador: Generador {mensaje['fin_generador']} terminado ({generadores_terminados}/{num_generadores})")
                    continue
            except:
                pass
            
            # Procesar transacción
            transaccion = Transaccion.from_json(datos)
            transacciones_procesadas += 1
            
            # Validar transacción
            es_valida = True
            motivo_invalida = ""
            
            if transaccion.monto <= 0:
                es_valida = False
                motivo_invalida = "Monto debe ser positivo"
            elif transaccion.tipo not in ['deposito', 'retiro', 'transferencia']:
                es_valida = False
                motivo_invalida = "Tipo de transacción inválido"
            elif transaccion.monto > 10000:  # Límite arbitrario
                es_valida = False
                motivo_invalida = "Monto excede el límite permitido"
            
            if es_valida:
                transacciones_validas += 1
                print(f"Validador: ✓ {transaccion.id} - {transaccion.tipo} ${transaccion.monto}")
                
                # Enviar al registrador
                transaccion_validada = {
                    "transaccion": json.loads(transaccion.to_json()),
                    "validada": True
                }
                os.write(pipe_salida, json.dumps(transaccion_validada).encode())
            else:
                transacciones_invalidas += 1
                print(f"Validador: ✗ {transaccion.id} - RECHAZADA: {motivo_invalida}")
                
                # Enviar rechazo al registrador para estadísticas
                transaccion_rechazada = {
                    "transaccion": json.loads(transaccion.to_json()),
                    "validada": False,
                    "motivo": motivo_invalida
                }
                os.write(pipe_salida, json.dumps(transaccion_rechazada).encode())
        
        except (json.JSONDecodeError, KeyError, OSError) as e:
            print(f"Validador: Error procesando datos: {e}")
    
    # Enviar mensaje de fin al registrador
    mensaje_fin = json.dumps({"fin_validador": True})
    os.write(pipe_salida, mensaje_fin.encode())
    
    print(f"Validador: Terminado - Procesadas: {transacciones_procesadas}, Válidas: {transacciones_validas}, Inválidas: {transacciones_invalidas}")

def registrador_transacciones(pipe_entrada):
    """
    Proceso registrador que acumula estadísticas de las transacciones
    """
    print("Registrador: Iniciado")
    
    estadisticas = {
        'total_transacciones': 0,
        'transacciones_validas': 0,
        'transacciones_invalidas': 0,
        'total_depositos': 0,
        'total_retiros': 0,
        'total_transferencias': 0,
        'monto_total_procesado': 0.0,
        'motivos_rechazo': {}
    }
    
    while True:
        try:
            datos = os.read(pipe_entrada, 1024).decode().strip()
            if not datos:
                continue
            
            mensaje = json.loads(datos)
            
            # Verificar si es mensaje de fin
            if "fin_validador" in mensaje:
                print("Registrador: Recibida señal de fin del validador")
                break
            
            # Procesar transacción validada o rechazada
            if "transaccion" in mensaje:
                estadisticas['total_transacciones'] += 1
                transaccion = mensaje['transaccion']
                
                if mensaje['validada']:
                    # Transacción válida
                    estadisticas['transacciones_validas'] += 1
                    estadisticas['monto_total_procesado'] += transaccion['monto']
                    
                    # Contar por tipo
                    if transaccion['tipo'] == 'deposito':
                        estadisticas['total_depositos'] += 1
                    elif transaccion['tipo'] == 'retiro':
                        estadisticas['total_retiros'] += 1
                    elif transaccion['tipo'] == 'transferencia':
                        estadisticas['total_transferencias'] += 1
                    
                    print(f"Registrador: ✓ Registrada {transaccion['id']} - {transaccion['tipo']} ${transaccion['monto']}")
                else:
                    # Transacción inválida
                    estadisticas['transacciones_invalidas'] += 1
                    motivo = mensaje.get('motivo', 'Sin motivo especificado')
                    
                    if motivo in estadisticas['motivos_rechazo']:
                        estadisticas['motivos_rechazo'][motivo] += 1
                    else:
                        estadisticas['motivos_rechazo'][motivo] = 1
                    
                    print(f"Registrador: ✗ Rechazada {transaccion['id']} - {motivo}")
        
        except (json.JSONDecodeError, KeyError, OSError) as e:
            print(f"Registrador: Error procesando datos: {e}")
    
    # Mostrar estadísticas finales
    print("\n" + "="*60)
    print("ESTADÍSTICAS FINALES DEL SISTEMA DE TRANSACCIONES")
    print("="*60)
    print(f"Total de transacciones procesadas: {estadisticas['total_transacciones']}")
    print(f"Transacciones válidas: {estadisticas['transacciones_validas']}")
    print(f"Transacciones inválidas: {estadisticas['transacciones_invalidas']}")
    print(f"Monto total procesado: ${estadisticas['monto_total_procesado']:.2f}")
    print(f"Total depósitos: {estadisticas['total_depositos']}")
    print(f"Total retiros: {estadisticas['total_retiros']}")
    print(f"Total transferencias: {estadisticas['total_transferencias']}")
    
    if estadisticas['motivos_rechazo']:
        print("\nMotivos de rechazo:")
        for motivo, cantidad in estadisticas['motivos_rechazo'].items():
            print(f"  - {motivo}: {cantidad}")
    
    print("="*60)

def main():
    print("=== Sistema de Procesamiento de Transacciones ===")
    print("Arquitectura: Generadores -> Validador -> Registrador")
    print("=" * 60)
    
    # Configuración del sistema
    num_generadores = 3
    transacciones_por_generador = 5
    
    # Crear pipes
    pipe_gen_val = os.pipe()  # Generadores -> Validador
    pipe_val_reg = os.pipe()  # Validador -> Registrador
    
    pids_generadores = []
    
    # Crear procesos generadores
    for i in range(num_generadores):
        pid = os.fork()
        if pid == 0:  # Proceso hijo (generador)
            # Cerrar extremos no utilizados
            os.close(pipe_gen_val[0])
            os.close(pipe_val_reg[0])
            os.close(pipe_val_reg[1])
            
            generador_transacciones(i+1, pipe_gen_val[1], transacciones_por_generador)
            
            os.close(pipe_gen_val[1])
            sys.exit(0)
        else:
            pids_generadores.append(pid)
    
    # Crear proceso validador
    pid_validador = os.fork()
    if pid_validador == 0:  # Proceso validador
        # Cerrar extremos no utilizados
        os.close(pipe_gen_val[1])
        os.close(pipe_val_reg[0])
        
        validador_transacciones(pipe_gen_val[0], pipe_val_reg[1], num_generadores)
        
        os.close(pipe_gen_val[0])
        os.close(pipe_val_reg[1])
        sys.exit(0)
    
    # Crear proceso registrador
    pid_registrador = os.fork()
    if pid_registrador == 0:  # Proceso registrador
        # Cerrar extremos no utilizados
        os.close(pipe_gen_val[0])
        os.close(pipe_gen_val[1])
        os.close(pipe_val_reg[1])
        
        registrador_transacciones(pipe_val_reg[0])
        
        os.close(pipe_val_reg[0])
        sys.exit(0)
    
    # Proceso padre: cerrar todos los pipes y esperar a los procesos
    os.close(pipe_gen_val[0])
    os.close(pipe_gen_val[1])
    os.close(pipe_val_reg[0])
    os.close(pipe_val_reg[1])
    
    # Esperar a todos los procesos
    for pid in pids_generadores:
        os.waitpid(pid, 0)
    
    os.waitpid(pid_validador, 0)
    os.waitpid(pid_registrador, 0)
    
    print("\nSistema de transacciones completado correctamente")

if __name__ == "__main__":
    main()