#!/usr/bin/env python3

# Ejercicio 3: Pipeline de Filtrado
# Crea una cadena de tres procesos conectados por pipes donde: 
# - El primer proceso genera números aleatorios entre 1 y 100
# - El segundo proceso filtra solo los números pares
# - El tercer proceso calcula el cuadrado de estos números pares

import os
import sys
import random

def main():
    # Crear dos pipes para conectar los tres procesos
    # pipe1: generador -> filtrador
    # pipe2: filtrador -> calculador
    pipe1 = os.pipe()
    pipe2 = os.pipe()
    
    # Crear primer proceso hijo (generador)
    pid1 = os.fork()
    
    if pid1 > 0:  # Proceso padre
        # Crear segundo proceso hijo (filtrador)
        pid2 = os.fork()
        
        if pid2 > 0:  # Proceso padre (será el calculador)
            # Cerrar extremos no utilizados
            os.close(pipe1[0])  # No lee del pipe1
            os.close(pipe1[1])  # No escribe al pipe1
            os.close(pipe2[1])  # No escribe al pipe2
            
            print("Calculador: Iniciado, esperando números pares...")
            
            # Leer números pares y calcular cuadrados
            while True:
                try:
                    datos = os.read(pipe2[0], 1024).decode().strip()
                    if not datos:
                        break
                    
                    if datos == "FIN":
                        print("Calculador: Recibida señal de fin")
                        break
                    
                    numero_par = int(datos)
                    cuadrado = numero_par ** 2
                    print(f"Calculador: {numero_par}² = {cuadrado}")
                    
                except (ValueError, OSError):
                    break
            
            os.close(pipe2[0])
            
            # Esperar a los procesos hijos
            os.waitpid(pid1, 0)
            os.waitpid(pid2, 0)
            print("Pipeline completado")
            
        elif pid2 == 0:  # Segundo proceso hijo (filtrador)
            # Cerrar extremos no utilizados
            os.close(pipe1[1])  # No escribe al pipe1
            os.close(pipe2[0])  # No lee del pipe2
            
            print("Filtrador: Iniciado, filtrando números pares...")
            
            # Leer números del generador y filtrar pares
            while True:
                try:
                    datos = os.read(pipe1[0], 1024).decode().strip()
                    if not datos:
                        break
                    
                    if datos == "FIN":
                        print("Filtrador: Recibida señal de fin, enviando FIN al calculador")
                        os.write(pipe2[1], b"FIN")
                        break
                    
                    numero = int(datos)
                    if numero % 2 == 0:  # Es par
                        print(f"Filtrador: {numero} es par, enviando al calculador")
                        os.write(pipe2[1], str(numero).encode())
                    else:
                        print(f"Filtrador: {numero} es impar, descartando")
                        
                except (ValueError, OSError):
                    break
            
            os.close(pipe1[0])
            os.close(pipe2[1])
            sys.exit(0)
            
        else:  # Error en segundo fork
            print("Error al crear segundo proceso hijo")
            sys.exit(1)
            
    elif pid1 == 0:  # Primer proceso hijo (generador)
        # Cerrar extremos no utilizados
        os.close(pipe1[0])  # No lee del pipe1
        os.close(pipe2[0])  # No usa pipe2
        os.close(pipe2[1])  # No usa pipe2
        
        print("Generador: Iniciado, generando números aleatorios...")
        
        # Generar 15 números aleatorios entre 1 y 100
        random.seed()  # Inicializar generador
        for i in range(15):
            numero = random.randint(1, 100)
            print(f"Generador: Generado {numero}")
            os.write(pipe1[1], str(numero).encode())
        
        # Enviar señal de fin
        print("Generador: Enviando señal de fin")
        os.write(pipe1[1], b"FIN")
        
        os.close(pipe1[1])
        sys.exit(0)
        
    else:  # Error en primer fork
        print("Error al crear primer proceso hijo")
        sys.exit(1)

if __name__ == "__main__":
    main()