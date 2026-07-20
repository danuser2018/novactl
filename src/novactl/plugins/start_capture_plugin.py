import argparse
import sys
import uuid
from typing import Optional
from novactl.interface import CommandPlugin
from novactl.events import StartSpeechCaptureCommand
from nova_event_bus import EventBusInterface


class StartCapturePlugin(CommandPlugin):
    """Plugin to send start speech capture command."""

    @property
    def name(self) -> str:
        return "start-capture"

    @property
    def description(self) -> str:
        return "Publish start speech capture command"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--channel",
            type=str,
            default="voice",
            help="Target capture channel (default: voice)"
        )

    async def execute(self, args: argparse.Namespace, event_bus: Optional[EventBusInterface] = None) -> int:
        if event_bus is None:
            sys.stderr.write("Error: Event bus interface is required for start-capture\n")
            return 1

        correlation_id = str(uuid.uuid4())
        channel = getattr(args, "channel", "voice") or "voice"

        cmd_event = StartSpeechCaptureCommand(
            correlation_id=correlation_id,
            channel=channel
        )

        await event_bus.publish(cmd_event)
        sys.stdout.write(f"Started speech capture (correlation_id={correlation_id})\n")
        return 0
