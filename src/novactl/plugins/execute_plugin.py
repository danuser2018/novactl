import argparse
import sys
import uuid
from typing import Optional
from novactl.interface import CommandPlugin
from novactl.events import ExecuteShortcutCommand
from nova_event_bus import EventBusInterface


class ExecutePlugin(CommandPlugin):
    """Plugin to execute a direct shortcut action."""

    @property
    def name(self) -> str:
        return "execute"

    @property
    def description(self) -> str:
        return "Execute a direct shortcut action"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "shortcut",
            type=str,
            help="Shortcut identifier to execute"
        )
        parser.add_argument(
            "--channel",
            type=str,
            default="voice",
            help="Target channel (default: voice)"
        )

    async def execute(self, args: argparse.Namespace, event_bus: Optional[EventBusInterface] = None) -> int:
        if event_bus is None:
            sys.stderr.write("Error: Event bus interface is required for execute\n")
            return 1

        shortcut = getattr(args, "shortcut", None)
        if not shortcut:
            sys.stderr.write("Error: 'shortcut' parameter is required\n")
            return 2

        correlation_id = str(uuid.uuid4())
        channel = getattr(args, "channel", "voice") or "voice"

        cmd_event = ExecuteShortcutCommand(
            correlation_id=correlation_id,
            shortcut=shortcut,
            channel=channel
        )

        await event_bus.publish(cmd_event)
        sys.stdout.write(f"Executed shortcut '{shortcut}' (correlation_id={correlation_id})\n")
        return 0
