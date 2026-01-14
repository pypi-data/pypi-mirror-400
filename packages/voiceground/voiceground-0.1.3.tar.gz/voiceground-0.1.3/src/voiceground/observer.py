"""VoicegroundObserver - Track conversation events from pipecat pipelines."""

import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from pipecat.frames.frames import (
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    CancelFrame,
    EndFrame,
    FunctionCallCancelFrame,
    FunctionCallResultFrame,
    FunctionCallsStartedFrame,
    LLMContextFrame,
    LLMFullResponseEndFrame,
    LLMRunFrame,
    LLMTextFrame,
    StartFrame,
    TranscriptionFrame,
    TTSAudioRawFrame,
    TTSStartedFrame,
    TTSStoppedFrame,
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
    VADUserStartedSpeakingFrame,
)
from pipecat.observers.base_observer import BaseObserver, FrameProcessed, FramePushed
from pipecat.processors.aggregators.llm_response import (
    LLMAssistantContextAggregator,
    LLMUserContextAggregator,
)
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContextFrame
from pipecat.processors.frame_processor import FrameDirection
from pipecat.services.llm_service import LLMService

from voiceground.events import EventCategory, EventType, VoicegroundEvent

if TYPE_CHECKING:
    from voiceground.reporters.base import BaseReporter


@dataclass
class FrameTrigger:
    """Trigger configuration for a specific frame type.

    Attributes:
        frame: The frame type that can trigger this event.
        source_class: Only trigger if source is an instance of one of these classes.
        direction: Only trigger if frame is pushed in this direction (None = any direction).
        data_extractor: Optional function to extract event data from the frame.
            Takes the frame as argument and returns a dict to merge into event.data.
    """

    frame: type
    source_class: tuple[type, ...] | None = None
    direction: FrameDirection | None = None
    data_extractor: Callable[[Any], dict[str, Any]] | None = field(default=None)


@dataclass
class EventTrigger:
    """Trigger configuration for an event type.

    Attributes:
        frame_triggers: List of frame triggers, each with its own optional source filter.
    """

    frame_triggers: list[FrameTrigger]


@dataclass
class CategoryEvents:
    """Event configuration for a category.

    Each category can define:
    - start: Trigger for the start event (closes category gate until end)
    - end: Trigger for the end event (reopens category gate)
    - first_byte: Trigger for first byte event (auto-resets on start)
    - data_accumulator: Function to accumulate data from frames between start and end.
        Called with (frame, accumulated_data) and returns updated accumulated_data dict.
        The accumulated data is merged into the end event's data.

    Attributes:
        category: The event category.
        description: Human-readable description of what this category measures.
        start: Start event trigger (optional).
        end: End event trigger (optional).
        first_byte: First byte event trigger (optional, resets on start).
        data_accumulator: Function to accumulate data from frames (optional).
    """

    category: EventCategory
    description: str = ""
    start: EventTrigger | None = None
    end: EventTrigger | None = None
    first_byte: EventTrigger | None = None
    data_accumulator: Callable[[Any, dict[str, Any]], dict[str, Any]] | None = field(default=None)


# =============================================================================
# EVENT CONFIGURATION - Edit this to customize event tracking
# =============================================================================
# Each category defines triggers for start, end, and first_byte events.
#
# Gates (implicit, per category):
# - start: closes the category gate (prevents re-firing until end)
# - end: reopens the category gate
# - first_byte: only fires once per start (auto-resets when start fires)
# =============================================================================

CATEGORIES: list[CategoryEvents] = [
    # --- User Speech ---
    CategoryEvents(
        category=EventCategory.USER_SPEAK,
        start=EventTrigger(frame_triggers=[FrameTrigger(frame=UserStartedSpeakingFrame)]),
        end=EventTrigger(
            frame_triggers=[
                FrameTrigger(
                    frame=UserStoppedSpeakingFrame,
                    direction=FrameDirection.DOWNSTREAM,  # Only process DOWNSTREAM to avoid duplicates
                )
            ]
        ),
    ),
    # --- Bot Speech ---
    CategoryEvents(
        category=EventCategory.BOT_SPEAK,
        start=EventTrigger(frame_triggers=[FrameTrigger(frame=BotStartedSpeakingFrame)]),
        end=EventTrigger(
            frame_triggers=[
                FrameTrigger(
                    frame=BotStoppedSpeakingFrame,
                    direction=FrameDirection.DOWNSTREAM,  # Only process DOWNSTREAM to avoid duplicates
                )
            ]
        ),
    ),
    # --- STT (Speech-to-Text) ---
    CategoryEvents(
        category=EventCategory.STT,
        start=EventTrigger(frame_triggers=[FrameTrigger(frame=VADUserStartedSpeakingFrame)]),
        end=EventTrigger(
            frame_triggers=[
                FrameTrigger(
                    frame=TranscriptionFrame,
                    data_extractor=lambda f: {"text": getattr(f, "text", "") or ""},
                )
            ]
        ),
    ),
    # --- LLM (Large Language Model) ---
    CategoryEvents(
        category=EventCategory.LLM,
        start=EventTrigger(
            frame_triggers=[
                FrameTrigger(
                    frame=OpenAILLMContextFrame,
                    source_class=(LLMUserContextAggregator,),
                ),
                FrameTrigger(
                    frame=LLMContextFrame,
                    source_class=(LLMUserContextAggregator,),
                ),
                FrameTrigger(
                    frame=OpenAILLMContextFrame,
                    source_class=(LLMAssistantContextAggregator,),
                    direction=FrameDirection.UPSTREAM,  # Only when triggering LLM run after tool calls
                ),
                FrameTrigger(
                    frame=LLMContextFrame,
                    source_class=(LLMAssistantContextAggregator,),
                    direction=FrameDirection.UPSTREAM,  # Only when triggering LLM run after tool calls
                ),
                FrameTrigger(
                    frame=LLMRunFrame,
                ),
            ]
        ),
        end=EventTrigger(
            frame_triggers=[
                FrameTrigger(
                    frame=LLMFullResponseEndFrame,
                    source_class=(LLMService,),  # Only from LLM services, not downstream services
                )
            ]
        ),
        first_byte=EventTrigger(frame_triggers=[FrameTrigger(frame=LLMTextFrame)]),
        data_accumulator=lambda frame, acc: {
            **acc,
            "text": acc.get("text", "") + (getattr(frame, "text", "") or ""),
        }
        if isinstance(frame, LLMTextFrame)
        else acc,
    ),
    # --- TTS (Text-to-Speech) ---
    CategoryEvents(
        category=EventCategory.TTS,
        start=EventTrigger(frame_triggers=[FrameTrigger(frame=TTSStartedFrame)]),
        end=EventTrigger(frame_triggers=[FrameTrigger(frame=TTSStoppedFrame)]),
        first_byte=EventTrigger(frame_triggers=[FrameTrigger(frame=TTSAudioRawFrame)]),
    ),
    # --- Tool Calling (Function Calling) ---
    CategoryEvents(
        category=EventCategory.TOOL_CALL,
        description="LLM function/tool calling",
        start=EventTrigger(
            frame_triggers=[
                FrameTrigger(
                    frame=FunctionCallsStartedFrame,
                    data_extractor=lambda f: {
                        "description": ", ".join(fc.function_name for fc in f.function_calls),
                        "operation": ", ".join(fc.function_name for fc in f.function_calls),
                    }
                    if f.function_calls
                    else {},
                )
            ]
        ),
        end=EventTrigger(
            frame_triggers=[
                FrameTrigger(
                    frame=FunctionCallResultFrame,
                    data_extractor=lambda f: {
                        "operation": f.function_name,
                    },
                ),
                FrameTrigger(
                    frame=FunctionCallCancelFrame,
                    data_extractor=lambda f: {
                        "operation": f.function_name,
                    },
                ),
            ]
        ),
    ),
    # --- System: Context Aggregation ---
    CategoryEvents(
        category=EventCategory.SYSTEM,
        description="Context aggregation timeout",
        start=EventTrigger(
            frame_triggers=[
                FrameTrigger(
                    frame=TranscriptionFrame,
                    data_extractor=lambda f: {
                        "operation": "context_aggregation_timeout",
                    },
                )
            ]
        ),
        end=EventTrigger(
            frame_triggers=[
                FrameTrigger(
                    frame=OpenAILLMContextFrame,
                    source_class=(LLMUserContextAggregator,),
                    data_extractor=lambda f: {
                        "operation": "context_aggregation_timeout",
                    },
                ),
                FrameTrigger(
                    frame=LLMContextFrame,
                    source_class=(LLMUserContextAggregator,),
                    data_extractor=lambda f: {
                        "operation": "context_aggregation_timeout",
                    },
                ),
                FrameTrigger(
                    frame=LLMRunFrame,
                    source_class=(LLMUserContextAggregator,),
                    data_extractor=lambda f: {
                        "operation": "context_aggregation_timeout",
                    },
                ),
            ]
        ),
    ),
]


class VoicegroundObserver(BaseObserver):
    """Observer for tracking conversation events in pipecat pipelines.

    This observer monitors frames flowing through the pipeline and emits
    normalized VoicegroundEvents to registered reporters.

    Args:
        reporters: List of reporters to receive events.
    """

    def __init__(
        self, reporters: list["BaseReporter"] | None = None, conversation_id: str | None = None
    ):
        super().__init__()
        self._reporters: list[BaseReporter] = reporters or []
        # Generate conversation_id if not provided
        self._conversation_id: str = conversation_id or str(uuid.uuid4())
        # Track processed frames to avoid duplicate events from same frame
        # Using frame.id which is a unique identifier for each frame instance
        self._processed_frames: set[int] = set()
        # Category gates: True = ready to fire start event
        self._category_ready: dict[EventCategory, bool] = {}
        # First byte gates: True = first byte not yet seen for this category
        self._first_byte_pending: dict[EventCategory, bool] = {}
        # Track accumulated data per category (for data_accumulator)
        self._category_accumulated_data: dict[EventCategory, dict[str, Any]] = {}
        # Prevent multiple end() calls
        self._ended: bool = False
        self._init_gates()

    def _init_gates(self) -> None:
        """Initialize all gates."""
        for cat_config in CATEGORIES:
            # Categories with start triggers have gates (start open)
            if cat_config.start:
                self._category_ready[cat_config.category] = True
            # Categories with first_byte triggers track first byte
            if cat_config.first_byte:
                self._first_byte_pending[cat_config.category] = True
            # Initialize accumulated data for categories with data accumulators
            if cat_config.data_accumulator:
                self._category_accumulated_data[cat_config.category] = {}

    def add_reporter(self, reporter: "BaseReporter") -> None:
        """Add a reporter to receive events."""
        self._reporters.append(reporter)

    def remove_reporter(self, reporter: "BaseReporter") -> None:
        """Remove a reporter."""
        self._reporters.remove(reporter)

    async def _emit_event(self, event: VoicegroundEvent) -> None:
        """Emit an event to all registered reporters."""
        for reporter in self._reporters:
            await reporter.on_event(event)

    async def end(self) -> None:
        """End the observation session and finalize all reporters.

        Called automatically when EndFrame or CancelFrame is detected.
        Can also be called manually. Safe to call multiple times.
        """
        if self._ended:
            return
        self._ended = True

        for reporter in self._reporters:
            await reporter.on_end()

    def _create_event(
        self,
        category: EventCategory,
        event_type: EventType,
        timestamp: int,
        source: str = "",
        data: dict[str, Any] | None = None,
    ) -> VoicegroundEvent:
        """Create a VoicegroundEvent with the given parameters."""
        timestamp_seconds = timestamp / 1_000_000_000
        return VoicegroundEvent(
            id=str(uuid.uuid4()),
            timestamp=timestamp_seconds,
            category=category,
            type=event_type,
            source=source,
            data=data or {},
        )

    def _check_source(
        self,
        source_class: tuple[type, ...] | None,
        source_obj: object,
    ) -> bool:
        """Check if source matches filter. Returns True if no filter."""
        if source_class is not None:
            return isinstance(source_obj, source_class)
        return True

    async def _try_emit(
        self,
        category: EventCategory,
        event_type: EventType,
        trigger: EventTrigger,
        frame,
        timestamp: int,
        timestamp_seconds: float,
        source_obj: object,
        source_name: str,
        direction: FrameDirection,
    ) -> bool:
        """Try to emit an event if conditions are met. Returns True if emitted."""
        matched_trigger: FrameTrigger | None = None

        # Check if frame matches any frame trigger and its source filter
        for frame_trigger in trigger.frame_triggers:
            if isinstance(frame, frame_trigger.frame):
                # Check source filter for this frame type
                if not self._check_source(frame_trigger.source_class, source_obj):
                    continue
                # Check direction filter if specified
                if frame_trigger.direction is not None and direction != frame_trigger.direction:
                    continue
                # Frame matches and all filters pass
                matched_trigger = frame_trigger
                break
        else:
            # No matching frame trigger found
            return False

        # Extract frame-specific data using the matched trigger's extractor
        event_data: dict[str, Any] = {}
        if matched_trigger.data_extractor:
            event_data = matched_trigger.data_extractor(frame)

        # Emit the event
        event = self._create_event(category, event_type, timestamp, source_name, event_data)
        await self._emit_event(event)
        return True

    async def on_push_frame(self, data: FramePushed) -> None:
        """Handle frame push events."""
        frame = data.frame
        timestamp = data.timestamp
        timestamp_seconds = timestamp / 1_000_000_000
        source_name = data.source.name if hasattr(data.source, "name") else ""

        # Call on_start when StartFrame is encountered
        if isinstance(frame, StartFrame):
            if not hasattr(self, "_started"):
                self._started = True
                for reporter in self._reporters:
                    await reporter.on_start(self._conversation_id)
            return

        # Check for pipeline end frames
        if isinstance(frame, (EndFrame, CancelFrame)):
            await self.end()
            return

        # Early exit if we've already processed this frame instance
        # Use frame.id which is a unique identifier for each frame instance
        if frame.id in self._processed_frames:
            return
        self._processed_frames.add(frame.id)

        # Update data accumulators for categories that are currently active (gate closed)
        for cat_config in CATEGORIES:
            if cat_config.data_accumulator and not self._category_ready.get(
                cat_config.category, True
            ):
                # Category is active (gate closed), accumulate data from this frame
                acc_data = self._category_accumulated_data.get(cat_config.category, {})
                self._category_accumulated_data[cat_config.category] = cat_config.data_accumulator(
                    frame, acc_data
                )

        # Process each category (no early returns - allow multiple events per frame)
        for cat_config in CATEGORIES:
            category = cat_config.category

            # --- START event ---
            if cat_config.start:
                # Check if category gate is open
                gate_open = self._category_ready.get(category, True)

                if gate_open and await self._try_emit(
                    category,
                    EventType.START,
                    cat_config.start,
                    frame,
                    timestamp,
                    timestamp_seconds,
                    data.source,
                    source_name,
                    data.direction,
                ):
                    # Close gate and reset first_byte
                    self._category_ready[category] = False
                    if category in self._first_byte_pending:
                        self._first_byte_pending[category] = True
                    # Reset accumulated data when category starts
                    if cat_config.data_accumulator:
                        self._category_accumulated_data[category] = {}

            # --- FIRST_BYTE event ---
            if cat_config.first_byte and self._first_byte_pending.get(category, False):
                if await self._try_emit(
                    category,
                    EventType.FIRST_BYTE,
                    cat_config.first_byte,
                    frame,
                    timestamp,
                    timestamp_seconds,
                    data.source,
                    source_name,
                    data.direction,
                ):
                    self._first_byte_pending[category] = False

            # --- END event ---
            if cat_config.end:
                # Check if this frame matches the end trigger
                matched_end_trigger: FrameTrigger | None = None
                for frame_trigger in cat_config.end.frame_triggers:
                    if isinstance(frame, frame_trigger.frame):
                        if not self._check_source(frame_trigger.source_class, data.source):
                            continue
                        if (
                            frame_trigger.direction is not None
                            and data.direction != frame_trigger.direction
                        ):
                            continue
                        matched_end_trigger = frame_trigger
                        break

                if matched_end_trigger:
                    # Extract frame-specific data
                    frame_data: dict[str, Any] = {}
                    if matched_end_trigger.data_extractor:
                        frame_data = matched_end_trigger.data_extractor(frame)

                    # Merge accumulated data if accumulator exists
                    accumulated_data = self._category_accumulated_data.get(category, {})
                    if cat_config.data_accumulator and accumulated_data:
                        event_data = {**frame_data, **accumulated_data}
                    else:
                        event_data = frame_data

                    # Emit event with merged data
                    event = self._create_event(
                        category, EventType.END, timestamp, source_name, event_data
                    )
                    await self._emit_event(event)

                    # Clear accumulated data after emitting
                    if cat_config.data_accumulator:
                        self._category_accumulated_data[category] = {}
                    # Reopen category gate
                    self._category_ready[category] = True

    async def on_process_frame(self, data: FrameProcessed) -> None:
        """Handle frame process events.

        Currently not used - we primarily track push events.
        """
        pass
