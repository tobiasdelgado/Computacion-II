# Procesos y Programación Concurrente en Python

### 1. Fundamentos de Procesos y Programación Concurrente

Cuando hablamos de **procesos** en un sistema operativo moderno, no nos referimos simplemente al código de un programa. Un proceso es mucho más: es la ejecución viva de ese programa, con su propio espacio en memoria, sus archivos abiertos, su pila de llamadas, sus registros internos de CPU y hasta su pequeño “universo privado” de variables y estado. Cada proceso, en esencia, es una isla: corre en paralelo con otros, pero sin tocar directamente sus recursos, lo que garantiza seguridad y estabilidad en el sistema.

Imaginemos un ejemplo sencillo: cuando abrimos un editor de texto, ese programa se convierte en un proceso. Si al mismo tiempo escuchamos música en un reproductor, eso es otro proceso. Ambos conviven, pero no interfieren directamente en la memoria del otro. Esa separación es clave para que, si el reproductor se bloquea, el editor no se vea afectado.

Ahora bien, dentro de los procesos existen unidades más pequeñas de ejecución: los **hilos** (o *threads*). Los hilos comparten la memoria y los recursos del proceso padre, lo que los hace más ligeros y rápidos de crear. Pero justamente porque comparten todo, pueden chocar entre sí. Si dos hilos modifican la misma variable al mismo tiempo sin coordinación, aparece un fenómeno temido en programación concurrente: la **condición de carrera**.

En contraste, los procesos no corren ese riesgo, porque cada uno vive en su propio espacio aislado. La tabla siguiente lo resume:

| Característica      | Proceso                          | Hilo                                   |
| ------------------- | -------------------------------- | -------------------------------------- |
| Memoria             | Aislada entre procesos           | Compartida entre hilos                 |
| Creación            | Más costosa                      | Más liviana                            |
| Comunicación        | Requiere IPC (pipes, sockets...) | Directa mediante variables compartidas |
| Tolerancia a fallos | Alta (aislamiento)               | Baja (un error puede colapsar todo)    |

Esta diferencia hace que los hilos sean útiles cuando necesitamos **velocidad de comunicación** y los procesos resulten más apropiados cuando buscamos **aislamiento y seguridad**.

---

### 2. Python y el desafío del GIL

Python, pese a ser uno de los lenguajes más populares para aprender y trabajar en ciencia de datos o automatización, esconde un detalle arquitectónico: el **Global Interpreter Lock (GIL)**.

El GIL funciona como un “candado global” que impide que dos hilos de un mismo proceso ejecuten código Python al mismo tiempo en diferentes núcleos. Esto significa que, aunque una computadora tenga varios procesadores, los hilos de Python no pueden aprovecharlos en paralelo para tareas intensivas en CPU.

Para entenderlo mejor: si tenemos una tarea como calcular millones de raíces cuadradas o procesar imágenes, los hilos en Python no podrán paralelizar realmente ese trabajo. Se turnarán, uno por vez, bajo la vigilancia del GIL.

Aquí es donde entra en juego la librería `multiprocessing`. A diferencia de los hilos, esta crea **procesos independientes**, cada uno con su propio intérprete de Python y, por lo tanto, sin GIL que los limite. De este modo, Python puede finalmente aprovechar todos los núcleos de la CPU.

#### Ventajas del enfoque con procesos:

* Se evita el GIL: hay verdadero paralelismo.
* Cada proceso tiene su propia memoria, reduciendo riesgos de corrupción.
* La caída de un proceso no arrastra a los demás.

#### Desventajas:

* La comunicación entre procesos es más costosa (requiere mecanismos explícitos como pipes o colas).
* Se consume más memoria, porque cada proceso mantiene su propio espacio.
* Para pasar datos de uno a otro hay que **serializarlos**, lo que introduce sobrecarga.

---

### 3. Creación y ciclo de vida de un proceso en Python

La clase `multiprocessing.Process` es la puerta de entrada para crear procesos en Python. Pensemos en ella como un molde: con él fabricamos procesos hijos que ejecutan funciones específicas.

Un ejemplo mínimo sería:

```python
from multiprocessing import Process

def saludo():
    print("Hola desde otro proceso")

if __name__ == '__main__':
    p = Process(target=saludo)
    p.start()
    p.join()
```

Aquí ocurre lo siguiente:

1. Se crea el objeto `Process` con la función `saludo` como tarea.
2. Al llamar a `start()`, nace un nuevo proceso independiente que corre la función.
3. `join()` obliga al programa principal a esperar hasta que el hijo termine.

Cada proceso tiene un **pid** (identificador único) y puede conocer a su padre (`ppid`). Así se forman árboles de procesos, donde uno puede tener varios hijos que cooperan para resolver una tarea.

---

### 4. Comunicación entre procesos

Una vez que tenemos varios procesos corriendo, necesitamos que hablen entre ellos. Aquí entra el **IPC (Inter-Process Communication)**.

Python ofrece dos mecanismos básicos:

#### Pipes

Un `Pipe` conecta dos extremos. Lo que uno envía, el otro recibe.

```python
from multiprocessing import Pipe

parent_conn, child_conn = Pipe()
parent_conn.send("hola")
print(child_conn.recv())
```

El pipe es rápido y simple, pero solo conecta a dos procesos.

#### Queues

Las **colas** (`Queue`) funcionan como buzones compartidos: un proceso puede dejar datos y otro recogerlos más tarde.

```python
from multiprocessing import Queue

q = Queue()
q.put("dato")
print(q.get())
```

A diferencia de los pipes, las colas permiten múltiples productores y consumidores, y son más seguras en escenarios con concurrencia compleja.

**Resumen:**

* Pipes: simples, ideales para dos procesos.
* Queues: más flexibles y seguras, aunque con algo más de sobrecarga.

---

### 5. Sincronización y condiciones de carrera

Cuando varios procesos trabajan con un mismo recurso (un archivo, una variable compartida), existe el riesgo de que lo hagan **simultáneamente** y se produzcan inconsistencias.

Un ejemplo típico sería un contador global. Si dos procesos lo incrementan a la vez, ambos podrían leer el mismo valor inicial y sobrescribir el resultado, perdiendo incrementos.

Para evitarlo se usan mecanismos de **sincronización**, siendo el más básico el **Lock**.

```python
from multiprocessing import Lock

lock = Lock()

with lock:
    # Sección crítica protegida
```

El lock actúa como un semáforo: solo un proceso puede entrar a la zona crítica a la vez. Así se previenen las condiciones de carrera.

---

### 6. Ejemplo práctico: trabajo en paralelo

Supongamos que tenemos un programa `mp_worker.py` que realiza tareas pesadas de CPU, como calcular números primos o aplicar filtros a imágenes. Si lo corremos secuencialmente, un único núcleo hará todo el trabajo.

En cambio, al crear varios procesos con `multiprocessing.Process`, cada núcleo puede tomar parte de la carga. El resultado: un tiempo de ejecución mucho menor.

Este tipo de pruebas nos permite comprobar, en la práctica, que Python con `multiprocessing` logra un paralelismo real en máquinas multi-core.

---

### Conclusiones

La programación concurrente en Python exige comprender sus particularidades:

* Los hilos son útiles para tareas de entrada/salida (I/O-bound), pero se ven limitados en cálculos intensivos por el GIL.
* El módulo `multiprocessing` abre la puerta al verdadero paralelismo, a costa de mayor complejidad en la comunicación y consumo de recursos.
* Pipes y Queues ofrecen soluciones prácticas para el intercambio de datos, mientras que los Locks permiten sincronización segura.

