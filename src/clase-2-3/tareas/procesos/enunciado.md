# Ejercicios de Procesos en Python

## 4.1 Ejercicios básicos

### Ejercicio 1: Crear un proceso hijo y mostrar los PID
**Objetivo:** utilizar `fork()` y comprender la relación padre-hijo.

### Ejercicio 2: Crear dos hijos desde el mismo padre
**Objetivo:** ver cómo un solo padre puede lanzar múltiples procesos hijos.

---

## 4.2 Ejercicios intermedios

### Ejercicio 3: Ejecutar otro programa con `exec()`
**Objetivo:** reemplazar el proceso hijo con un nuevo programa externo.

### Ejercicio 4: Crear procesos secuenciales
**Objetivo:** lanzar un hijo, esperar su finalización, y luego crear otro.

---

## 4.3 Ejercicios avanzados

### Ejercicio 5: Producir y observar un proceso zombi
**Objetivo:** generar un proceso zombi temporal para su inspección.

### Ejercicio 6: Crear un proceso huérfano
**Objetivo:** observar la adopción de procesos por `init`.

### Ejercicio 7: Crear múltiples procesos simultáneos
**Objetivo:** observar la expansión del árbol de procesos.

---

## 4.4 Desafío extra

### Ejercicio 8: Simular un servidor multiproceso
**Objetivo:** Simular un servidor que atiende conexiones de clientes (ficticios) lanzando un hijo por cada uno. Ideal para comprender cómo escalar procesos de manera controlada.

---

## Instrucciones de ejecución

Para ejecutar los ejercicios:

```bash
python3 ej-1.py
python3 ej-2.py
# ... etc
```

**Nota importante:** Los ejercicios 5 y 6 requieren observación externa con comandos como `ps` para ver el comportamiento de procesos zombi y huérfanos.