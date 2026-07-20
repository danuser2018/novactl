# Documento de Refinamiento: Primera Implementación de novactl

- **Documento de Origen**: [first_implementation.md](file:///home/danuser2018/workspace/novactl/doc/features/first_implementation.md)
- **Estado**: Refinado / Listo para revisión de DoR

---

## 1. Resumen y Contexto de Negocio

`novactl` es la herramienta oficial de línea de comandos (CLI) del ecosistema Nova. Su propósito principal es permitir que las aplicaciones del sistema operativo, scripts de usuario, atajos de teclado y componentes externos interactúen con Nova de forma estandarizada mediante la emisión de comandos estructurados.

Actualmente, el control de la captura de voz y la ejecución de acciones directas se realiza mediante scripts de integración individuales. `novactl` consolida y sustituirá progresivamente estos scripts (`mic-start`, `mic-stop`, etc.) ofreciendo una CLI modular basada en arquitectura de plugins. Esto desacopla el sistema operativo del bus de eventos subyacente y centraliza la publicación de comandos mediante la librería cliente `nova-event-bus` (que actúa sobre la infraestructura NATS).

---

## 2. Análisis de Servicios e Impacto

| Servicio | Tipo de Cambio | Descripción del Impacto |
| :--- | :--- | :--- |
| `novactl` | **[NEW]** | Creación completa de la herramienta CLI en Python: motor central de CLI, arquitectura modular de plugins (`version`, `help`, `start-capture`, `stop-capture`, `execute`), integración con `nova-event-bus`, suite de tests con `pytest`, configuración del ejecutable en el PATH (`pyproject.toml`), documentación en `README.md` y flujo de integración continua con GitHub Actions. |
| `nova-event-bus` | **Ninguno** | Consumo directo de la librería existente para instanciar el cliente NATS y publicar eventos tipados. |
| `home-assistant` | **[MODIFY]** | Actualización de documentación del sistema y registro del nuevo ADR (`adr-020-integracion-novactl.md`). |
| Otros servicios de Nova | **Ninguno** | Los servicios existentes (`orchestrator`, `stt-capability`, etc.) recibirán los eventos estándar publicados por `novactl` en el bus sin requerir cambios de código. |

---

## 3. Especificación de Comportamiento (Criterios de Aceptación)

### Escenario 1: Consultar versión de novactl
```gherkin
Scenario: Query novactl version
  Given that the novactl executable is installed and available in PATH
  When the user executes "novactl version"
  Then novactl must output the version string "novactl 1.0.0" to standard output
  And the process exit code must be 0
```

### Escenario 2: Solicitar ayuda general y de comando específico
```gherkin
Scenario: Query general and command-specific help
  Given that the novactl executable is installed
  When the user executes "novactl help" or "novactl --help"
  Then novactl must display the list of available commands ("version", "help", "start-capture", "stop-capture", "execute")
  And the process exit code must be 0
  When the user executes "novactl help execute"
  Then novactl must display the specific syntax and flags for the "execute" subcommand
  And the process exit code must be 0
```

### Escenario 3: Iniciar captura de voz mediante start-capture
```gherkin
Scenario: Publish start speech capture command
  Given that novactl is executed with "novactl start-capture"
  And default options are used (channel = "voice")
  When the start-capture plugin executes
  Then it must generate a unique correlationId (UUIDv4)
  And publish a StartSpeechCaptureCommand event to subject "novactl.command.start_speech_capture" via nova-event-bus
  And display a confirmation message with correlationId to standard output
  And exit with status code 0
```

### Escenario 4: Detener captura de voz mediante stop-capture
```gherkin
Scenario: Publish stop speech capture command
  Given that novactl is executed with "novactl stop-capture"
  And default options are used (channel = "voice")
  When the stop-capture plugin executes
  Then it must generate a unique correlationId (UUIDv4)
  And publish a StopSpeechCaptureCommand event to subject "novactl.command.stop_speech_capture" via nova-event-bus
  And display a confirmation message with correlationId to standard output
  And exit with status code 0
```

### Escenario 5: Ejecutar una acción directa mediante execute
```gherkin
Scenario: Execute a direct shortcut action
  Given that novactl is executed with "novactl execute volume-up"
  When the execute plugin executes
  Then it must capture shortcut parameter "volume-up"
  And generate a unique correlationId (UUIDv4)
  And publish an ExecuteShortcutCommand event to subject "novactl.command.execute_shortcut" containing shortcut = "volume-up" and channel = "voice"
  And exit with status code 0
```

### Escenario 6: Comando o subcomando no reconocido
```gherkin
Scenario: Handle invalid or unknown command
  Given that the user executes "novactl unknown-cmd"
  When novactl processes the command-line arguments
  Then it must output an error message to standard error indicating that "unknown-cmd" is not a recognized command
  And display usage guidance
  And exit with a non-zero status code (e.g. status 2)
```

### Escenario 7: Imposibilidad de conectar con el Event Bus (NATS offline)
```gherkin
Scenario: Event bus connection failure
  Given that the NATS broker is unreachable or offline
  When the user executes "novactl start-capture"
  Then novactl must catch the connection timeout exception from nova-event-bus
  And output a user-friendly error message to standard error
  And exit with status code 1 without raising an unhandled stack trace
```

---

## 4. Diseño Técnico y Contratos

### Estructura de Directorios (English)

```text
novactl/
├── README.md                    # Project overview, installation, usage & plugin guidelines
├── CONTRIBUTING.md              # Contribution guidelines
├── CHANGELOG.md                 # Project changelog
├── LICENSE                      # Project license
├── .gitignore                   # Git ignore settings
├── pyproject.toml               # Build system, dependencies & CLI entrypoint configuration
├── requirements.txt             # Project requirements
│
├── .github/
│   └── workflows/
│       └── pr-tests.yml         # GitHub Action workflow for PR automated tests
│
├── doc/
│   ├── features/
│   │   └── first_implementation.md
│   └── refinements/
│       └── first_implementation_refinement.md
│
├── src/
│   └── novactl/
│       ├── __init__.py          # Package initialization (__version__ = "1.0.0")
│       ├── cli.py               # Main CLI parser and application entrypoint
│       ├── interface.py         # Plugin abstract base class definitions
│       ├── plugin_manager.py    # Plugin discovery and loader implementation
│       ├── events.py            # Event dataclasses using nova-event-bus @event decorator
│       └── plugins/             # Core plugin implementations
│           ├── __init__.py
│           ├── version_plugin.py
│           ├── help_plugin.py
│           ├── start_capture_plugin.py
│           ├── stop_capture_plugin.py
│           └── execute_plugin.py
│
└── tests/
    ├── __init__.py
    ├── test_cli.py              # CLI entrypoint and argument parsing tests
    ├── test_plugin_manager.py   # Plugin registry and loading tests
    └── test_plugins.py          # Unit tests for individual command plugins
```

---

## Contratos Lógicos de Clases e Interfaz (English)

### 1. Interfaz de Plugins (`src/novactl/interface.py`)

```python
from abc import ABC, abstractmethod
import argparse
from typing import Any, Dict, Optional
from nova_event_bus import EventBusInterface

class CommandPlugin(ABC):
    """Abstract base class for all novactl command plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the CLI command (e.g. 'start-capture')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Brief description of the command for CLI help messages."""
        pass

    @abstractmethod
    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configures subparser flags and arguments for this command."""
        pass

    @abstractmethod
    async def execute(self, args: argparse.Namespace, event_bus: Optional[EventBusInterface] = None) -> int:
        """
        Executes the command logic.
        Returns process exit status code (0 for success, non-zero for failure).
        """
        pass
```

---

### 2. Definición de Eventos (`src/novactl/events.py`)

```python
from dataclasses import dataclass
from nova_event_bus import Event, event

@event("novactl.command.start_speech_capture")
@dataclass
class StartSpeechCaptureCommand(Event):
    correlation_id: str
    channel: str = "voice"

@event("novactl.command.stop_speech_capture")
@dataclass
class StopSpeechCaptureCommand(Event):
    correlation_id: str
    channel: str = "voice"

@event("novactl.command.execute_shortcut")
@dataclass
class ExecuteShortcutCommand(Event):
    correlation_id: str
    shortcut: str
    channel: str = "voice"
```

---

### 3. Gestor de Plugins (`src/novactl/plugin_manager.py`)

```python
from typing import Dict, List, Type
from novactl.interface import CommandPlugin

class PluginManager:
    """Discovers and manages novactl command plugins."""

    def __init__(self) -> None:
        self._plugins: Dict[str, CommandPlugin] = {}

    def register_plugin(self, plugin: CommandPlugin) -> None:
        """Registers a command plugin instance."""
        self._plugins[plugin.name] = plugin

    def load_builtin_plugins(self) -> None:
        """Loads all standard built-in plugins from novactl.plugins package."""
        pass

    def get_plugin(self, name: str) -> Optional[CommandPlugin]:
        """Retrieves a registered plugin by name."""
        return self._plugins.get(name)

    def get_all_plugins(self) -> List[CommandPlugin]:
        """Returns all registered plugins."""
        return list(self._plugins.values())
```

---

### 4. Punto de Entrada CLI (`src/novactl/cli.py`)

```python
import sys
import argparse
from typing import List, Optional
from novactl.plugin_manager import PluginManager

def build_parser(plugin_manager: PluginManager) -> argparse.ArgumentParser:
    """Constructs the root ArgumentParser and attaches subcommands from registered plugins."""
    pass

def main(argv: Optional[List[str]] = None) -> int:
    """CLI execution entrypoint. Returns exit status code."""
    pass

if __name__ == "__main__":
    sys.exit(main())
```

---

### Configuración del Paquete (`pyproject.toml`)

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "novactl"
version = "1.0.0"
description = "Nova ecosystem Command Line Interface"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "nova-event-bus",
]

[project.scripts]
novactl = "novactl.cli:main"

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=5.0.0",
    "pytest-asyncio>=0.23.0",
]
```

---

### Diseño de la GitHub Action (`.github/workflows/pr-tests.yml`)

```yaml
name: PR Tests

on:
  pull_request:
    branches: [ main, master ]
  push:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .[dev]

      - name: Run Pytest suite
        run: |
          pytest --cov=src/novactl --cov-report=term-missing tests/
```

---

### Estructura de `README.md`

El fichero `README.md` del repositorio debe incluir de forma completa:
1. **Descripción General**: Propósito de `novactl` como CLI oficial de Nova.
2. **Requisitos de Instalación**: Instalación local mediante `pip install -e .` o mediante el instalador del ecosistema.
3. **Comandos Disponibles (v1)**:
   - `novactl version`
   - `novactl help` / `novactl help <command>`
   - `novactl start-capture [--channel voice]`
   - `novactl stop-capture [--channel voice]`
   - `novactl execute <shortcut> [--channel voice]`
4. **Arquitectura de Plugins**: Explicación de cómo añadir nuevos comandos creando clases derivadas de `CommandPlugin`.
5. **Configuración de Mensajería**: Variables de entorno soportadas (p. ej. `NATS_URL`).
6. **Ejecución de Tests**: Instrucciones para ejecutar `pytest`.

---

## 5. Casos de Borde y Manejo de Errores

1.  **Fallo de Conexión NATS / Broker No Disponible**:
    - Si `nova-event-bus` no logra conectarse al broker NATS (ej. por timeout o servicio caído), `novactl` capturará `EventBusError` o `ConnectionError`, emitirá un mensaje explicativo por stderr ("Error: Could not connect to Nova event bus") y saldrá con código de retorno 1.
2.  **Argumentos Faltantes o Inválidos**:
    - Para `execute` sin especificar el parámetro `shortcut`, `argparse` mostrará la sintaxis correcta del subcomando por stderr y finalizará con código 2.
3.  **Generación de Identificador Único (`correlationId`)**:
    - Cada ejecución de comando (`start-capture`, `stop-capture`, `execute`) generará un `correlationId` UUIDv4 aleatorio garantizando la trazabilidad de la petición a través de los microservicios de Nova.
4.  **Ejecución Síncrona vs Asíncrona**:
    - `novactl` es una herramienta CLI efímera. Tras conectar, publicar el evento tipado y realizar el flush en NATS, cerrará limpiamente la conexión y finalizará el proceso inmediatamente sin quedar bloqueado en background.
5.  **Carga de Plugins Inexistentes / Errores en Plugins**:
    - Si la carga de un plugin falla al arrancar por una excepción no controlada, el gestor de plugins capturará el error, registrará un aviso en stderr y continuará registrando los demás plugins válidos.

---

## 6. Estrategia de Testing

- **Tests del Parser CLI y Gestor de Plugins (`tests/test_cli.py` & `tests/test_plugin_manager.py`)**:
  - Verificar que el parser detecta correctamente subcomandos conocidos (`version`, `help`, `start-capture`, `stop-capture`, `execute`).
  - Verificar la respuesta ante argumentos inválidos o flag `--help`.
  - Probar la carga y registro dinámico de plugins.
- **Tests de Plugins de Comandos (`tests/test_plugins.py`)**:
  - Probar `VersionPlugin`: comprobar que la salida formateada coincide con `novactl 1.0.0`.
  - Probar `StartCapturePlugin` y `StopCapturePlugin`: mockear `nova-event-bus`, ejecutar la acción y verificar que se llama a `publish()` pasando las instancias tipadas `StartSpeechCaptureCommand` y `StopSpeechCaptureCommand` con un `correlation_id` válido.
  - Probar `ExecutePlugin`: verificar la correcta asignación del atributo `shortcut` y publicación del evento `ExecuteShortcutCommand`.
  - Probar la gestión de fallos al publicar en el event bus mediante mocks que lanzan excepciones.

---

## 7. Plan de Implementación

- `[ ]` **Tarea 1: Configuración de Proyecto y Dependencias (`pyproject.toml` & `requirements.txt`)**
  - Crear `pyproject.toml` definiendo el paquete `novactl`, dependencias (`nova-event-bus`) y el script de consola `novactl = novactl.cli:main`.
  - Crear `requirements.txt` con las dependencias base y de desarrollo.

- `[ ]` **Tarea 2: Documentación del Repositorio (`README.md`)**
  - Rellenar `README.md` documentando en español la arquitectura del CLI, los comandos de la v1 (`version`, `help`, `start-capture`, `stop-capture`, `execute`), guía de instalación, configuración de NATS y desarrollo de nuevos plugins.

- `[ ]` **Tarea 3: Definición de Interfaces y Dataclasses de Eventos**
  - Crear `src/novactl/interface.py` con la clase abstracta base `CommandPlugin`.
  - Crear `src/novactl/events.py` definiendo `StartSpeechCaptureCommand`, `StopSpeechCaptureCommand` y `ExecuteShortcutCommand` usando el decorador `@event` de `nova-event-bus`.

- `[ ]` **Tarea 4: Gestor de Plugins (`PluginManager`)**
  - Implementar `src/novactl/plugin_manager.py` para el registro y resolución de plugins de comandos.

- `[ ]` **Tarea 5: Plugins de Información (`VersionPlugin` y `HelpPlugin`)**
  - Implementar `src/novactl/plugins/version_plugin.py` para mostrar la versión del CLI.
  - Implementar `src/novactl/plugins/help_plugin.py` para la gestión avanzada de ayuda por comando.

- `[ ]` **Tarea 6: Plugins de Captura de Voz (`StartCapturePlugin` y `StopCapturePlugin`)**
  - Implementar `src/novactl/plugins/start_capture_plugin.py` publicando `StartSpeechCaptureCommand`.
  - Implementar `src/novactl/plugins/stop_capture_plugin.py` publicando `StopSpeechCaptureCommand`.

- `[ ]` **Tarea 7: Plugin de Ejecución Directa (`ExecutePlugin`)**
  - Implementar `src/novactl/plugins/execute_plugin.py` recibiendo el atajo por argumento, aceptando la flag opcional `--channel` (con valor por defecto `"voice"`) y publicando `ExecuteShortcutCommand`.

- `[ ]` **Tarea 8: Punto de Entrada Principal (`cli.py`)**
  - Implementar `src/novactl/cli.py` integrando `argparse`, `PluginManager`, inicialización de `nova-event-bus` y manejo global de excepciones.

- `[ ]` **Tarea 9: Suite de Pruebas Unitarias e Integración (`tests/`)**
  - Crear `tests/test_cli.py`, `tests/test_plugin_manager.py` y `tests/test_plugins.py` asegurando cobertura de tests para todos los comandos y casos de borde.

- `[ ]` **Tarea 10: Integración Continua (GitHub Action Workflow)**
  - Crear `.github/workflows/pr-tests.yml` para ejecutar automáticamente `pytest` con reporte de cobertura en cada Pull Request o Push a la rama principal.

- `[ ]` **Tarea 11: Registro en Changelog**
  - Registrar los cambios de la primera versión en `CHANGELOG.md` bajo la sección `[Sin publicar]`.

- `[ ]` **Tarea 12: Registro de Decisión Arquitectónica (ADR-020) y Sincronización de Referencias**
  - Redactar `docs/adr/adr-020-integracion-novactl.md` en el repositorio `home-assistant` documentando formalmente la arquitectura del CLI `novactl` y su desacoplamiento del bus mediante `nova-event-bus`, tomando como base la propuesta del Anexo.
  - Actualizar la documentación central del sistema en `home-assistant` (`docs/architecture.md` y `docs/services.md`) para registrar `novactl` como la CLI oficial del ecosistema.
  - Sincronizar la sección de `Referencias` en las skills transversales afectadas (`service-responsibilities`, `system-deployment`, `communication-patterns`, `event-driven-architecture` y `feature-refinement`) añadiendo la referencia explícita al nuevo ADR-020.

---

## Anexo: Propuesta de ADR-020

### ADR-020: Integración del CLI novactl y Publicación de Comandos Mediante nova-event-bus

- **Fecha**: 20-07-2026
- **Estado**: Propuesto
- **Contexto**:
  Actualmente, las interacciones desde el entorno de escritorio del sistema operativo Linux (tales como atajos de teclado, botones físicos o scripts de automatización) hacia Nova se realizan invocando scripts individuales en el host (p. ej., `mic-start`, `mic-stop`). Esta aproximación presenta limitaciones de mantenibilidad, dificulta el control de versiones y acopla la invocación de acciones a la ejecución local de binarios específicos.
  
  Con la llegada del message broker NATS y la librería unificada `nova-event-bus` (ADR-017 y ADR-018), se hace indispensable disponer de un punto de entrada CLI unificado y estándar (`novactl`) que abstraiga la tecnología de red subyacente y permita emitir comandos estructurados hacia cualquier servicio del ecosistema Nova.

- **Decisión**:
  1. Desarrollar `novactl` como la herramienta de línea de comandos oficial en Python para el ecosistema Nova.
  2. Implementar una arquitectura basada en plugins (`CommandPlugin`), donde cada subcomando (`start-capture`, `stop-capture`, `execute`, etc.) es un módulo aislado responsable únicamente de validar sus argumentos y construir el evento tipado correspondiente.
  3. `novactl` utilizará de forma exclusiva la API pública de `nova-event-bus` para la publicación de eventos, quedando prohibida la inclusión de código o dependencias directas a NATS en `novactl`.
  4. Los eventos emitidos por `novactl` seguirán el patrón de nomenclatura `novactl.command.<nombre_comando>` e incluirán un `correlation_id` aleatorio (UUIDv4) para asegurar la trazabilidad distribuida.
  5. Progresivamente, los gestores de atajos de teclado del sistema y componentes externos migrarán las invocaciones de scripts legacy hacia `novactl`.

- **Alternativas consideradas**:
  - **Invocación directa de endpoints REST**: Rechazada por acoplar el CLI a endpoints específicos de servicios concretos y requerir conocimiento de la topología de red.
  - **Scripts Bash independientes mantenidos en el host**: Rechazada por falta de homogeneidad, mayor dificultad para testing y duplicación de lógica de transporte.
  - **Uso directo del cliente `nats-py` en la CLI**: Rechazada por violar ADR-018 y generar vendor lock-in con NATS.

- **Consecuencias**:
  - **Desacoplamiento**: El sistema operativo interactúa únicamente con la CLI `novactl`, sin conocer la infraestructura ni la tecnología del bus de eventos.
  - **Extensibilidad**: Incorporar un nuevo comando solo requiere implementar un nuevo plugin derivado de `CommandPlugin` sin modificar el motor principal del CLI.
  - **Consistencia y Trazabilidad**: Todos los comandos del CLI generan eventos estructurados y validados tipadamente mediante `nova-event-bus` con `correlation_id`.

