# Copyright (c) 2024-2025 Or Posener
#
# SPDX-License-Identifier: BSD 2-Clause License
#

from unittest.mock import MagicMock

import pytest
from pipecat.frames.frames import (
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    FunctionCallResultFrame,
    FunctionCallsStartedFrame,
    LLMFullResponseEndFrame,
    LLMRunFrame,
    LLMTextFrame,
    StartFrame,
    TranscriptionFrame,
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
    VADUserStartedSpeakingFrame,
)
from pipecat.observers.base_observer import FramePushed
from pipecat.processors.filters.identity_filter import IdentityFilter
from pipecat.processors.frame_processor import FrameDirection
from pipecat.services.llm_service import LLMService

from tests.test_utils import run_observer_test
from voiceground import VoicegroundObserver
from voiceground.events import EventCategory, EventType
from voiceground.reporters import BaseReporter


class MockReporter(BaseReporter):
    """Mock reporter for testing."""

    def __init__(self):
        self.events = []
        self.ended = False
        self.started = False
        self.conversation_id = None

    async def on_start(self, conversation_id: str):
        """Mark as started and store conversation_id."""
        self.started = True
        self.conversation_id = conversation_id

    async def on_event(self, event):
        """Record event."""
        self.events.append(event)

    async def on_end(self):
        """Mark as ended."""
        self.ended = True


class ObserverTestResult:
    """Result object from running a test, with encapsulated assertion method."""

    def __init__(self, reporter: MockReporter):
        self.reporter = reporter

    def assert_events(
        self, expected_events: list[tuple[EventCategory, EventType]], ended: bool = True
    ):
        """Assert that reporter captured the expected events.

        Args:
            expected_events: List of (category, type) tuples for expected events in order.
            ended: Whether the reporter should have been ended. Defaults to True.
        """
        assert len(self.reporter.events) == len(expected_events), (
            f"Expected {len(expected_events)} events, got {len(self.reporter.events)}"
        )
        assert self.reporter.ended == ended, f"Expected ended={ended}, got {self.reporter.ended}"

        for i, (expected_category, expected_type) in enumerate(expected_events):
            event = self.reporter.events[i]
            assert event.category == expected_category, (
                f"Event {i}: expected category {expected_category}, got {event.category}"
            )
            assert event.type == expected_type, (
                f"Event {i}: expected type {expected_type}, got {event.type}"
            )

    def assert_event_data(self, event_index: int, expected_data: dict):
        """Assert that an event has the expected data.

        Args:
            event_index: Index of the event to check.
            expected_data: Dictionary of expected data key-value pairs.
        """
        event = self.reporter.events[event_index]
        for key, value in expected_data.items():
            assert key in event.data, f"Event {event_index}: missing data key '{key}'"
            assert event.data[key] == value, (
                f"Event {event_index}: data['{key}'] = {event.data[key]}, expected {value}"
            )


@pytest.fixture
def run_test_with_observer():
    """Create a function to run tests with an observer already set up.

    Returns a function that takes frames_to_send (list of FramePushed) and runs them through the observer.
    Returns an ObserverTestResult object with the reporter and assert_events method.
    """

    async def _run(frames_to_send, conversation_id=None):
        reporter = MockReporter()
        observer = VoicegroundObserver(reporters=[reporter], conversation_id=conversation_id)

        await run_observer_test(observer, frames_to_send)
        return ObserverTestResult(reporter)

    return _run


class TestVoicegroundObserver:
    """Tests for VoicegroundObserver - testing with mock pipeline using run_test."""

    @pytest.mark.asyncio
    async def test_initializes_repoter_with_generated_conversation_id(self, run_test_with_observer):
        """Test that conversation_id is generated if not provided."""
        result = await run_test_with_observer([])

        assert result.reporter.conversation_id is not None
        assert len(result.reporter.conversation_id) > 0

    @pytest.mark.asyncio
    async def test_initializes_repoter_with_provided_conversation_id(self, run_test_with_observer):
        """Test that provided conversation_id is used."""
        custom_id = "test-conversation-123"
        identity = IdentityFilter()
        frames_to_send = [
            FramePushed(
                source=identity,
                destination=identity,
                frame=StartFrame(),
                direction=FrameDirection.DOWNSTREAM,
                timestamp=0,
            ),
        ]
        result = await run_test_with_observer(frames_to_send, conversation_id=custom_id)

        assert result.reporter.conversation_id == custom_id

    @pytest.mark.asyncio
    async def test_end_frame_triggers_reporter_end(self, run_test_with_observer):
        """Test that EndFrame triggers reporter on_end."""
        # EndFrame is added automatically by run_test
        result = await run_test_with_observer([])

        assert result.reporter.ended is True

    @pytest.mark.asyncio
    async def test_complete_conversation_sequence(self, run_test_with_observer):
        """Test a complete conversation sequence produces all expected events."""
        identity = IdentityFilter()
        frames_to_send = [
            FramePushed(
                source=identity,
                destination=identity,
                frame=UserStartedSpeakingFrame(),
                direction=FrameDirection.DOWNSTREAM,
                timestamp=0,
            ),
            FramePushed(
                source=identity,
                destination=identity,
                frame=UserStoppedSpeakingFrame(),
                direction=FrameDirection.DOWNSTREAM,
                timestamp=100_000_000,
            ),
            FramePushed(
                source=identity,
                destination=identity,
                frame=BotStartedSpeakingFrame(),
                direction=FrameDirection.DOWNSTREAM,
                timestamp=200_000_000,
            ),
            FramePushed(
                source=identity,
                destination=identity,
                frame=BotStoppedSpeakingFrame(),
                direction=FrameDirection.DOWNSTREAM,
                timestamp=300_000_000,
            ),
        ]

        result = await run_test_with_observer(frames_to_send)

        result.assert_events(
            [
                (EventCategory.USER_SPEAK, EventType.START),
                (EventCategory.USER_SPEAK, EventType.END),
                (EventCategory.BOT_SPEAK, EventType.START),
                (EventCategory.BOT_SPEAK, EventType.END),
            ]
        )

    @pytest.mark.asyncio
    async def test_frame_deduplication(self, run_test_with_observer):
        """Test that duplicate events within dedup window are filtered."""
        identity = IdentityFilter()
        frame1 = UserStartedSpeakingFrame()
        frames_to_send = [
            FramePushed(
                source=identity,
                destination=identity,
                frame=frame1,
                direction=FrameDirection.DOWNSTREAM,
                timestamp=0,
            ),
            FramePushed(
                source=identity,
                destination=identity,
                frame=frame1,  # Same frame instance
                direction=FrameDirection.DOWNSTREAM,
                timestamp=100_000,
            ),
        ]

        result = await run_test_with_observer(frames_to_send)

        # Should only have one event due to frame deduplication
        assert len(result.reporter.events) <= 1

    @pytest.mark.asyncio
    async def test_category_gates_prevent_duplicate_starts(self, run_test_with_observer):
        """Test that category gates prevent duplicate start events until end."""
        identity = IdentityFilter()

        frames_to_send = [
            FramePushed(
                source=identity,
                destination=identity,
                frame=UserStartedSpeakingFrame(),
                direction=FrameDirection.DOWNSTREAM,
                timestamp=0,
            ),
            FramePushed(
                source=identity,
                destination=identity,
                frame=UserStartedSpeakingFrame(),  # Should be blocked by gate
                direction=FrameDirection.DOWNSTREAM,
                timestamp=100_000_000,
            ),
            FramePushed(
                source=identity,
                destination=identity,
                frame=UserStoppedSpeakingFrame(),  # Opens gate
                direction=FrameDirection.DOWNSTREAM,
                timestamp=200_000_000,
            ),
            FramePushed(
                source=identity,
                destination=identity,
                frame=UserStartedSpeakingFrame(),  # Should now work
                direction=FrameDirection.DOWNSTREAM,
                timestamp=300_000_000,
            ),
        ]

        result = await run_test_with_observer(frames_to_send)

        # Should have two start events (first one, and the one after end)
        start_events = [e for e in result.reporter.events if e.type == EventType.START]
        assert len(start_events) == 2

    @pytest.mark.asyncio
    async def test_llm_text_accumulation(self, run_test_with_observer):
        """Test that LLM text chunks are accumulated and included in end event."""
        # Create a mock LLM service for source filtering
        mock_llm_service = MagicMock(spec=LLMService)
        mock_llm_service.name = "MockLLMService#0"

        frames_to_send = [
            FramePushed(
                source=mock_llm_service,
                destination=mock_llm_service,
                frame=LLMRunFrame(),
                direction=FrameDirection.DOWNSTREAM,
                timestamp=0,
            ),
            FramePushed(
                source=mock_llm_service,
                destination=mock_llm_service,
                frame=LLMTextFrame(text="Hello"),
                direction=FrameDirection.DOWNSTREAM,
                timestamp=100_000_000,
            ),
            FramePushed(
                source=mock_llm_service,
                destination=mock_llm_service,
                frame=LLMTextFrame(text=" world"),
                direction=FrameDirection.DOWNSTREAM,
                timestamp=200_000_000,
            ),
            FramePushed(
                source=mock_llm_service,
                destination=mock_llm_service,
                frame=LLMTextFrame(text="!"),
                direction=FrameDirection.DOWNSTREAM,
                timestamp=300_000_000,
            ),
            FramePushed(
                source=mock_llm_service,
                destination=mock_llm_service,
                frame=LLMFullResponseEndFrame(),
                direction=FrameDirection.DOWNSTREAM,
                timestamp=400_000_000,
            ),
        ]

        result = await run_test_with_observer(frames_to_send)

        # Find the LLM end event
        llm_end_events = [
            e
            for e in result.reporter.events
            if e.category == EventCategory.LLM and e.type == EventType.END
        ]
        assert len(llm_end_events) == 1

        # Check that accumulated text is in the event data
        assert "text" in llm_end_events[0].data
        assert llm_end_events[0].data["text"] == "Hello world!"

    @pytest.mark.asyncio
    async def test_stt_transcription_extraction(self, run_test_with_observer):
        """Test that transcription text is extracted from TranscriptionFrame."""
        transcription_text = "Hello, this is a test transcription"
        identity = IdentityFilter()

        frames_to_send = [
            FramePushed(
                source=identity,
                destination=identity,
                frame=VADUserStartedSpeakingFrame(),
                direction=FrameDirection.DOWNSTREAM,
                timestamp=0,
            ),
            FramePushed(
                source=identity,
                destination=identity,
                frame=TranscriptionFrame(
                    text=transcription_text,
                    user_id="test_user",
                    timestamp="2024-01-01T00:00:00Z",
                ),
                direction=FrameDirection.DOWNSTREAM,
                timestamp=100_000_000,
            ),
        ]

        result = await run_test_with_observer(frames_to_send)

        # Find the STT end event
        stt_end_events = [
            e
            for e in result.reporter.events
            if e.category == EventCategory.STT and e.type == EventType.END
        ]
        assert len(stt_end_events) == 1

        # Check that transcription text is in the event data
        assert "text" in stt_end_events[0].data
        assert stt_end_events[0].data["text"] == transcription_text

    @pytest.mark.asyncio
    async def test_tool_call_events(self, run_test_with_observer):
        """Test that tool call frames produce tool_call events."""
        # Create mock function call objects
        mock_function_call = MagicMock()
        mock_function_call.function_name = "get_weather"

        identity = IdentityFilter()
        frames_to_send = [
            FramePushed(
                source=identity,
                destination=identity,
                frame=FunctionCallsStartedFrame(function_calls=[mock_function_call]),
                direction=FrameDirection.DOWNSTREAM,
                timestamp=0,
            ),
            FramePushed(
                source=identity,
                destination=identity,
                frame=FunctionCallResultFrame(
                    function_name="get_weather",
                    tool_call_id="test_call_123",
                    arguments={"location": "San Francisco"},
                    result="Sunny, 72°F",
                ),
                direction=FrameDirection.DOWNSTREAM,
                timestamp=100_000_000,
            ),
        ]

        result = await run_test_with_observer(frames_to_send)

        # Check for tool_call events
        tool_call_events = [
            e for e in result.reporter.events if e.category == EventCategory.TOOL_CALL
        ]
        assert len(tool_call_events) >= 1

        # Check that start event exists and has operation
        start_events = [e for e in tool_call_events if e.type == EventType.START]
        assert len(start_events) >= 1
        if start_events:
            assert "operation" in start_events[0].data

        # Check that end event exists and has operation
        end_events = [e for e in tool_call_events if e.type == EventType.END]
        assert len(end_events) >= 1
        if end_events:
            assert "operation" in end_events[0].data
            assert end_events[0].data["operation"] == "get_weather"

    @pytest.mark.asyncio
    async def test_source_field_in_events(self, run_test_with_observer):
        """Test that events include the source field."""
        identity = IdentityFilter()
        frames_to_send = [
            FramePushed(
                source=identity,
                destination=identity,
                frame=UserStartedSpeakingFrame(),
                direction=FrameDirection.DOWNSTREAM,
                timestamp=0,
            ),
            FramePushed(
                source=identity,
                destination=identity,
                frame=UserStoppedSpeakingFrame(),
                direction=FrameDirection.DOWNSTREAM,
                timestamp=100_000_000,
            ),
        ]

        result = await run_test_with_observer(frames_to_send)

        # All events should have a source field
        for event in result.reporter.events:
            assert hasattr(event, "source")
            assert isinstance(event.source, str)
