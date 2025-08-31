#!/bin/bash
# **Ejercicio 5: Contar Archivos con Pipes**
# **Objetivo:** Contar cuántos archivos cumplen con un criterio.

# **Instrucción:**
# Usa un pipe para contar cuántos archivos en tu directorio contienen la palabra "txt" en su nombre.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ls "$SCRIPT_DIR" | grep txt | wc -l