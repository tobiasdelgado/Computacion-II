#!/bin/bash
# **Ejercicio 2: Redirección de Entrada y Contar Líneas**
# **Objetivo:** Leer un archivo y contar sus líneas sin usar la interfaz interactiva de `wc`.

# **Instrucción:**
# Utiliza redirección para contar cuántas líneas tiene el archivo `listado.txt` que creaste en el ejercicio anterior.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
wc -l < "$SCRIPT_DIR/ej-1.txt"
