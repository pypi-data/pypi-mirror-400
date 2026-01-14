"""Voiceground event types for conversation observability."""

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EventCategory(str, Enum):
    """Categories of conversation events."""

    USER_SPEAK = "user_speak"
    BOT_SPEAK = "bot_speak"
    STT = "stt"
    LLM = "llm"
    TTS = "tts"
    TOOL_CALL = "tool_call"
    SYSTEM = "system"


class EventType(str, Enum):
    """Types of events within each category."""

    START = "start"
    END = "end"
    FIRST_BYTE = "first_byte"


@dataclass
class VoicegroundEvent:
    """A normalized conversation event.

    Attributes:
        id: Unique identifier for this event.
        timestamp: Unix timestamp in seconds when the event occurred.
        category: The category of the event (user_speak, bot_speak, stt, llm, tts, tool_call, system).
        type: The type of event (start, end, first_byte).
        source: The name of the processor/frame source that triggered this event.
        data: Additional event-specific data.
    """

    id: str
    timestamp: float
    category: EventCategory
    type: EventType
    source: str = ""
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert the event to a dictionary for JSON serialization."""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "category": self.category.value,
            "type": self.type.value,
            "source": self.source,
            "data": self.data,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VoicegroundEvent":
        """Create an event from a dictionary."""
        # Generate ID if not present (for backward compatibility)
        event_id = data.get("id") or str(uuid.uuid4())
        return cls(
            id=event_id,
            timestamp=data["timestamp"],
            category=EventCategory(data["category"]),
            type=EventType(data["type"]),
            source=data.get("source", ""),
            data=data.get("data", {}),
        )
