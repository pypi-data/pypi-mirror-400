#!/usr/bin/env python3
"""Example demonstrating Voiceground with tool calling (function calling).

This example uses:
- LocalAudioTransport for microphone input and speaker output
- ElevenLabs for both STT and TTS
- OpenAI as the LLM with function calling support

The example includes a simple weather function that the LLM can call.

Requirements:
    pip install "pipecat-ai[openai,elevenlabs,local]"

    On macOS, also install portaudio (required for pyaudio):
    brew install portaudio

Environment variables:
    OPENAI_API_KEY: Your OpenAI API key
    ELEVENLABS_API_KEY: Your ElevenLabs API key
    VOICE_ID: A voice id for the selected voice
"""

import asyncio
import os
import sys
import uuid
from datetime import datetime

import aiohttp
from dotenv import load_dotenv
from loguru import logger
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.services.elevenlabs.stt import ElevenLabsSTTService
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.services.llm_service import FunctionCallParams
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.local.audio import LocalAudioTransport, LocalAudioTransportParams

from voiceground import HTMLReporter, VoicegroundObserver

load_dotenv(override=True)

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")


# Example function that the LLM can call
async def get_weather(location: str) -> str:
    """Get the current weather for a location.

    Args:
        location: The city or location name

    Returns:
        A string describing the weather
    """
    # Simulate API delay
    await asyncio.sleep(0.3)

    # This is a mock function - in a real application, you'd call a weather API
    weather_data = {
        "San Francisco": "Sunny, 72°F",
        "New York": "Cloudy, 65°F",
        "London": "Rainy, 55°F",
        "Tokyo": "Clear, 75°F",
    }
    return weather_data.get(location, f"Unknown location: {location}")


async def get_current_time(timezone: str = "UTC") -> str:
    """Get the current time in a specific timezone.

    Args:
        timezone: The timezone (default: UTC)

    Returns:
        A string with the current time
    """
    # Simulate API delay
    await asyncio.sleep(0.3)

    now = datetime.now()
    return f"The current time in {timezone} is {now.strftime('%Y-%m-%d %H:%M:%S')}"


async def main():
    # Validate API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("VOICE_ID")

    if not openai_key:
        print("❌ OPENAI_API_KEY environment variable is required")
        sys.exit(1)
    if not elevenlabs_key:
        print("❌ ELEVENLABS_API_KEY environment variable is required")
        sys.exit(1)
    if not voice_id:
        print("❌ VOICE_ID environment variable is required")
        sys.exit(1)

    print("🎙️ Starting voice conversation with tool calling...")
    print("   Try asking: 'What's the weather in San Francisco?' or 'What time is it?'")
    print("   Speak into your microphone. Press Ctrl+C to exit.\n")

    async with aiohttp.ClientSession() as session:
        # Create Voiceground reporter and observer
        # Optionally provide a conversation_id, or let it auto-generate a UUID
        conversation_id = str(uuid.uuid4())  # Or use your own ID
        reporter = HTMLReporter(output_dir="./reports", auto_open=True)
        observer = VoicegroundObserver(reporters=[reporter], conversation_id=conversation_id)

        # Configure local audio transport with input and output
        transport = LocalAudioTransport(
            LocalAudioTransportParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                vad_enabled=True,
                vad_analyzer=SileroVADAnalyzer(),
            )
        )

        # Initialize ElevenLabs STT service
        stt = ElevenLabsSTTService(
            api_key=elevenlabs_key,
            aiohttp_session=session,
        )

        # Initialize ElevenLabs TTS service

        tts = ElevenLabsTTSService(
            api_key=elevenlabs_key,
            aiohttp_session=session,
            voice_id=voice_id,
        )

        # Initialize OpenAI LLM service
        llm = OpenAILLMService(
            api_key=openai_key,
            model="gpt-4o-mini",
        )

        # Define tool schemas for the context
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get the current weather for a specific location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city or location name, e.g. San Francisco",
                            }
                        },
                        "required": ["location"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_current_time",
                    "description": "Get the current time in a specific timezone",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "timezone": {
                                "type": "string",
                                "description": "The timezone name, e.g. UTC, America/New_York",
                            }
                        },
                        "required": [],
                    },
                },
            },
        ]

        # Register function handlers with the LLM service
        async def handle_get_weather(params: FunctionCallParams):
            """Handle weather function calls."""
            location = params.arguments.get("location", "Unknown")
            result = await get_weather(location)
            await params.result_callback(result)

        async def handle_get_current_time(params: FunctionCallParams):
            """Handle time function calls."""
            timezone = params.arguments.get("timezone", "UTC")
            result = await get_current_time(timezone)
            await params.result_callback(result)

        llm.register_function("get_weather", handle_get_weather)
        llm.register_function("get_current_time", handle_get_current_time)

        # Set up conversation context with tools
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful and friendly AI assistant with access to tools. "
                    "You can check the weather and get the current time. "
                    "When the user asks about weather or time, use the appropriate function. "
                    "Keep your responses concise and conversational."
                ),
            },
        ]
        context = OpenAILLMContext(messages, tools=tools)
        context_aggregator = llm.create_context_aggregator(context)

        # Build the pipeline
        pipeline = Pipeline(
            [
                transport.input(),  # Capture audio from microphone
                stt,  # Convert speech to text (ElevenLabs)
                context_aggregator.user(),  # Add user message to context
                llm,  # Generate response (OpenAI) with function calling
                tts,  # Convert text to speech (ElevenLabs)
                transport.output(),  # Play audio through speakers
                context_aggregator.assistant(),  # Add assistant message to context
            ]
        )

        # Create pipeline task with the Voiceground observer
        task = PipelineTask(
            pipeline,
            params=PipelineParams(
                allow_interruptions=True,
                enable_metrics=True,
                enable_usage_metrics=True,
            ),
            observers=[observer],
        )

        @task.event_handler("on_pipeline_started")
        async def on_pipeline_started(task, frame):
            await task.queue_frame(LLMRunFrame())

        # Run the pipeline
        runner = PipelineRunner(handle_sigint=True)

        try:
            await runner.run(task)
        except KeyboardInterrupt:
            print("\n\n👋 Conversation ended by user.")
        finally:
            print("\n📊 Report generated in ./reports/")
            print("   - voiceground_report_*.html: Interactive visualization")
            print("   - Look for 'tool_call' events to see function calls!")


if __name__ == "__main__":
    asyncio.run(main())
