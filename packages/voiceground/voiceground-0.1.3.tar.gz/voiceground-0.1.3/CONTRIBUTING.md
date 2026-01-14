# Contributing to Voiceground

Thank you for your interest in contributing to Voiceground!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/poseneror/voiceground.git
   cd voiceground
   ```

2. Install UV (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. Install dependencies:
   ```bash
   uv sync --group dev
   ```

4. Install the React client dependencies:
   ```bash
   cd client && npm install && cd ..
   ```

## Project Structure

```
voiceground/
├── src/voiceground/       # Python package
│   ├── observer.py        # VoicegroundObserver implementation
│   ├── events.py          # Event dataclasses
│   └── reporters/         # Reporter implementations
├── client/                # React client source
├── scripts/               # Development scripts
└── examples/              # Example pipelines
```

## Running Tests

```bash
uv run pytest
```

## Building the Client

```bash
python scripts/develop.py build
```

## Code Style

- Follow PEP 8 for Python code
- Use type hints for all function signatures
- Write docstrings for public APIs

## Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`uv run pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

By contributing, you agree that your contributions will be licensed under the BSD-2-Clause License.

