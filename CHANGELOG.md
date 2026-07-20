# Registro de cambios

Todos los cambios notables de este proyecto se documentan en este fichero.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y este proyecto adhiere a [Versionado Semántico](https://semver.org/lang/es/).

## Guía de uso

Cada versión se documenta bajo su número de versión y fecha de publicación.
Los cambios se agrupan en las siguientes categorías:

- **Añadido** — nuevas funcionalidades.
- **Cambiado** — cambios en funcionalidades existentes.
- **Obsoleto** — funcionalidades que serán eliminadas en versiones futuras.
- **Eliminado** — funcionalidades eliminadas en esta versión.
- **Corregido** — corrección de errores.
- **Seguridad** — correcciones de vulnerabilidades.

---

## [1.0.0] - 2026-07-21

### Añadido

- Implementación de la primera versión del CLI `novactl` v1.0.0 con motor central en Python (`cli.py`), gestor de plugins (`plugin_manager.py`) e interfaz abstracta (`interface.py`).
- Implementación de plugins incorporados: `VersionPlugin` (`novactl version`), `HelpPlugin` (`novactl help`), `StartCapturePlugin` (`novactl start-capture`), `StopCapturePlugin` (`novactl stop-capture`) y `ExecutePlugin` (`novactl execute`).
- Definición de eventos tipados de comando (`StartSpeechCaptureCommand`, `StopSpeechCaptureCommand`, `ExecuteShortcutCommand`) integrados mediante `nova-event-bus` (`events.py`).
- Configuración de empaquetado y ejecutable en `pyproject.toml` y dependencias en `requirements.txt`.
- Documentación completa de uso, instalación y arquitectura de plugins en `README.md`.
- Workflow de GitHub Actions `.github/workflows/pr-tests.yml` para ejecución automatizada de tests en PRs y pushes.
- Suite de tests unitarios e integración con `pytest` y `pytest-cov` en el directorio `tests/`.
- Fichero `CONTRIBUTING.md` con el flujo de trabajo Trunk Based Development,
  convenciones de commits, guía de Pull Requests y buenas prácticas para
  desarrollo asistido con IA.
- Fichero `CHANGELOG.md` con el formato Keep a Changelog v1.1.0 en castellano.
- Configuración del agente de IA mediante el directorio `.agent` y el enlace simbólico a las skills compartidas del ecosistema.

### Corregido

- Especificación de la dependencia `nova-event-bus` con URL de Git (`nova-event-bus @ git+https://github.com/danuser2018/nova-event-bus.git@1.1.0`) en `pyproject.toml` para resolver la instalación de la librería local en los workflows de CI/CD.

---

<!-- Plantilla para nuevas versiones:

## [X.Y.Z] - AAAA-MM-DD

### Añadido
-

### Cambiado
-

### Obsoleto
-

### Eliminado
-

### Corregido
-

### Seguridad
-

-->

[Sin publicar]: https://github.com/danuser2018/novactl/compare/HEAD...HEAD
