# Voiceground

Observability framework for [Pipecat](https://github.com/pipecat-ai/pipecat) voice and multimodal conversational AI.

## Features

- **VoicegroundObserver**: Track conversation events following Pipecat's Observer pattern
- **HTMLReporter**: Generate interactive HTML reports with timeline visualization

## Installation

```bash
pip install voiceground
```

Or with UV:

```bash
uv add voiceground
```

## Quick Start

```python
import uuid
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineTask
from voiceground import VoicegroundObserver, HTMLReporter

# Create observer with HTML reporter
conversation_id = str(uuid.uuid4())
reporter = HTMLReporter(output_dir="./reports")
observer = VoicegroundObserver(
    reporters=[reporter],
    conversation_id=conversation_id
)

# Create pipeline task with observer
task = PipelineTask(
    pipeline=Pipeline([...]),
    observers=[observer]
)

# Run your pipeline
```

## Tested With

Voiceground has been tested with the following Pipecat providers:

### LLM Providers
- [x] OpenAI (GPT)

### STT Providers
- [x] ElevenLabs

### TTS Providers
- [x] ElevenLabs

## Event Categories

Voiceground tracks the following event categories:

| Category | Types | Description |
|----------|-------|-------------|
| `user_speak` | `start`, `end` | User speech events |
| `bot_speak` | `start`, `end` | Bot speech events |
| `stt` | `start`, `end` | Speech-to-text processing (includes transcription text) |
| `llm` | `start`, `first_byte`, `end` | LLM response generation (includes generated text) |
| `tts` | `start`, `first_byte`, `end` | Text-to-speech synthesis |
| `tool_call` | `start`, `end` | LLM function/tool calling |
| `system` | `start`, `end` | System events (e.g., context aggregation) |

## Report Features

The generated HTML reports include:

- **Timeline Visualization**: Interactive timeline showing all events and their relationships
- **Events Table**: Detailed view of all tracked events with timestamps, sources, and data
- **Turns Table**: Conversation turns with performance metrics:
  - Response time
  - LLM Time to First Byte (TTFB)
  - TTS latency
  - STT processing time
- **Metrics Summary**: Average metrics across the conversation
- **Event Highlighting**: Hover over events or turns to see related events highlighted

## Examples

See the `examples/` directory for complete working examples:

- **basic_pipeline.py**: Basic voice conversation with STT, LLM, and TTS
- **tool_calling_pipeline.py**: Example with LLM function calling

To run an example:

```bash
# Install example dependencies
uv sync --all-extras

# Set required environment variables
export OPENAI_API_KEY=your_key
export ELEVENLABS_API_KEY=your_key
export VOICE_ID=your_voice_id

# Run the example
python examples/basic_pipeline.py
```

**Note**: On macOS, you'll need to install portaudio for audio support:
```bash
brew install portaudio
```

## Development

```bash
# Clone the repository
git clone https://github.com/poseneror/voiceground.git
cd voiceground

# Install all dependencies (including dev and examples)
uv sync --all-extras

# Run tests
uv run pytest

# Run linting
uv run ruff check .

# Run type checking
uv run mypy src

# Build the client
python scripts/develop.py build

# Run example (requires portaudio on macOS: brew install portaudio)
python scripts/develop.py example
```

## License

BSD-2-Clause License - see [LICENSE](LICENSE) for details.

