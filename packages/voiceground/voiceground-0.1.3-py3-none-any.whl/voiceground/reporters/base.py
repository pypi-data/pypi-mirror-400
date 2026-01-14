"""Base reporter interface for Voiceground."""

from abc import ABC, abstractmethod

from voiceground.events import VoicegroundEvent


class BaseReporter(ABC):
    """Abstract base class for event reporters.

    Reporters receive VoicegroundEvents from the observer and can
    process them in various ways (logging, storage, streaming, etc.).
    """

    @abstractmethod
    async def on_start(self, conversation_id: str) -> None:
        """Handle pipeline start.

        Called when the pipeline starts. Reporters can initialize
        any resources or set metadata here.

        Args:
            conversation_id: Unique identifier for this conversation session.
        """
        pass

    @abstractmethod
    async def on_event(self, event: VoicegroundEvent) -> None:
        """Handle a new event.

        Args:
            event: The event to process.
        """
        pass

    @abstractmethod
    async def on_end(self) -> None:
        """Handle pipeline termination.

        Called when the pipeline ends (EndFrame or CancelFrame).
        Reporters should finalize any pending operations here.
        """
        pass
