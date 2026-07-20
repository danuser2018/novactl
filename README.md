# novactl

`novactl` es la herramienta de línea de comandos (CLI) oficial del ecosistema Nova. Su objetivo principal es permitir la interacción estandarizada desde el entorno del sistema operativo (scripts de usuario, atajos de teclado, botones físicos y componentes externos) con el ecosistema de microservicios de Nova mediante la emisión de comandos estructurados a través del bus de eventos NATS (`nova-event-bus`).

## Requisitos e Instalación

### Requisitos previos
- Python 3.10 o superior.
- Librería `nova-event-bus` instalada o disponible en el entorno Python.

### Instalación local en modo desarrollo
Para instalar `novactl` en el entorno actual y disponer del ejecutable en el `PATH`:

```bash
pip install -e .
```

O instalando las dependencias completas de desarrollo:

```bash
pip install -e .[dev]
```

## Comandos Disponibles (v1)

- **`novactl version`**
  Muestra la versión instalada de `novactl` (ejemplo: `novactl 1.0.0`).

- **`novactl help [comando]`**
  Muestra la ayuda general de la CLI o la ayuda específica de un subcomando.

- **`novactl start-capture [--channel voice]`**
  Solicita el inicio de captura de audio/voz. Publica un evento `StartSpeechCaptureCommand` en la parte del bus correspondiente (`novactl.command.start_speech_capture`).

- **`novactl stop-capture [--channel voice]`**
  Solicita la detención de captura de audio/voz. Publica un evento `StopSpeechCaptureCommand` en `novactl.command.stop_speech_capture`.

- **`novactl execute <shortcut> [--channel voice]`**
  Solicita la ejecución de una acción directa o atajo (ej. `novactl execute volume-up`). Publica un evento `ExecuteShortcutCommand` en `novactl.command.execute_shortcut`.

## Arquitectura de Plugins

`novactl` utiliza una arquitectura extensible basada en plugins para la definición de sus comandos. Cada subcomando es una clase aislada que hereda de `CommandPlugin` (`novactl.interface.CommandPlugin`).

### Creación de un nuevo plugin de comando

1. Crea un fichero en `src/novactl/plugins/mi_comando_plugin.py`.
2. Hereda de `CommandPlugin` e implementa la interfaz requerida:

```python
import argparse
from typing import Optional
from novactl.interface import CommandPlugin
from nova_event_bus import EventBusInterface

class MiComandoPlugin(CommandPlugin):
    @property
    def name(self) -> str:
        return "mi-comando"

    @property
    def description(self) -> str:
        return "Descripción de mi comando."

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--opcion", type=str, help="Opción de ejemplo")

    async def execute(self, args: argparse.Namespace, event_bus: Optional[EventBusInterface] = None) -> int:
        # Lógica del comando y publicación de eventos
        return 0
```

3. Registra el plugin en `PluginManager.load_builtin_plugins()`.

## Configuración de Mensajería

`novactl` interactúa con el bus mediante la librería `nova-event-bus`, la cual lee por defecto las siguientes variables de entorno:

- `NATS_URL`: URL del broker NATS (por defecto: `nats://localhost:4222`).

## Ejecución de Tests

Para ejecutar la suite de pruebas unitarias e integración con reporte de cobertura:

```bash
pytest --cov=src/novactl --cov-report=term-missing tests/
```
