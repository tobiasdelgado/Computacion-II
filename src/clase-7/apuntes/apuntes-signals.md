# Señales en Sistemas Operativos: Comunicación Asíncrona entre Procesos

Imagina que un proceso en ejecución es como una persona concentrada en leer un libro. De pronto, alguien lo toca en el hombro para avisarle algo importante: esa interrupción inesperada es, en esencia, lo que representan las **señales en los sistemas operativos**. Se trata de un mecanismo asíncrono mediante el cual el kernel o incluso otro proceso puede interrumpir el flujo de un programa para notificarle la ocurrencia de un evento.

## Fundamentos: ¿Qué es una señal?

Una **señal** no es más que un número entero que tiene un significado estándar definido por POSIX. Aunque parezca simple, detrás de ese entero hay toda una semántica: puede significar que el usuario presionó `Ctrl+C` (`SIGINT`), que un proceso hijo terminó (`SIGCHLD`), o que se intentó acceder a memoria inválida (`SIGSEGV`).

La señal es enviada por el kernel o por otro proceso, y lo que sucede a continuación depende de cómo el programa receptor esté configurado:

* Puede terminar inmediatamente.
* Puede ignorar la señal.
* O puede ejecutar un *manejador de señal*, que es una pequeña función destinada a reaccionar al evento.

Este mecanismo le da al sistema un poder muy particular: los procesos no necesitan estar constantemente “preguntando” si ocurrió algo (como harían con *polling*), sino que simplemente reaccionan cuando el evento sucede.

## Una mirada histórica

Las señales nacieron en los primeros sistemas UNIX como una extensión natural del concepto de interrupción en hardware. Su propósito inicial era gestionar situaciones excepcionales: un hijo terminando, un pipe roto, un error de ejecución. Con el tiempo, fueron adoptadas como un canal general de comunicación, especialmente útil en la línea de comandos y en scripts.

La estandarización POSIX no solo fijó su comportamiento, sino que introdujo las llamadas **señales en tiempo real**, que pueden encolarse y transportar información adicional. Esto les dio un carácter más flexible, aunque siempre conservando su esencia de ser un mecanismo *ligero, inmediato y reactivo*.

## Modelo conceptual de funcionamiento

Cada proceso mantiene dos estructuras internas importantes:

1. **Tabla de señales pendientes**, donde se anotan las señales que llegaron pero aún no se procesaron.
2. **Máscara de señales bloqueadas**, que define qué señales deben esperar antes de interrumpir al proceso.

Cuando llega una señal, el kernel verifica si está bloqueada o no. Si no lo está, interrumpe el flujo normal del programa para ejecutar la acción definida: ya sea la predeterminada (terminar, ignorar, detener, continuar) o el *handler* que el programador haya configurado.

Podemos clasificar las señales en tres tipos:

* **Síncronas**: se producen como consecuencia de la propia ejecución (ej. división por cero → `SIGFPE`).
* **Asíncronas**: provienen del exterior, como un `kill` enviado desde otro proceso.
* **Reales (POSIX)**: una versión más moderna y potente, con colas y datos adjuntos.

## Envío de señales: el “toque en el hombro”

Los sistemas ofrecen varias funciones para enviar señales. Algunas clásicas en C son:

```c
kill(pid, SIGTERM);        // Enviar a otro proceso
raise(SIGINT);             // Enviar a sí mismo
pthread_kill(tid, SIGUSR1);// A un hilo específico
sigqueue(pid, SIGRTMIN, (union sigval){.sival_int=42}); // Con datos extra
```

En la práctica, desde la terminal, todos hemos usado `kill -9 <pid>`, que envía la señal `SIGKILL` para forzar la terminación de un proceso.

## Instalación de manejadores: cómo reaccionar a la señal

Supongamos que queremos que nuestro programa responda de forma especial cuando reciba `SIGUSR1`. Podemos hacerlo con `sigaction()`:

```c
#include <signal.h>
#include <unistd.h>

void handler(int sig) {
    write(1, "Señal capturada\n", 17);
}

int main() {
    struct sigaction sa = {0};
    sa.sa_handler = handler;
    sigaction(SIGUSR1, &sa, NULL);

    while (1) pause(); // espera la señal
}
```

Es importante destacar que los manejadores deben ser **async-signal-safe**: dentro de ellos solo podemos usar funciones seguras, como `write()` o `exit()`. Llamar a `printf()` dentro de un handler puede ser peligroso.

## Bloqueo selectivo: cuando no queremos ser interrumpidos

A veces, necesitamos que ciertas secciones de código no sean perturbadas por señales. Para eso se usan máscaras:

```c
sigset_t mask;
sigemptyset(&mask);
sigaddset(&mask, SIGINT);
pthread_sigmask(SIG_BLOCK, &mask, NULL); // Bloquea SIGINT
```

De este modo, podemos entrar a una sección crítica sabiendo que no seremos interrumpidos.

## Señales y multithreading

En programas con varios hilos, las señales se vuelven más delicadas: POSIX indica que una señal enviada a un proceso puede ser recibida por cualquiera de sus hilos. Por eso, suele ser recomendable centralizar el manejo en un hilo dedicado, que espere con `sigwait()` y despache tareas según corresponda.

## Señales en Python

Python incluye soporte parcial de señales mediante el módulo `signal`. Sin embargo, solo el proceso principal puede recibirlas. Un ejemplo sencillo es:

```python
import signal, time

def handler(signum, frame):
    print(f"Recibida señal: {signum}")

signal.signal(signal.SIGUSR1, handler)
print("Esperando señales...")
while True:
    time.sleep(1)
```

Si desde otra terminal ejecutamos `kill -USR1 <pid>`, veremos el mensaje aparecer.

## Comparando señales con otros mecanismos IPC

Aunque existen alternativas como *pipes*, *sockets* o *memoria compartida*, las señales tienen un lugar único. No son para transmitir grandes volúmenes de datos, sino para notificar eventos de forma inmediata.

| Mecanismo     | Asíncrono | Datos        | Uso principal                       |
| ------------- | --------- | ------------ | ----------------------------------- |
| Señales       | ✓         | Limitado     | Notificación rápida                 |
| Pipes         | ✗         | Flujo amplio | Comunicación continua               |
| Sockets       | ✗         | Ilimitado    | Comunicación entre máquinas         |
| Shared Memory | ✗         | Ilimitado    | Velocidad máxima con sincronización |

## Un ejemplo práctico: sincronización entre padre e hijo

Veamos cómo un padre espera a su hijo mediante una señal:

```python
import os, signal, time, sys

got_signal = False

def handler(signum, frame):
    global got_signal
    print("[PADRE] Señal recibida, procediendo...")
    got_signal = True

signal.signal(signal.SIGUSR1, handler)

pid = os.fork()
if pid == 0:
    # Hijo
    print("[HIJO] Iniciando inicialización...")
    time.sleep(2)
    os.kill(os.getppid(), signal.SIGUSR1)
    print("[HIJO] Señal enviada al padre")
    sys.exit(0)
else:
    print("[PADRE] Esperando señal del hijo...")
    while not got_signal:
        time.sleep(0.1)
    print("[PADRE] Continuando con la ejecución")
```

Aquí, el padre no necesita *preguntar* continuamente al hijo si terminó: simplemente reacciona cuando recibe la señal.

## Señales comunes en la práctica

Entre todas las señales definidas por POSIX, algunas son especialmente importantes en el desarrollo diario. Aquí profundizamos en tres de las más utilizadas:

### **SIGUSR1 y SIGUSR2** (User-defined signals)
- **Números:** SIGUSR1 = 10, SIGUSR2 = 12
- **Propósito:** Son señales **definidas por el usuario** para comunicación personalizada
- **Comportamiento por defecto:** Terminan el proceso
- **Uso típico:**
  - **Comunicación entre procesos relacionados** (padre-hijo, procesos cooperativos)
  - **Recarga de configuración** (muchos demonios usan SIGUSR1 para reload)
  - **Control de estado** (pausar/reanudar, cambiar modo de operación)
  - **Notificaciones personalizadas** entre aplicaciones

#### Ejemplos reales:
```bash
# Nginx: recargar configuración sin parar
kill -USR1 <nginx_pid>

# Apache: rotación de logs
kill -USR1 <apache_pid>

# Procesos personalizados: toggle debug mode
kill -USR2 <mi_proceso_pid>
```

### **SIGTERM** (Termination signal)
- **Número:** 15
- **Propósito:** Solicitar **terminación elegante** del proceso
- **Comportamiento por defecto:** Termina el proceso
- **Uso típico:**
  - **Shutdown limpio** de servicios y aplicaciones
  - **Comando `kill` por defecto** (sin especificar señal)
  - **Scripts de sistema** para parar servicios ordenadamente
  - **Permite cleanup** antes de terminar (cerrar archivos, conexiones, etc.)

#### Ejemplos reales:
```bash
# Estas son equivalentes (SIGTERM es la por defecto)
kill 1234
kill -TERM 1234 
kill -15 1234

# Systemd usa SIGTERM para parar servicios
systemctl stop mi-servicio  # Envía SIGTERM internamente
```

### **Comparación de señales comunes**

| Señal | Número | Propósito | Control del usuario | Uso típico |
|-------|--------|-----------|-------------------|------------|
| SIGUSR1 | 10 | **Personalizada** | Total (define comportamiento) | Reload, toggle features |
| SIGUSR2 | 12 | **Personalizada** | Total (define comportamiento) | Debug mode, custom actions |  
| SIGTERM | 15 | **Terminación elegante** | Puede interceptar para cleanup | Shutdown servicios |
| SIGKILL | 9 | **Terminación forzada** | **No interceptable** | Matar proceso bloqueado |
| SIGINT | 2 | **Interrupción (Ctrl+C)** | Puede interceptar | Cancelar operación |

La clave está en que **SIGUSR1** y **SIGUSR2** no tienen un significado predefinido: es el programador quien decide qué hacer cuando las recibe. Esto las convierte en un canal de comunicación extremadamente flexible para aplicaciones que necesitan coordinarse sin recurrir a mecanismos más complejos.

## Conclusión

Las señales son un mecanismo clásico y poderoso en los sistemas operativos. Aunque hoy existen formas más sofisticadas de comunicación, ninguna reemplaza su simplicidad y eficacia cuando se trata de **notificar eventos urgentes, coordinar procesos o controlar la ejecución desde el terminal**.

Dominar las señales es comprender uno de los pilares más antiguos y elegantes de UNIX: el arte de reaccionar justo en el momento adecuado.

