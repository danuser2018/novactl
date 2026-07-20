import argparse
import sys
from typing import Optional
from novactl.interface import CommandPlugin
from nova_event_bus import EventBusInterface


class HelpPlugin(CommandPlugin):
    """Plugin to display general or command-specific help."""

    def __init__(self, parser: Optional[argparse.ArgumentParser] = None) -> None:
        self.parser = parser

    def set_parser(self, parser: argparse.ArgumentParser) -> None:
        self.parser = parser

    @property
    def name(self) -> str:
        return "help"

    @property
    def description(self) -> str:
        return "Display help information for novactl or a specific command"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("command", nargs="?", help="Specific command to get help for")

    async def execute(self, args: argparse.Namespace, event_bus: Optional[EventBusInterface] = None) -> int:
        target_cmd = getattr(args, "command", None)
        root_parser = getattr(args, "_root_parser", self.parser)

        if target_cmd and root_parser:
            subparsers_actions = [
                action for action in root_parser._actions
                if isinstance(action, argparse._SubParsersAction)
            ]
            found = False
            for action in subparsers_actions:
                if target_cmd in action.choices:
                    subparser = action.choices[target_cmd]
                    subparser.print_help()
                    found = True
                    break
            if not found:
                sys.stderr.write(f"Unknown command: '{target_cmd}'\n")
                root_parser.print_help(sys.stderr)
                return 2
        elif root_parser:
            root_parser.print_help()
        else:
            sys.stdout.write("novactl available commands: version, help, start-capture, stop-capture, execute\n")
        return 0
