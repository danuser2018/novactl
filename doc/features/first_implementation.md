# novactl - Especificación funcional

## Objetivo

`novactl` es la interfaz de línea de comandos oficial de Nova.

Su responsabilidad es permitir que aplicaciones del sistema operativo interactúen con el ecosistema Nova mediante el envío de comandos.

`novactl` sustituirá progresivamente a los scripts de integración actuales (`mic-start`, `mic-stop`, etc.), proporcionando una API estable y extensible para cualquier componente externo.

---

# Objetivos de diseño

- Proporcionar una interfaz CLI estable para Nova.
- Desacoplar el sistema operativo de la implementación del bus de mensajería.
- Centralizar la publicación de comandos.
- Facilitar la automatización desde scripts, atajos de teclado y otros procesos.
- Permitir la incorporación de nuevos comandos sin modificar el núcleo de la aplicación.

---

# Arquitectura

`novactl` se implementará como una aplicación basada en plugins.

Cada comando será un plugin independiente.

```
novactl
        │
        ├── version
        ├── help
        ├── start-capture
        ├── stop-capture
        └── execute
```

El ejecutable únicamente será responsable de:

- descubrir los plugins disponibles;
- resolver el comando solicitado;
- delegar la ejecución en el plugin correspondiente.

Toda la lógica funcional residirá en los plugins.

---

# Comandos disponibles (v1)

## version

Muestra la versión instalada de `novactl`.

Ejemplo:

```bash
novactl version
```

---

## help

Muestra la ayuda general o la ayuda específica de un comando.

Ejemplo:

```bash
novactl help
```

```bash
novactl help execute
```

---

## start-capture

Publica el comando:

```
StartSpeechCaptureCommand
```

Contexto inicial:

- correlationId
- channel

Canal por defecto:

```
voice
```

---

## stop-capture

Publica el comando:

```
StopSpeechCaptureCommand
```

Contexto inicial:

- correlationId
- channel

Canal por defecto:

```
voice
```

---

## execute

Solicita la ejecución directa de una acción de Nova sin necesidad de reconocimiento de voz.

Ejemplos:

```bash
novactl execute time
```

```bash
novactl execute volume-up
```

El comando publicará:

```
ExecuteShortcutCommand
```

incluyendo:

- correlationId
- channel
- shortcut

---

# Arquitectura de plugins

Cada comando implementará una interfaz común.

Responsabilidades del plugin:

- validar parámetros;
- construir el comando correspondiente;
- delegar su publicación mediante la librería `nova-messaging`.

Los plugins no conocerán la tecnología de mensajería utilizada.

---

# Dependencias

- nova-messaging

`novactl` utilizará exclusivamente la API pública de `nova-messaging`.

No contendrá código específico de NATS.

---

# Instalación

`novactl` se instalará como ejecutable del sistema operativo durante la instalación de Nova.

Debe quedar disponible en el PATH del usuario.

Ejemplo:

```bash
$ novactl version
novactl 1.0.0
```

---

# Evolución prevista

En futuras versiones podrán añadirse nuevos comandos como:

- status
- diagnostics
- publish
- subscribe
- devices
- plugins
- goals

La incorporación de nuevos comandos no requerirá modificaciones en el núcleo de `novactl`, únicamente la implementación de un nuevo plugin.