# Capítulo 1: Fundamentos y Teoría de los Procesos

### 1.1 El concepto de proceso

Dentro del estudio de los sistemas operativos, el término **proceso** se refiere a la unidad fundamental de trabajo. Para entenderlo con claridad, conviene diferenciarlo de un programa. Un programa es un conjunto estático de instrucciones almacenadas en un archivo dentro del disco. Permanece allí de manera pasiva, como una receta escrita en un papel.

Un proceso, en cambio, es la puesta en marcha de ese programa: la receta siendo preparada. Se trata de una **instancia activa en memoria**, que posee recursos asignados y un contexto de ejecución propio. Por esta razón, aunque un mismo programa pueda existir como archivo único en el disco, puede dar lugar a múltiples procesos independientes en ejecución.

Cada proceso mantiene un conjunto de atributos que lo caracterizan. El sistema operativo le asigna un **PID (Process ID)** que lo identifica de manera única, así como un **PPID (Parent Process ID)** que indica qué otro proceso lo creó. También conserva información sobre su **estado**, que puede ser de ejecución, espera, suspensión o incluso un estado “zombi” cuando ha terminado pero aún no ha sido liberado completamente.

El contexto de un proceso incluye estructuras vitales: un **contador de programa**, que señala la próxima instrucción a ejecutar; una **pila (stack)**, donde se almacenan datos temporales como parámetros de funciones o direcciones de retorno; un **segmento de datos**, que conserva variables globales y estáticas; y una tabla de **archivos abiertos**, que le permite interactuar con el sistema de entrada y salida.

El sistema operativo se encarga de coordinar todos estos elementos, garantizando que múltiples procesos puedan coexistir sobre el mismo hardware sin interferirse. Esta tarea no solo busca eficiencia, sino también seguridad y previsibilidad en la ejecución.

### 1.2 El modelo de procesos en UNIX

El diseño de UNIX y de sus descendientes se apoya en un modelo de procesos con una estructura jerárquica. En él, **todo proceso, salvo el primero, es creado por otro**, siguiendo una lógica de herencia.

El núcleo de este modelo reside en dos llamadas al sistema: `fork()` y `exec()`. La primera, `fork()`, permite que un proceso cree una copia de sí mismo. Esta copia es casi idéntica, con su propio espacio de memoria pero replicando el contenido inicial. Ambos procesos —padre e hijo— continúan la ejecución desde el mismo punto, aunque pueden diferenciarse por el valor de retorno de la llamada.

Luego, el proceso hijo puede invocar `exec()`. Con esta operación, sustituye completamente su espacio de memoria por el de un nuevo programa, convirtiéndose así en otra aplicación distinta. La combinación de `fork()` y `exec()` constituye la base de la creación de procesos en UNIX, un mecanismo tan simple como poderoso.

Toda esta jerarquía se organiza en torno a un proceso primordial: `init` en los sistemas tradicionales, o `systemd` en las versiones modernas de Linux. Este proceso es creado directamente por el kernel durante el arranque, y a partir de él se despliega la genealogía completa de procesos del sistema.

Herramientas como `pstree` permiten visualizar esta estructura en forma de árbol, mostrando cómo cada rama se origina en `init` o `systemd`. El modelo, concebido hace más de medio siglo, ha demostrado ser extraordinariamente robusto y sigue siendo la piedra angular en la gestión de procesos de los sistemas tipo UNIX.

# Capítulo 2: Historia y Evolución de la Gestión de Procesos

El concepto de **proceso**, hoy tan central en la informática, no nació de manera inmediata ni evidente. Más bien, fue el resultado de una evolución progresiva de los sistemas operativos, que pasaron de ser simples despachadores de tareas a convertirse en plataformas multitarea complejas y sofisticadas. Esta transformación refleja no solo el avance del hardware, sino también la necesidad creciente de organizar y aprovechar mejor los recursos de cómputo.

### 2.1 Los primeros pasos: sistemas monoprogramados

En las décadas de 1950 y 1960, los sistemas operativos tal como los conocemos no existían. Los primeros computadores —como el ENIAC o el IBM 701— eran operados de manera manual. Los programas se cargaban en memoria a través de tarjetas perforadas o cintas magnéticas, y la máquina ejecutaba una única tarea de principio a fin.

En este contexto, la idea de un “proceso” no tenía lugar. Solo había un programa corriendo y, hasta que no terminaba, no podía iniciarse otro. No existía la noción de identidad, estado o jerarquía en la ejecución.

Con el aumento de la demanda de cómputo, surgieron los **sistemas batch**. Estos permitían agrupar varios trabajos en una cola, que el computador ejecutaba uno tras otro de forma automática. Aunque rudimentario, este esquema introdujo una idea embrionaria de lo que luego sería el proceso: una unidad de ejecución definida, con un inicio, un fin y recursos asociados.

### 2.2 La multiprogramación: el gran salto

El verdadero punto de inflexión llegó con la **multiprogramación**. Este modelo habilitó la coexistencia de varios programas en memoria, compartiendo el procesador mediante turnos de ejecución. El sistema operativo debía decidir qué programa usaría el procesador en cada momento, alternando entre ellos y ofreciendo la sensación de simultaneidad.

Este cambio obligó a diseñar mecanismos de aislamiento de memoria, planificación de la CPU y protección de recursos. Y con ello nació, formalmente, el **proceso moderno**: una entidad independiente, con identidad propia y recursos asignados, capaz de convivir con otros en un mismo sistema sin interferencias.

### 2.3 UNIX y el paradigma fork/exec

Hacia finales de los años 60, los laboratorios Bell de AT\&T desarrollaron **UNIX**, un sistema operativo que marcaría el rumbo de la informática. Entre sus aportes más influyentes se encuentra el modelo de creación de procesos basado en las llamadas al sistema `fork()` y `exec()`.

Con `fork()`, un proceso podía clonar su propio contexto y generar un hijo idéntico, con su propio espacio de memoria. A continuación, mediante `exec()`, ese hijo podía transformarse en un programa completamente distinto, reemplazando su código y datos. Esta separación entre “crear” y “transformar” resultó elegante y poderosa, facilitando la construcción de **shells, servidores y demonios**, y estableciendo un paradigma que perdura hasta hoy.

UNIX también introdujo una visión minimalista en la que “**todo es un archivo**”. Bajo esta lógica, incluso los procesos podían observarse y manipularse a través de interfaces como el directorio virtual `/proc`. Este enfoque simplificó el diagnóstico, la depuración y el control de procesos desde el espacio de usuario, convirtiéndose en un rasgo definitorio de la filosofía UNIX.

### 2.4 Herencia y vigencia en la actualidad

Las ideas forjadas en UNIX sobrevivieron al paso del tiempo y se expandieron a sus descendientes directos, como **Linux**, **FreeBSD** y **macOS**, e incluso influenciaron sistemas distintos, como **Windows**, que adoptó mecanismos equivalentes a través de subsistemas como WSL (Windows Subsystem for Linux).

Con el correr de los años, la gestión de procesos se ha enriquecido con nuevas abstracciones: **hilos (threads)** para permitir concurrencia ligera, **contenedores** mediante namespaces y cgroups en Linux, y esquemas avanzados de **planificación** para aprovechar mejor los recursos en entornos masivos.

Sin embargo, la piedra angular sigue siendo la misma: un proceso como unidad fundamental de ejecución, con identidad, contexto y recursos propios. Incluso en escenarios modernos como la **virtualización** o la **computación en la nube**, donde las capas de abstracción se multiplican, la noción de proceso continúa siendo indispensable.

Esta continuidad histórica evidencia la solidez del diseño original y su extraordinaria capacidad de adaptación. Lo que comenzó como una necesidad de ejecutar varios programas de manera ordenada, se transformó en uno de los pilares conceptuales más perdurables de la informática.

# Capítulo 3: Profundización Técnica sobre el Modelo de Procesos

Entender un proceso no se limita a reconocerlo como un concepto abstracto dentro de los sistemas operativos. También requiere explorar los mecanismos concretos mediante los cuales se crea, se transforma y finalmente desaparece. Este capítulo profundiza en el funcionamiento interno del modelo de procesos, mostrando cómo se materializa en sistemas UNIX y cómo puede observarse desde el punto de vista del programador.

### 3.1 `fork()`: la clonación de procesos

La llamada al sistema `fork()` constituye uno de los pilares del modelo UNIX. Su propósito es sencillo de enunciar: **duplicar el proceso actual para crear uno nuevo**. El proceso original se denomina **padre**, y el recién creado recibe el nombre de **hijo**.

Lo interesante de `fork()` es que, desde el punto de vista del programador, parece retornar dos veces: una en el padre y otra en el hijo. El padre recibe como valor de retorno el identificador (PID) del hijo, mientras que el hijo recibe un 0. Esta dualidad permite distinguir en qué rama de la ejecución nos encontramos y así escribir lógica condicional.

Un ejemplo en Python ilustra este comportamiento:

```python
import os

pid = os.fork()
if pid == 0:
    print("[HIJO] PID:", os.getpid())
else:
    print("[PADRE] PID:", os.getpid(), "→ hijo:", pid)
```

Ambos procesos ejecutan este mismo bloque, pero cada uno lo hace con un rol distinto.

A nivel interno, `fork()` no copia toda la memoria inmediatamente, ya que eso resultaría demasiado costoso. En su lugar, los sistemas modernos emplean una técnica llamada **copy-on-write (COW)**: padre e hijo comparten las mismas páginas de memoria en modo lectura, y solo si alguno de los dos intenta modificarlas se genera una copia real. De esta forma se logra eficiencia sin perder independencia entre procesos.

Otro aspecto importante es la **herencia de recursos**. El hijo conserva las variables de entorno, los descriptores de archivos y el estado general del padre, lo que permite que continúen trabajando con los mismos recursos externos, como sockets o archivos abiertos, aunque sus espacios de memoria sean distintos.

### 3.2 `exec()`: la transformación de procesos

Si `fork()` es la manera de crear un nuevo proceso, la familia de funciones `exec()` constituye el medio para **transformar un proceso en algo completamente distinto**.

Cuando se llama a `exec()`, el proceso actual abandona su programa original y carga en memoria un nuevo ejecutable, sustituyendo su código, sus datos y su punto de inicio. Esto significa que todo lo que viene después de `exec()` en el programa original nunca se ejecuta, ya que el proceso ha cambiado de identidad.

Un ejemplo sencillo muestra cómo un shell implementa este mecanismo:

```python
import os

pid = os.fork()
if pid == 0:
    os.execlp("ls", "ls", "-l")  # El hijo se transforma en "ls -l"
else:
    os.wait()  # El padre espera la finalización del hijo
```

Aquí, el padre crea un hijo con `fork()`, y ese hijo es reemplazado por el comando `ls -l` gracias a `exec()`. El resultado es que el shell nunca ejecuta directamente `ls`, sino que delega en un hijo transformado en ese programa.

La familia `exec` incluye múltiples variantes (`execl`, `execp`, `execv`, `execvp`, entre otras), que se diferencian en cómo reciben los argumentos y la ruta al ejecutable. Esta flexibilidad resulta fundamental para los entornos multitarea.

### 3.3 Procesos zombis y huérfanos

En la vida de los procesos existen también estados peculiares que, aunque indeseados en apariencia, cumplen funciones importantes en la gestión del sistema. Dos de ellos son los **zombis** y los **huérfanos**.

#### Los zombis: procesos que ya no viven, pero tampoco mueren

Un proceso zombi es aquel que ya ha terminado su ejecución, pero cuya información de salida todavía no ha sido recogida por su padre. Aunque no ocupa memoria ni consume CPU, permanece en la tabla de procesos en estado `Z`.

Esto ocurre porque el sistema operativo conserva datos esenciales como el código de salida y el tiempo de CPU consumido, de modo que el padre pueda recuperarlos mediante `wait()` o `waitpid()`. Si el padre nunca lo hace, el zombi se queda allí, acumulándose como una sombra en el sistema.

Un pequeño experimento en Python permite ver un zombi en acción:

```python
import os, time

pid = os.fork()
if pid == 0:
    print("[HIJO] Terminando")
    os._exit(0)
else:
    print("[PADRE] No recolecto al hijo todavía")
    time.sleep(15)  # Durante este tiempo el hijo es zombi
```

Si durante esos segundos se ejecuta `ps -el | grep Z`, podrá observarse el proceso hijo en estado zombi.

#### Los huérfanos: procesos sin padre

Un proceso huérfano, en cambio, surge cuando el padre finaliza antes que el hijo. En sistemas UNIX, este hijo no queda abandonado: automáticamente es **adoptado por el proceso init** (PID 1), o en sistemas modernos por `systemd`. De este modo, alguien se hace responsable de esperar su finalización y evitar zombis residuales.

Otro experimento ilustra el fenómeno:

```python
import os, time

pid = os.fork()
if pid > 0:
    print("[PADRE] Terminando de inmediato")
    os._exit(0)
else:
    print("[HIJO] Mi padre murió, ahora me adopta init")
    time.sleep(10)
```

Durante esos segundos, puede observarse con `ps -o pid,ppid,stat,cmd` que el hijo ya no tiene como padre al proceso original, sino a `init`.

Este comportamiento muestra cómo los sistemas operativos no solo crean procesos, sino que también **aseguran su limpieza y orden**, incluso en escenarios donde los programas terminan de manera abrupta o inesperada.

# Capítulo Extra: El destino de los procesos no recolectados

Cuando un proceso padre llama a **`wait()`**, lo que está diciendo en realidad es:

👉 *“Pausa mi ejecución hasta que alguno de mis hijos termine, y tráeme su información de salida”*.

Eso significa que:

* Si en ese momento **algún hijo ya terminó** y está en estado zombi, entonces `wait()` **no bloquea nada**: inmediatamente devuelve la información de ese hijo y lo elimina de la tabla de procesos.
* Si **ningún hijo ha terminado todavía**, entonces sí: el padre **queda bloqueado** en esa línea de código, suspendido, hasta que uno de sus hijos finalice.

En otras palabras, `wait()` no “espera por esperar”, sino que su función es recolectar el estado de salida de un hijo. Si hay algo pendiente que recolectar, lo hace enseguida; si no, se detiene hasta que lo haya.

📌 Ejemplo narrado:

1. Un proceso padre crea un hijo con `fork()`.

2. Llama inmediatamente a `wait()`.

   * El padre queda detenido hasta que el hijo termine.
   * Cuando el hijo acaba, el padre “despierta”, recibe el código de salida y continúa.

3. Si el hijo hubiera terminado antes de que el padre ejecutara `wait()`, entonces el hijo estaría en estado zombi momentáneamente. En ese caso, al llamar `wait()`, el padre recoge los datos **sin esperar**.

---

Entonces:

* **Sí, `wait()` bloquea** si no hay ningún hijo finalizado.
* **No, `wait()` no bloquea** si ya hay hijos en estado zombi listos para ser recolectados.


En los capítulos anteriores vimos cómo los procesos se crean y finalizan, y también cómo surgen los estados especiales de **zombi** y **huérfano**. Sin embargo, aún queda una pregunta clave: ¿qué sucede cuando el padre de un proceso no se ocupa de sus hijos?

### El padre que no llama a `wait()`

Cuando un proceso hijo finaliza, el sistema operativo conserva su información de salida en la tabla de procesos. Este “registro” espera a ser leído por el padre a través de `wait()` o `waitpid()`.

* Si el padre **sí llama** a `wait()`, el hijo desaparece por completo y libera su entrada.
* Si el padre **no lo hace**, el hijo permanece como **zombi**: ya no ejecuta código, no tiene memoria asignada, pero aún ocupa un espacio en la tabla de procesos.

Este estado puede acumularse si el padre crea muchos hijos y nunca los recolecta. Aunque los zombis no consumen CPU, sí consumen un recurso limitado: los identificadores de proceso (PID).

### Múltiples hijos zombis

Supongamos un escenario donde un proceso padre crea dos hijos, ambos terminan, y el padre nunca los espera. Durante la vida del padre, esos hijos permanecerán como zombis.

Ahora bien, si el padre muere, ocurre algo interesante:

* Los hijos zombis son automáticamente **adoptados por `init` o `systemd`**.
* Este proceso especial llama a `wait()` sobre ellos, liberando las entradas y eliminando los zombis.

Así, el sistema operativo garantiza que ningún zombi pueda quedar “huérfano” indefinidamente.

### ¿Y el padre? ¿También puede ser zombi?

La respuesta es **sí**. Cuando un proceso termina, él mismo se convierte en un zombi hasta que su propio padre lo recoja con `wait()`. La diferencia es que este estado suele ser muy breve, porque la mayoría de los padres bien diseñados realizan esa llamada.

En el caso de que el padre de un proceso no exista más, la misma regla se aplica: el proceso terminado es adoptado por `init/systemd`, que se encarga de recolectarlo. De este modo, la cadena de herencia asegura que siempre exista alguien que limpie los restos.

### Conclusión

El estado de zombi no es un error del sistema, sino un mecanismo necesario para que el padre pueda conocer cómo terminó su hijo. Sin embargo, si el padre ignora esta responsabilidad, los zombis pueden acumularse mientras él viva. Cuando finalmente muere, el sistema operativo transfiere esa tarea a `init/systemd`, que garantiza la limpieza de todos los procesos pendientes.

En resumen:

* Un hijo sin `wait()` se convierte en zombi.
* Si el padre muere, el zombi es adoptado y eliminado por `init/systemd`.
* El propio padre puede ser zombi si su padre no lo espera, pero nunca indefinidamente: el sistema siempre asegura una limpieza final.



