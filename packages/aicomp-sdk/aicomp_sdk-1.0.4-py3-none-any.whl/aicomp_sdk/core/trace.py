from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ToolEvent:
    name: str
    args: Dict[str, Any]
    ok: bool
    output: str
    side_effect: str
    scope: str
    source: str  # what influenced: user|web|email|file|tool
    error: Optional[str] = None


@dataclass
class Trace:
    seed: int
    user_messages: List[str] = field(default_factory=list)
    tool_events: List[ToolEvent] = field(default_factory=list)
    assistant_messages: List[str] = field(default_factory=list)

    def add_user(self, text: str):
        self.user_messages.append(text)

    def add_tool(self, ev: ToolEvent):
        self.tool_events.append(ev)

    def add_assistant(self, text: str):
        self.assistant_messages.append(text)
