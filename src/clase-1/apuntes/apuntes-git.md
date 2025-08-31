# **Control de Versiones con Git**

## **Capítulo 1: Historia del Control de Versiones y la Revolución de Git**

Al principio, cuando los programadores trabajaban en equipo, no había un “control de versiones” formal. Cada uno guardaba copias del código con nombres como *programa\_v1.c*, *programa\_final.c*, *programa\_final\_bueno.c*, etc. Imaginate el desorden: nadie sabía cuál era la última versión ni quién había cambiado qué.

Después, para resolver ese caos, aparecieron los primeros **sistemas de control de versiones**:

* **SCCS y RCS**: Guardaban los cambios en los archivos, pero todavía eran bastante limitados.
* **CVS**: Dio un paso adelante porque ya permitía que varias personas trabajaran a la vez sobre el mismo proyecto.

Hasta ahí todo bien, pero había un problema: **estos sistemas eran centralizados**. Eso significa que todo dependía de un **servidor central**, como si fuera “el jefe” del proyecto. Si ese servidor se caía, nadie podía trabajar. Además, si no estabas conectado a internet, era muy difícil colaborar. Ejemplos: **Subversion (SVN)** y **Perforce**.

---

Entonces llega el **gran cambio con Git en 2005**. Todo empieza porque el kernel de Linux usaba un sistema llamado **BitKeeper**, que era distribuido pero no libre. Cuando les sacaron la licencia, Linus Torvalds dijo: “Bueno, hagamos el nuestro”. Y nació Git.

Git cambió las reglas del juego por varias razones:

1. **Distribuido**: cada programador tiene en su computadora una copia *completa* del proyecto, con todo el historial. O sea, no dependés de un servidor para trabajar.
2. **Snapshots en lugar de diferencias**: mientras los viejos sistemas guardaban “qué cambió” de una versión a otra, Git guarda el estado completo de los archivos cada vez (aunque internamente optimiza el espacio).
3. **Seguro**: cada cambio se guarda con una especie de “huella digital” (hash), lo que hace casi imposible corromper el historial sin que se note.

---

👉 Entonces, la diferencia principal es:

* **Antes (Sistemas Centralizados)**: dependías de un servidor central, era más frágil y menos flexible.
* **Ahora (Git)**: cada programador tiene una copia completa del proyecto, podés trabajar offline, colaborar de forma más libre y segura, y el sistema es mucho más rápido y confiable.


## **Capítulo 2: Fundamentos de Git y su Arquitectura Interna**

Git opera bajo un modelo distribuido, donde cada desarrollador mantiene una copia completa del repositorio. Para entender su funcionamiento, es esencial conocer los siguientes conceptos:

- **Repositorio (`.git/`)**: Contiene toda la información del proyecto, incluyendo commits, ramas y referencias.
- **Área de trabajo (Working Directory)**: La carpeta donde se encuentran los archivos en su versión actual.
- **Área de preparación (Staging Area o Index)**: Un espacio intermedio donde se almacenan cambios antes de confirmarlos.
- **Commit**: Un snapshot de los archivos en un punto determinado del tiempo.
- **Branch (rama)**: Una línea de desarrollo separada del historial principal.
- **Remote Repository**: Repositorios alojados en servidores como GitHub, GitLab o Bitbucket.

**Cómo guarda la información Git?**

Los sistemas viejos guardaban solo las diferencias (“qué cambió de una versión a otra”).
Git hace algo distinto:

* Guarda una **foto completa (snapshot)** del proyecto en cada commit.
* Si algo no cambió, no repite el archivo: simplemente apunta a la versión anterior.
* Cada commit está protegido con una “huella digital” (un hash), lo que hace que sea muy difícil corromper el historial sin que se note.

**Como trabajamos con git?**

Git es flexible y deja que cada equipo trabaje como quiera:

* **Centralizado** → todos trabajan sobre una sola rama principal, parecido a los sistemas viejos.
* **Feature Branching** → cada nueva idea o función se prueba en una rama aparte, y si funciona, se junta con la principal.
* **Git Flow** → un sistema más formal: hay ramas para desarrollo, ramas para nuevas funciones, ramas para sacar versiones, y ramas rápidas para arreglar errores urgentes.
* **Forking Workflow** → muy usado en proyectos abiertos: cada colaborador hace una copia completa del proyecto (un “fork”), trabaja ahí y después manda sus cambios al proyecto original.
