### Capítulo 3: Entrada y Salida en Unix/Linux 

**3.1 Todo es un archivo**
En Unix y Linux, absolutamente todo se trata como si fuera un archivo: un documento, un teclado, un mouse, un disco, incluso la red. Eso significa que leer de un teclado o leer de un archivo sigue las mismas reglas.

Cuando un programa corre, siempre tiene 3 canales abiertos:

* **`stdin` (entrada estándar, nº 0):** de dónde el programa recibe datos (normalmente el teclado).
* **`stdout` (salida estándar, nº 1):** dónde el programa muestra resultados (normalmente la terminal).
* **`stderr` (salida de error, nº 2):** un canal separado para mensajes de error, así no se mezclan con los resultados normales.

---

**3.2 Descriptores de archivo**

Un **descriptor de archivo** es un **número que identifica un recurso abierto** (archivo, dispositivo, socket, etc.) dentro de un proceso. Es como un ticket que el kernel asigna para referirse al recurso de manera uniforme.

#### Los 3 descriptores básicos

Cuando arrancás un proceso, siempre tiene estos descriptores:

* `0` → stdin (entrada, normalmente teclado)
* `1` → stdout (salida, normalmente pantalla)
* `2` → stderr (errores, normalmente pantalla también)

#### Tabla de descriptores por proceso

Cada programa tiene **su propia tabla de descriptores**, con números que apuntan a sus recursos abiertos. Esto significa que **los números 0, 1 y 2 se repiten en cada proceso**, pero cada uno apunta a su propio teclado, pantalla o archivo.

**Ejemplo narrativo:**

* Vos y tu amigo tienen cada uno una libreta (tabla de descriptores).
* En la hoja nº 0 anotás: “mi entrada es el teclado”.
* En la hoja nº 1 anotás: “mi salida es la terminal”.
* En la hoja nº 2 anotás: “mis errores van a la terminal”.
* Tu amigo tiene su libreta con hojas 0, 1 y 2 también, pero puede apuntar a otras cosas, como un archivo.

**Ejemplo práctico en Linux:**

```sh
echo "hola"
echo "hola" > salida.txt
```

* En el primer caso, el descriptor 1 (stdout) apunta a la pantalla.
* En el segundo, el descriptor 1 apunta al archivo `salida.txt`. Otro proceso en paralelo sigue apuntando a su propia pantalla.

Además de los 0, 1 y 2, cada archivo que abras recibe el siguiente descriptor libre (3, 4, 5, …), y todos se manejan en la **tabla privada de cada proceso**.


---

**3.3 Redirección (cambiar entradas/salidas)**

La redirección permite **cambiar la fuente o destino de datos de un programa** sin modificar su código.

#### Redirección de salida (`>`, `>>`)

* `>` → redirige stdout (descriptor 1) a **cualquier descriptor de archivo**, que puede ser:

  * Un archivo en disco (`salida.txt`)
  * Un dispositivo especial (`/dev/null`)
  * Un proceso o pipe (`>(grep ".txt")`)

```sh
ls > lista.txt     # stdout va a un archivo
ls > /dev/null     # stdout se descarta
```

* `>>` → igual que `>`, pero **agrega** al final del destino sin sobrescribirlo.

#### Redirección de entrada (`<`)

* `<` → redirige stdin (descriptor 0) desde **cualquier flujo de datos**, que puede ser:

  * Un archivo en disco
  * Un dispositivo especial
  * Un pipe o proceso

```sh
wc -l < archivo.txt   # stdin toma datos del archivo
```

El programa no sabe la diferencia: sigue leyendo desde stdin, pero ahora stdin proviene de otra fuente.

#### Redirección de errores (`2>`, `2>>`, `&>`)

* `2>` → redirige stderr a un destino (archivo, dispositivo, etc.).
* `2>>` → agrega errores al destino sin sobrescribirlo.
* `&>` → redirige stdout y stderr juntos.

```sh
comando_inexistente 2>/dev/null  # errores descartados
script.sh &> salida.log           # salida y errores juntos
```

---

**3.4 Pipes (`|`)**
Un **pipe** (`|`) conecta programas entre sí. Lo que uno escribe en su salida, el otro lo recibe como entrada.

Ejemplo:

```sh
ls -l | grep ".txt" | wc -l
```

1. `ls -l` → lista archivos con detalle.
2. `grep ".txt"` → filtra solo los que terminan en `.txt`.
3. `wc -l` → cuenta cuántos son.

Es como una cadena de montaje: cada comando hace su parte y pasa el resultado al siguiente.

---

**3.5 Dispositivos especiales en `/dev/`**
En la carpeta `/dev/` viven “archivos especiales” que representan dispositivos:

* `/dev/null` → el agujero negro: todo lo que va ahí desaparece.
* `/dev/zero` → fuente infinita de ceros (útil para llenar archivos o discos de prueba).
* `/dev/random` y `/dev/urandom` → generan números aleatorios.
* `/dev/tty` → representa tu terminal actual.

Ejemplo:

```sh
cat archivo.txt > /dev/null
```

Esto lee el archivo pero tira la salida al agujero negro, así que no ves nada en pantalla.
