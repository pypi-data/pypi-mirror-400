"""Tests for Voiceground reporters."""

import tempfile
import uuid
from pathlib import Path

import pytest

from voiceground.events import EventCategory, EventType, VoicegroundEvent
from voiceground.reporters import HTMLReporter


class TestHTMLReporter:
    """Tests for HTMLReporter."""

    @pytest.mark.asyncio
    async def test_write_events_on_end(self):
        """Test that reporter writes events when pipeline ends."""
        with tempfile.TemporaryDirectory() as tmpdir:
            conversation_id = str(uuid.uuid4())
            reporter = HTMLReporter(output_dir=tmpdir)

            await reporter.on_start(conversation_id)

            event1 = VoicegroundEvent(
                id=str(uuid.uuid4()),
                timestamp=1000.0,
                category=EventCategory.LLM,
                type=EventType.START,
            )
            event2 = VoicegroundEvent(
                id=str(uuid.uuid4()),
                timestamp=1001.5,
                category=EventCategory.LLM,
                type=EventType.END,
            )

            await reporter.on_event(event1)
            await reporter.on_event(event2)
            await reporter.on_end()

            # Check that HTML file was created (no longer generates JSON)
            html_path = Path(tmpdir) / f"voiceground_report_{conversation_id}.html"
            assert html_path.exists()

            # Check contents
            with open(html_path) as f:
                html_content = f.read()

            # Verify events are embedded in HTML
            assert "llm" in html_content
            assert "start" in html_content
            assert "end" in html_content

    @pytest.mark.asyncio
    async def test_generate_html_report(self):
        """Test that HTML report is generated."""
        import uuid

        with tempfile.TemporaryDirectory() as tmpdir:
            conversation_id = str(uuid.uuid4())
            reporter = HTMLReporter(output_dir=tmpdir)

            await reporter.on_start(conversation_id)

            event = VoicegroundEvent(
                id=str(uuid.uuid4()),
                timestamp=1000.0,
                category=EventCategory.TTS,
                type=EventType.FIRST_BYTE,
            )

            await reporter.on_event(event)
            await reporter.on_end()

            # Check that HTML file was created with conversation_id in filename
            html_path = Path(tmpdir) / f"voiceground_report_{conversation_id}.html"
            assert html_path.exists()

            # Check that HTML contains event data
            with open(html_path) as f:
                html_content = f.read()

            assert "Voiceground Report" in html_content or "voiceground" in html_content.lower()
            assert "tts" in html_content
            assert "first_byte" in html_content
