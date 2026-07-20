import argparse
import asyncio
import sys
from typing import List, Optional

from novactl.plugin_manager import PluginManager
from nova_event_bus import NatsEventBus, EventBusError, EventBusConnectionError


def build_parser(plugin_manager: PluginManager) -> argparse.ArgumentParser:
    """Constructs the root ArgumentParser and attaches subcommands from registered plugins."""
    parser = argparse.ArgumentParser(
        prog="novactl",
        description="Nova ecosystem Command Line Interface"
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    for plugin in plugin_manager.get_all_plugins():
        sub_parser = subparsers.add_parser(plugin.name, help=plugin.description)
        plugin.configure_parser(sub_parser)
        if hasattr(plugin, "set_parser"):
            plugin.set_parser(parser)

    return parser


async def async_main(argv: Optional[List[str]] = None) -> int:
    """Async CLI execution entrypoint."""
    if argv is None:
        argv = sys.argv[1:]

    plugin_manager = PluginManager()
    plugin_manager.load_builtin_plugins()
    parser = build_parser(plugin_manager)

    # If no arguments passed, print help and exit 0
    if not argv:
        parser.print_help()
        return 0

    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 2

    if not args.subcommand:
        parser.print_help()
        return 0

    setattr(args, "_root_parser", parser)

    plugin = plugin_manager.get_plugin(args.subcommand)
    if not plugin:
        sys.stderr.write(f"Error: Command '{args.subcommand}' is not recognized.\n")
        parser.print_help(sys.stderr)
        return 2

    # Information plugins like 'version' and 'help' don't require an event bus
    if args.subcommand in ("version", "help"):
        return await plugin.execute(args)

    # Event publishing plugins require NatsEventBus connection
    event_bus = NatsEventBus()
    try:
        await event_bus.connect()
    except (EventBusError, EventBusConnectionError, ConnectionError, OSError, Exception) as e:
        sys.stderr.write("Error: Could not connect to Nova event bus\n")
        return 1

    try:
        return await plugin.execute(args, event_bus)
    finally:
        try:
            await event_bus.disconnect()
        except Exception:
            pass


def main(argv: Optional[List[str]] = None) -> int:
    """CLI execution entrypoint. Returns exit status code."""
    try:
        return asyncio.run(async_main(argv))
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
