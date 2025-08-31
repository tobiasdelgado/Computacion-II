#!/bin/bash
# **Ejercicio 1: Redirección de Salida Básica**
# **Objetivo:** Crear un archivo con el listado de archivos y carpetas de un directorio.

# **Instrucción:**
# Ejecuta un comando que guarde la salida del listado de archivos de tu directorio actual en un archivo llamado `listado.txt`.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ls "$SCRIPT_DIR" > ej-1.txt
