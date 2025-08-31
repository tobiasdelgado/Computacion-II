#!/usr/bin/env python3

# Ejercicio 6: Servidor de Operaciones Matemáticas
# Crea un "servidor" de operaciones matemáticas usando pipes. El proceso cliente envía 
# operaciones matemáticas como cadenas (por ejemplo, "5 + 3", "10 * 2"), y el servidor 
# las evalúa y devuelve el resultado. Implementa manejo de errores para operaciones inválidas.

import os
import sys
import re

def es_operacion_segura(operacion):
    """
    Verifica que la operación solo contenga números, espacios y operadores básicos
    Esto previene la ejecución de código malicioso
    """
    # Permitir solo números, espacios, paréntesis y operadores básicos
    patron = r'^[\d\s\+\-\*\/\(\)\.]+$'
    return re.match(patron, operacion) is not None

def evaluar_operacion(operacion):
    """
    Evalúa una operación matemática de manera segura
    """
    try:
        # Verificar que la operación es segura
        if not es_operacion_segura(operacion):
            return "ERROR: Operación no válida - solo se permiten números y operadores básicos (+, -, *, /, ())"
        
        # Evaluar la operación
        resultado = eval(operacion)
        return str(resultado)
        
    except ZeroDivisionError:
        return "ERROR: División por cero"
    except SyntaxError:
        return "ERROR: Sintaxis incorrecta"
    except Exception as e:
        return f"ERROR: {str(e)}"

def main():
    # Crear pipes para comunicación bidireccional
    pipe_cliente_servidor = os.pipe()  # Cliente envía operaciones
    pipe_servidor_cliente = os.pipe()  # Servidor envía resultados
    
    print("=== Servidor de Operaciones Matemáticas ===")
    print("El cliente puede enviar operaciones como: 5 + 3, 10 * 2, (4 + 6) / 2")
    print("Escribe 'salir' para terminar")
    print("=" * 50)
    
    # Crear proceso hijo (servidor)
    pid = os.fork()
    
    if pid > 0:  # Proceso padre (cliente)
        # Cerrar extremos no utilizados
        os.close(pipe_cliente_servidor[0])  # No lee del primer pipe
        os.close(pipe_servidor_cliente[1])  # No escribe en el segundo pipe
        
        print("Cliente iniciado. Puedes enviar operaciones matemáticas.")
        
        try:
            while True:
                # Solicitar operación al usuario
                operacion = input("Operación (o 'salir'): ").strip()
                
                if operacion.lower() == 'salir':
                    # Enviar señal de salida al servidor
                    os.write(pipe_cliente_servidor[1], b"SALIR")
                    print("Cliente: Cerrando conexión...")
                    break
                
                if operacion:  # Solo procesar si no está vacía
                    print(f"Cliente: Enviando '{operacion}' al servidor...")
                    
                    # Enviar operación al servidor
                    os.write(pipe_cliente_servidor[1], operacion.encode())
                    
                    # Leer resultado del servidor
                    resultado = os.read(pipe_servidor_cliente[0], 1024).decode()
                    print(f"Servidor: {operacion} = {resultado}")
                    print()
        
        except (KeyboardInterrupt, EOFError):
            print("\nCliente: Interrumpido por el usuario")
            os.write(pipe_cliente_servidor[1], b"SALIR")
        
        # Cerrar pipes y esperar al servidor
        os.close(pipe_cliente_servidor[1])
        os.close(pipe_servidor_cliente[0])
        os.waitpid(pid, 0)
        print("Conexión cerrada")
        
    elif pid == 0:  # Proceso hijo (servidor)
        # Cerrar extremos no utilizados
        os.close(pipe_cliente_servidor[1])  # No escribe en el primer pipe
        os.close(pipe_servidor_cliente[0])  # No lee del segundo pipe
        
        print("Servidor: Iniciado, esperando operaciones...")
        
        contador_operaciones = 0
        
        try:
            while True:
                # Leer operación del cliente
                datos = os.read(pipe_cliente_servidor[0], 1024).decode().strip()
                
                if datos == "SALIR":
                    print("Servidor: Cliente desconectado")
                    break
                
                if datos:
                    contador_operaciones += 1
                    print(f"Servidor: Recibida operación #{contador_operaciones}: '{datos}'")
                    
                    # Evaluar la operación
                    resultado = evaluar_operacion(datos)
                    
                    # Enviar resultado al cliente
                    os.write(pipe_servidor_cliente[1], resultado.encode())
                    print(f"Servidor: Resultado enviado: {resultado}")
        
        except OSError:
            print("Servidor: Error de comunicación")
        
        print(f"Servidor: Terminando... Procesadas {contador_operaciones} operaciones")
        
        # Cerrar pipes
        os.close(pipe_cliente_servidor[0])
        os.close(pipe_servidor_cliente[1])
        sys.exit(0)
        
    else:  # Error en fork
        print("Error al crear proceso servidor")
        sys.exit(1)

def servidor_multiple_clientes():
    """
    Versión extendida que simula múltiples operaciones predefinidas
    para demostrar el funcionamiento sin interacción del usuario
    """
    pipe_cliente_servidor = os.pipe()
    pipe_servidor_cliente = os.pipe()
    
    # Operaciones de prueba
    operaciones_prueba = [
        "5 + 3",
        "10 * 2", 
        "15 / 3",
        "2 ** 8",
        "(4 + 6) * 2",
        "100 / 0",  # Error: división por cero
        "5 + * 3",  # Error: sintaxis incorrecta
        "sqrt(16)",  # Error: función no permitida
        "7.5 + 2.5"
    ]
    
    print("=== Demo Automática del Servidor ===")
    
    pid = os.fork()
    
    if pid > 0:  # Cliente
        os.close(pipe_cliente_servidor[0])
        os.close(pipe_servidor_cliente[1])
        
        for i, operacion in enumerate(operaciones_prueba, 1):
            print(f"Cliente: Enviando operación {i}: '{operacion}'")
            os.write(pipe_cliente_servidor[1], operacion.encode())
            
            resultado = os.read(pipe_servidor_cliente[0], 1024).decode()
            print(f"Resultado: {operacion} = {resultado}")
            print()
        
        # Enviar señal de salida
        os.write(pipe_cliente_servidor[1], b"SALIR")
        
        os.close(pipe_cliente_servidor[1])
        os.close(pipe_servidor_cliente[0])
        os.waitpid(pid, 0)
        
    elif pid == 0:  # Servidor
        os.close(pipe_cliente_servidor[1])
        os.close(pipe_servidor_cliente[0])
        
        while True:
            datos = os.read(pipe_cliente_servidor[0], 1024).decode().strip()
            if datos == "SALIR":
                break
                
            resultado = evaluar_operacion(datos)
            os.write(pipe_servidor_cliente[1], resultado.encode())
        
        os.close(pipe_cliente_servidor[0])
        os.close(pipe_servidor_cliente[1])
        sys.exit(0)

if __name__ == "__main__":
    print("Selecciona el modo:")
    print("1. Servidor interactivo")
    print("2. Demo automática")
    
    modo = input("Modo (1 o 2): ").strip()
    
    if modo == "2":
        servidor_multiple_clientes()
    else:
        main()