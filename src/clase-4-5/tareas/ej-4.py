#!/usr/bin/env python3

# Ejercicio 4: Simulador de Shell
# Implementa un programa que simule una versión simplificada del operador pipe (|) de la shell.
# El programa debe ejecutar dos comandos proporcionados por el usuario y conectar la salida 
# del primero con la entrada del segundo.

import os
import sys
import subprocess

def main():
    # Solicitar comandos al usuario
    print("Simulador de Shell - Operador Pipe (|)")
    print("Ejemplo de uso: 'ls -la' | 'grep txt'")
    print()
    
    comando1 = input("Ingrese el primer comando: ").strip()
    comando2 = input("Ingrese el segundo comando: ").strip()
    
    if not comando1 or not comando2:
        print("Error: Ambos comandos son requeridos")
        return
    
    print(f"\nEjecutando: {comando1} | {comando2}")
    print("-" * 50)
    
    # Crear pipe para conectar los comandos
    pipe_fd = os.pipe()
    
    # Crear primer proceso hijo para el primer comando
    pid1 = os.fork()
    
    if pid1 > 0:  # Proceso padre
        # Crear segundo proceso hijo para el segundo comando
        pid2 = os.fork()
        
        if pid2 > 0:  # Proceso padre
            # El padre cierra ambos extremos del pipe
            os.close(pipe_fd[0])
            os.close(pipe_fd[1])
            
            # Esperar a ambos procesos hijos
            os.waitpid(pid1, 0)
            os.waitpid(pid2, 0)
            
            print("-" * 50)
            print("Pipeline completado")
            
        elif pid2 == 0:  # Segundo proceso hijo (comando2)
            # Cerrar extremo de escritura del pipe
            os.close(pipe_fd[1])
            
            # Redirigir stdin para leer del pipe
            os.dup2(pipe_fd[0], sys.stdin.fileno())
            os.close(pipe_fd[0])
            
            try:
                # Ejecutar segundo comando
                # Separar comando y argumentos
                args = comando2.split()
                os.execvp(args[0], args)
                
            except OSError as e:
                print(f"Error ejecutando '{comando2}': {e}")
                sys.exit(1)
                
        else:  # Error en segundo fork
            print("Error al crear segundo proceso hijo")
            sys.exit(1)
            
    elif pid1 == 0:  # Primer proceso hijo (comando1)
        # Cerrar extremo de lectura del pipe
        os.close(pipe_fd[0])
        
        # Redirigir stdout para escribir al pipe
        os.dup2(pipe_fd[1], sys.stdout.fileno())
        os.close(pipe_fd[1])
        
        try:
            # Ejecutar primer comando
            # Separar comando y argumentos
            args = comando1.split()
            os.execvp(args[0], args)
            
        except OSError as e:
            print(f"Error ejecutando '{comando1}': {e}", file=sys.stderr)
            sys.exit(1)
            
    else:  # Error en primer fork
        print("Error al crear primer proceso hijo")
        sys.exit(1)

# Función alternativa usando subprocess (más simple pero menos educativa)
def simulador_subprocess():
    """
    Versión alternativa usando subprocess.Popen que es más robusta
    pero menos educativa para entender los pipes a bajo nivel
    """
    print("Simulador de Shell - Versión con subprocess")
    print("Ejemplo de uso: 'ls -la' | 'grep txt'")
    print()
    
    comando1 = input("Ingrese el primer comando: ").strip()
    comando2 = input("Ingrese el segundo comando: ").strip()
    
    if not comando1 or not comando2:
        print("Error: Ambos comandos son requeridos")
        return
    
    try:
        # Crear primer proceso
        proc1 = subprocess.Popen(comando1.split(), stdout=subprocess.PIPE)
        
        # Crear segundo proceso que lee del primero
        proc2 = subprocess.Popen(comando2.split(), stdin=proc1.stdout, stdout=subprocess.PIPE)
        
        # Cerrar stdout del primer proceso en el padre
        proc1.stdout.close()
        
        # Obtener resultado final
        salida, error = proc2.communicate()
        
        if salida:
            print(salida.decode())
        if error:
            print(f"Error: {error.decode()}", file=sys.stderr)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Usar la versión con fork y pipes de bajo nivel por defecto
    main()
    
    # Descomentar la siguiente línea para usar la versión con subprocess
    # simulador_subprocess()