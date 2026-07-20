import sys
from typing import Dict, List, Optional
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
        builtin_classes = []
        try:
            from novactl.plugins.version_plugin import VersionPlugin
            builtin_classes.append(VersionPlugin)
        except Exception as e:
            sys.stderr.write(f"Warning: Failed to load VersionPlugin: {e}\n")

        try:
            from novactl.plugins.help_plugin import HelpPlugin
            builtin_classes.append(HelpPlugin)
        except Exception as e:
            sys.stderr.write(f"Warning: Failed to load HelpPlugin: {e}\n")

        try:
            from novactl.plugins.start_capture_plugin import StartCapturePlugin
            builtin_classes.append(StartCapturePlugin)
        except Exception as e:
            sys.stderr.write(f"Warning: Failed to load StartCapturePlugin: {e}\n")

        try:
            from novactl.plugins.stop_capture_plugin import StopCapturePlugin
            builtin_classes.append(StopCapturePlugin)
        except Exception as e:
            sys.stderr.write(f"Warning: Failed to load StopCapturePlugin: {e}\n")

        try:
            from novactl.plugins.execute_plugin import ExecutePlugin
            builtin_classes.append(ExecutePlugin)
        except Exception as e:
            sys.stderr.write(f"Warning: Failed to load ExecutePlugin: {e}\n")

        for cls in builtin_classes:
            try:
                plugin_instance = cls()
                self.register_plugin(plugin_instance)
            except Exception as e:
                sys.stderr.write(f"Warning: Failed to instantiate plugin {cls.__name__}: {e}\n")

    def get_plugin(self, name: str) -> Optional[CommandPlugin]:
        """Retrieves a registered plugin by name."""
        return self._plugins.get(name)

    def get_all_plugins(self) -> List[CommandPlugin]:
        """Returns all registered plugins."""
        return list(self._plugins.values())
