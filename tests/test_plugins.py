import argparse
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock
from novactl.plugins.version_plugin import VersionPlugin
from novactl.plugins.help_plugin import HelpPlugin
from novactl.plugins.start_capture_plugin import StartCapturePlugin
from novactl.plugins.stop_capture_plugin import StopCapturePlugin
from novactl.plugins.execute_plugin import ExecutePlugin
from novactl.events import StartSpeechCaptureCommand, StopSpeechCaptureCommand, ExecuteShortcutCommand


@pytest.mark.asyncio
async def test_version_plugin(capsys):
    plugin = VersionPlugin()
    assert plugin.name == "version"
    assert "version" in plugin.description.lower()

    parser = argparse.ArgumentParser()
    plugin.configure_parser(parser)

    exit_code = await plugin.execute(argparse.Namespace())
    assert exit_code == 0

    captured = capsys.readouterr()
    assert "novactl 1.0.0" in captured.out


@pytest.mark.asyncio
async def test_help_plugin_general(capsys):
    plugin = HelpPlugin()
    assert plugin.name == "help"

    exit_code = await plugin.execute(argparse.Namespace())
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "novactl available commands" in captured.out


@pytest.mark.asyncio
async def test_help_plugin_specific_command(capsys):
    root_parser = argparse.ArgumentParser(prog="novactl")
    subparsers = root_parser.add_subparsers(dest="command")
    exec_parser = subparsers.add_parser("execute", help="Execute shortcut")
    exec_parser.add_argument("shortcut", help="Shortcut to execute")

    plugin = HelpPlugin(parser=root_parser)
    args = argparse.Namespace(command="execute", _root_parser=root_parser)

    exit_code = await plugin.execute(args)
    assert exit_code == 0


@pytest.mark.asyncio
async def test_start_capture_plugin_success(capsys):
    plugin = StartCapturePlugin()
    assert plugin.name == "start-capture"

    mock_bus = AsyncMock()
    args = argparse.Namespace(channel="voice")

    exit_code = await plugin.execute(args, mock_bus)
    assert exit_code == 0

    mock_bus.publish.assert_called_once()
    published_event = mock_bus.publish.call_args[0][0]
    assert isinstance(published_event, StartSpeechCaptureCommand)
    assert published_event.channel == "voice"
    assert published_event.correlation_id is not None

    captured = capsys.readouterr()
    assert "Started speech capture" in captured.out


@pytest.mark.asyncio
async def test_start_capture_plugin_no_bus():
    plugin = StartCapturePlugin()
    exit_code = await plugin.execute(argparse.Namespace(), event_bus=None)
    assert exit_code == 1


@pytest.mark.asyncio
async def test_stop_capture_plugin_success(capsys):
    plugin = StopCapturePlugin()
    assert plugin.name == "stop-capture"

    mock_bus = AsyncMock()
    args = argparse.Namespace(channel="voice")

    exit_code = await plugin.execute(args, mock_bus)
    assert exit_code == 0

    mock_bus.publish.assert_called_once()
    published_event = mock_bus.publish.call_args[0][0]
    assert isinstance(published_event, StopSpeechCaptureCommand)
    assert published_event.channel == "voice"
    assert published_event.correlation_id is not None

    captured = capsys.readouterr()
    assert "Stopped speech capture" in captured.out


@pytest.mark.asyncio
async def test_stop_capture_plugin_no_bus():
    plugin = StopCapturePlugin()
    exit_code = await plugin.execute(argparse.Namespace(), event_bus=None)
    assert exit_code == 1


@pytest.mark.asyncio
async def test_execute_plugin_success(capsys):
    plugin = ExecutePlugin()
    assert plugin.name == "execute"

    mock_bus = AsyncMock()
    args = argparse.Namespace(shortcut="volume-up", channel="voice")

    exit_code = await plugin.execute(args, mock_bus)
    assert exit_code == 0

    mock_bus.publish.assert_called_once()
    published_event = mock_bus.publish.call_args[0][0]
    assert isinstance(published_event, ExecuteShortcutCommand)
    assert published_event.shortcut == "volume-up"
    assert published_event.channel == "voice"
    assert published_event.correlation_id is not None

    captured = capsys.readouterr()
    assert "Executed shortcut 'volume-up'" in captured.out


@pytest.mark.asyncio
async def test_execute_plugin_missing_shortcut():
    plugin = ExecutePlugin()
    mock_bus = AsyncMock()
    args = argparse.Namespace(shortcut=None, channel="voice")

    exit_code = await plugin.execute(args, mock_bus)
    assert exit_code == 2
