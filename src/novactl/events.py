from dataclasses import dataclass
from nova_event_bus import Event, event


@event("novactl.command.start_speech_capture")
@dataclass
class StartSpeechCaptureCommand(Event):
    correlation_id: str
    channel: str = "voice"


@event("novactl.command.stop_speech_capture")
@dataclass
class StopSpeechCaptureCommand(Event):
    correlation_id: str
    channel: str = "voice"


@event("novactl.command.execute_shortcut")
@dataclass
class ExecuteShortcutCommand(Event):
    correlation_id: str
    shortcut: str
    channel: str = "voice"
