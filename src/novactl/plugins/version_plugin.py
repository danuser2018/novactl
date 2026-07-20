import argparse
import sys
from typing import Optional
from novactl import __version__
from novactl.interface import CommandPlugin
from nova_event_bus import EventBusInterface


class VersionPlugin(CommandPlugin):
    """Plugin to query novactl version."""

    @property
    def name(self) -> str:
        return "version"

    @property
    def description(self) -> str:
        return "Show novactl version"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        pass

    async def execute(self, args: argparse.Namespace, event_bus: Optional[EventBusInterface] = None) -> int:
        sys.stdout.write(f"novactl {__version__}\n")
        return 0
