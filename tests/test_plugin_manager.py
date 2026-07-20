import argparse
from typing import Optional
import pytest
from novactl.interface import CommandPlugin
from novactl.plugin_manager import PluginManager
from nova_event_bus import EventBusInterface


class DummyPlugin(CommandPlugin):
    @property
    def name(self) -> str:
        return "dummy"

    @property
    def description(self) -> str:
        return "Dummy plugin description"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        pass

    async def execute(self, args: argparse.Namespace, event_bus: Optional[EventBusInterface] = None) -> int:
        return 0


def test_plugin_registration():
    manager = PluginManager()
    dummy = DummyPlugin()
    manager.register_plugin(dummy)

    assert manager.get_plugin("dummy") is dummy
    assert dummy in manager.get_all_plugins()
    assert manager.get_plugin("nonexistent") is None


def test_load_builtin_plugins():
    manager = PluginManager()
    manager.load_builtin_plugins()

    plugin_names = [p.name for p in manager.get_all_plugins()]
    assert "version" in plugin_names
    assert "help" in plugin_names
    assert "start-capture" in plugin_names
    assert "stop-capture" in plugin_names
    assert "execute" in plugin_names
