from abc import ABC, abstractmethod
import argparse
from typing import Optional
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
