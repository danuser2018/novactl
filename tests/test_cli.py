import pytest
from unittest.mock import AsyncMock, patch
from novactl.cli import main, build_parser
from novactl.plugin_manager import PluginManager
from nova_event_bus import EventBusConnectionError


def test_build_parser():
    manager = PluginManager()
    manager.load_builtin_plugins()
    parser = build_parser(manager)

    subparsers_actions = [
        action for action in parser._actions
        if action.dest == "subcommand"
    ]
    assert len(subparsers_actions) == 1
    choices = subparsers_actions[0].choices
    assert "version" in choices
    assert "help" in choices
    assert "start-capture" in choices
    assert "stop-capture" in choices
    assert "execute" in choices


def test_main_version(capsys):
    exit_code = main(["version"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "novactl 1.0.0" in captured.out


def test_main_no_args(capsys):
    exit_code = main([])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "usage: novactl" in captured.out


def test_main_help_command(capsys):
    exit_code = main(["help", "execute"])
    assert exit_code == 0


def test_main_invalid_command():
    exit_code = main(["unknown-cmd"])
    assert exit_code == 2


@patch("novactl.cli.NatsEventBus")
def test_main_bus_command_success(mock_event_bus_cls, capsys):
    mock_bus_instance = AsyncMock()
    mock_event_bus_cls.return_value = mock_bus_instance

    exit_code = main(["start-capture"])
    assert exit_code == 0
    mock_bus_instance.connect.assert_called_once()
    mock_bus_instance.publish.assert_called_once()
    mock_bus_instance.disconnect.assert_called_once()


@patch("novactl.cli.NatsEventBus")
def test_main_nats_offline(mock_event_bus_cls, capsys):
    mock_bus_instance = AsyncMock()
    mock_bus_instance.connect.side_effect = EventBusConnectionError("Broker offline")
    mock_event_bus_cls.return_value = mock_bus_instance

    exit_code = main(["start-capture"])
    assert exit_code == 1

    captured = capsys.readouterr()
    assert "Error: Could not connect to Nova event bus" in captured.err
