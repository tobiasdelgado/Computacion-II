#!/bin/bash
# **Ejercicio 7: Uso de `/dev/null` para Silenciar Salida**
# **Objetivo:** Ejecutar un comando sin mostrar nada en pantalla.

# **Instrucción:**
# Ejecuta un comando que intente listar un directorio inexistente y envía **toda** su salida a `/dev/null`.

ls /directorio/inexistente &> /dev/null