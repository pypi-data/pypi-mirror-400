#!/usr/bin/env python3
"""Basic example demonstrating Voiceground with a real pipecat pipeline.

This example uses:
- LocalAudioTransport for microphone input and speaker output
- ElevenLabs for both STT and TTS
- OpenAI as the LLM

Requirements:
    pip install "pipecat-ai[openai,elevenlabs,local]"

    On macOS, also install portaudio (required for pyaudio):
    brew install portaudio

Environment variables:
    OPENAI_API_KEY: Your OpenAI API key
    ELEVENLABS_API_KEY: Your ElevenLabs API key
    VOICE_ID: Voice id for the selected voice
"""

import asyncio
import os
import sys
import uuid

import aiohttp
from dotenv import load_dotenv
from loguru import logger
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.services.elevenlabs.stt import ElevenLabsSTTService
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.local.audio import LocalAudioTransport, LocalAudioTransportParams

from voiceground import HTMLReporter, VoicegroundObserver

load_dotenv(override=True)

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")


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

    print("🎙️ Starting voice conversation...")
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

        # Set up conversation context
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful and friendly AI assistant. "
                    "Keep your responses concise and conversational. "
                    "You are having a voice conversation, so be natural and engaging."
                ),
            },
        ]
        context = OpenAILLMContext(messages)
        context_aggregator = llm.create_context_aggregator(context)

        # Build the pipeline
        pipeline = Pipeline(
            [
                transport.input(),  # Capture audio from microphone
                stt,  # Convert speech to text (ElevenLabs)
                context_aggregator.user(),  # Add user message to context
                llm,  # Generate response (OpenAI)
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
            conversation_id=conversation_id,
        )

        # Run the pipeline
        runner = PipelineRunner(handle_sigint=True)

        try:
            await runner.run(task)
        except KeyboardInterrupt:
            print("\n\n👋 Conversation ended by user.")
        finally:
            print("\n📊 Report generated in ./reports/")
            print("   - voiceground_report_*.html: Interactive visualization")


if __name__ == "__main__":
    asyncio.run(main())
