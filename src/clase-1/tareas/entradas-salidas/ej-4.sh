#!/bin/bash
# **Ejercicio 4: Uso de Pipes**
# **Objetivo:** Encadenar comandos para filtrar información.

# **Instrucción:**
# Lista los archivos de tu directorio actual y usa `grep` para mostrar solo los archivos que contienen la palabra "log" en su nombre.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ls "$SCRIPT_DIR" | grep log