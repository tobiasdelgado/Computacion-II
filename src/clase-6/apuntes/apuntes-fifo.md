# FIFOs en Sistemas Unix/Linux: Fundamentos, Implementación y Aplicaciones Avanzadas

## Introducción

En el universo Unix/Linux, la comunicación entre procesos —conocida como _Inter-Process Communication_ o IPC— constituye uno de los cimientos sobre los que se construye la robustez de estos sistemas operativos. Entre los diversos mecanismos de IPC disponibles, los _FIFOs_ (First-In, First-Out), también llamados _named pipes_, destacan por ofrecer un canal de comunicación sencillo, eficiente y persistente.

Los FIFOs permiten que procesos no necesariamente relacionados (es decir, que no provienen de un mismo `fork`) puedan intercambiar información a través de un archivo especial en el sistema. Así, se convierten en un puente entre programas, scripts o demonios que necesitan coordinarse sin depender de una infraestructura compleja.

En este apunte exploraremos su origen histórico, su implementación en el kernel, su funcionamiento práctico en Python y, además, veremos cómo emplear herramientas más avanzadas como `select()` y `poll()` para gestionar múltiples FIFOs de manera simultánea.

---

## 1. Fundamentos Teóricos

### 1.1 Comunicación entre procesos: el panorama general

La comunicación entre procesos surge de la necesidad de que los programas no trabajen en aislamiento. Un sistema moderno rara vez es un conjunto de tareas solitarias: lo usual es que los procesos deban cooperar, compartir datos o coordinar sus acciones.

Unix ofrece diversas técnicas para ello: _pipes anónimos_, _FIFOs_, _memoria compartida_, _colas de mensajes_, _semaforización_, entre otros. La elección depende del nivel de complejidad, de la necesidad de persistencia y de los requisitos de sincronización.

### 1.2 El modelo FIFO

Un FIFO es un archivo especial que implementa la política _primero en entrar, primero en salir_. Esto significa que el primer byte escrito es el primero en ser leído, garantizando un flujo ordenado.

La diferencia fundamental con un _pipe anónimo_ es que un FIFO tiene una entrada visible en el sistema de archivos. Esto lo hace accesible a procesos no relacionados, siempre que tengan permisos adecuados. Además, puede sobrevivir a la finalización de los programas, lo cual lo convierte en un mecanismo más persistente y flexible.

---

## 2. Contexto Histórico

En los años setenta, los primeros sistemas Unix ya incluían _pipes_, pero estos solo podían usarse entre procesos emparentados (padre-hijo). Esto limitaba mucho su aplicación. Con la llegada de los _named pipes_ en **Unix System III** y luego en **System V**, se amplió el paradigma: ahora cualquier proceso podía abrir un canal común en el sistema de archivos y enviar o recibir información.

Ese avance, aunque pequeño en apariencia, permitió arquitecturas de software mucho más modulares. Por ejemplo, un demonio podía escuchar eventos de distintos programas sin necesidad de compartir un ancestro común.

---

## 3. Arquitectura Interna de los FIFOs

Cuando se crea un FIFO, el kernel lo trata como un archivo especial. En realidad, está respaldado por una estructura `inode` y gestionado por un buffer circular en memoria del kernel.

- **Buffer interno:** los datos no se escriben en disco, sino en memoria, en una cola circular.
    
- **Sincronización:** si un proceso intenta leer un FIFO vacío, quedará bloqueado hasta que llegue información. Del mismo modo, si un proceso escribe y no hay lector, quedará esperando.
    
- **No persistencia de datos:** una vez leídos, los datos desaparecen. A diferencia de un archivo tradicional, el FIFO no conserva histórico: es solo un flujo en tránsito.
    

Los tamaños de estos buffers y sus políticas de espera se configuran a nivel de sistema, y el kernel utiliza colas de espera (_wait queues_) para coordinar accesos.

---

## 4. Operaciones Fundamentales

### 4.1 Creación de un FIFO

La creación se hace con el comando `mkfifo` o con la llamada al sistema:

```bash
$ mkfifo /tmp/mi_fifo
```

Ese archivo ahora aparece en el sistema como un archivo especial. Puede ser abierto en modo lectura o escritura por cualquier proceso.

### 4.2 Lectura y escritura en Python con `os`

Ejemplo de escritura:

```python
# escritor.py
import os
fd = os.open('/tmp/mi_fifo', os.O_WRONLY)
os.write(fd, b'Hola desde el escritor\n')
os.close(fd)
```

Ejemplo de lectura:

```python
# lector.py
import os
fd = os.open('/tmp/mi_fifo', os.O_RDONLY)
data = os.read(fd, 1024)
print("Lectura:", data.decode())
os.close(fd)
```

Si no existe un lector al abrir en modo escritura (o viceversa), el proceso quedará bloqueado. Para evitarlo, puede usarse la bandera `O_NONBLOCK`.

### 4.3 Datos consumibles

En un FIFO los datos no se acumulan indefinidamente: una vez que se leen, desaparecen. Esto lo convierte en un mecanismo de flujo, no de almacenamiento.

---

## 5. Select y Poll: Multiplexando FIFOs

Hasta aquí hemos trabajado con un FIFO a la vez. Pero ¿qué sucede cuando un programa debe escuchar múltiples fuentes al mismo tiempo? Un ejemplo clásico es un servidor que recibe mensajes de distintos clientes mediante varios FIFOs.

Leer secuencialmente cada FIFO sería ineficiente. Aquí entran en juego dos llamadas del sistema: `select()` y `poll()`.

### 5.1 `select()`

`select()` permite vigilar varios descriptores de archivo a la vez. Se le entrega un conjunto de descriptores de lectura, escritura y excepciones, y la función bloquea hasta que alguno esté listo.

Ejemplo en Python:

```python
import os, select

# Suponiendo que ya existen varios FIFOs
fifos = ['/tmp/f1', '/tmp/f2']
fds = [os.open(f, os.O_RDONLY | os.O_NONBLOCK) for f in fifos]

while True:
    rlist, _, _ = select.select(fds, [], [])
    for fd in rlist:
        data = os.read(fd, 1024)
        if data:
            print(f"Mensaje desde {fd}: {data.decode().strip()}")
```

Aquí, `select()` bloquea hasta que al menos uno de los FIFOs tenga datos. Así, el programa no desperdicia CPU con bucles de espera activa.

### 5.2 `poll()`

`poll()` cumple un propósito similar, pero con una interfaz más flexible: permite asociar eventos específicos a cada descriptor y manejar miles de ellos con mayor eficiencia.

Ejemplo en Python:

```python
import os, select

fifos = ['/tmp/f1', '/tmp/f2']
fds = [os.open(f, os.O_RDONLY | os.O_NONBLOCK) for f in fifos]

poller = select.poll()
for fd in fds:
    poller.register(fd, select.POLLIN)

while True:
    events = poller.poll()  # Espera indefinidamente
    for fd, event in events:
        if event & select.POLLIN:
            data = os.read(fd, 1024)
            if data:
                print(f"poll: {data.decode().strip()}")
```

La ventaja de `poll()` sobre `select()` es su escalabilidad. Mientras que `select()` tiene un límite en el número de descriptores que puede manejar (FD_SETSIZE), `poll()` permite registrar prácticamente cualquier cantidad.

En aplicaciones modernas, como servidores de alta concurrencia o sistemas embebidos con múltiples sensores, `poll()` resulta la herramienta adecuada.

---

## 6. Patrones de Implementación

1. **Productor-consumidor:** un proceso genera datos y otro los consume.
    
2. **Comunicación unidireccional:** un FIFO para cada sentido de transmisión.
    
3. **Comunicación bidireccional:** dos FIFOs, uno para ida y otro para vuelta.
    

El uso de `select()` o `poll()` permite, además, construir _multiplexores_ que recolectan información desde múltiples fuentes y la centralizan en un proceso monitor.

---

## 7. Comparación con Otros Mecanismos IPC

- **Pipes anónimos:** más simples, pero solo entre procesos relacionados.
    
- **FIFOs:** más flexibles y persistentes, con integración al sistema de archivos.
    
- **Sockets:** más potentes, soportan redes y mayor complejidad de protocolos.
    

---

## 8. Rendimiento y Consideraciones

El rendimiento de un FIFO depende del tamaño del buffer, la velocidad de los procesos y el scheduler del sistema. El uso de `select()` o `poll()` es clave para evitar consumo innecesario de CPU y para gestionar gran cantidad de canales simultáneamente.

---

## 9. Ejemplos Prácticos

- **Sistema de logging:** múltiples procesos escriben mensajes en un FIFO central que otro proceso vuelca a un archivo de log.
    
- **Chat en consola:** dos terminales, dos FIFOs (`fifo_in` y `fifo_out`), permiten un diálogo en tiempo real.
    
- **Multiplexor de sensores:** varios drivers de hardware escriben en FIFOs distintos, y un programa central usa `poll()` para recolectar y procesar datos.
    

---

## 10. Seguridad

Como cualquier archivo, un FIFO obedece a los permisos POSIX. Es fundamental establecerlos correctamente, pues de lo contrario cualquiera podría escribir mensajes falsos o leer información sensible. Además, conviene eliminarlos (`unlink()`) cuando ya no se necesiten, para evitar que queden accesibles.

---

## Conclusión

Los FIFOs son un ejemplo perfecto de cómo Unix, fiel a su filosofía de “todo es un archivo”, ofrece mecanismos simples que resuelven problemas complejos. Aunque hoy en día existen alternativas más sofisticadas como colas de mensajes, _message brokers_ o sockets de red, los FIFOs siguen siendo insustituibles en ciertos escenarios: son ligeros, ubicuos, y permiten aprender los fundamentos de la comunicación concurrente.

Comprender a fondo su funcionamiento, junto con herramientas como `select()` y `poll()`, no solo es útil para programar en Unix/Linux, sino también para desarrollar la mentalidad de ingeniero de sistemas: saber cómo coordinar procesos, optimizar recursos y construir arquitecturas fiables sobre cimientos sencillos.
