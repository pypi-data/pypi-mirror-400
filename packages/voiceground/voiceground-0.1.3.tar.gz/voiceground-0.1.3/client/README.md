# Voiceground Client

A React-based visualization client for Voiceground conversation analytics. Displays post-conversation reports with interactive timelines, turn-by-turn metrics, and event tracking.

## Features

- **Turns View**: Per-turn breakdown with metrics (Response Time, STT Latency, LLM TTFB, TTS Latency)
- **Events View**: Detailed timeline of all conversation events with filtering
- **Session Timeline**: Interactive timeline visualization with hover details
- **Centralized Configuration**: Event categories, colors, and labels managed in a single config system

## Tech Stack

- **React 19** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **Jotai** for state management
- **Radix UI** components (Popover, ScrollArea, etc.)

## Project Structure

```
src/
├── components/          # React components
│   ├── ui/             # Reusable UI components (shadcn/ui style)
│   ├── AppHeader.tsx   # Application header with view toggle
│   ├── AppFooter.tsx   # Footer with session timeline
│   ├── EventsTable.tsx # Events table with filtering
│   ├── TurnsTable.tsx  # Per-turn metrics table
│   ├── SessionTimeline.tsx # Interactive timeline visualization
│   └── ...
├── config/             # Centralized configuration
│   ├── eventCategories.ts # Category definitions, colors, labels
│   ├── eventTypes.ts      # Event type definitions
│   └── metrics.ts         # Metric definitions
├── atoms.ts            # Jotai state atoms
├── types.ts            # TypeScript type definitions
└── App.tsx             # Main application component
```

## Getting Started

### Prerequisites

- Node.js (see `.nvmrc` for version)
- npm or yarn

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build

```bash
npm run build
```

Builds the app for production to the `dist` folder. The build is configured to create a single-file output suitable for embedding in static HTML reports.

## Configuration

The client uses a centralized configuration system located in `src/config/`:

- **Event Categories**: Colors, labels, descriptions, and display order are defined in `config/eventCategories.ts`
- **Event Types**: Type labels are defined in `config/eventTypes.ts`
- **Metrics**: Metric definitions and labels are in `config/metrics.ts`

To modify colors, labels, or add new categories, update the configuration files rather than hardcoding values in components.

## Data Format

The client expects events in the following format (embedded via `window.__VOICEGROUND_EVENTS__`):

```typescript
interface VoicegroundEvent {
  timestamp: number;
  category: 'user_speak' | 'bot_speak' | 'stt' | 'llm' | 'tts' | 'system';
  type: 'start' | 'end' | 'first_byte';
  data: Record<string, unknown>;
}
```

## Development Notes

### TypeScript Configuration

This project uses a single `tsconfig.json` file (not the split `tsconfig.app.json` / `tsconfig.node.json` pattern). The configuration handles both React source code and Vite build configuration.

### ESLint Configuration

If you want to expand the ESLint configuration for type-aware rules, update `eslint.config.js`:

```js
      parserOptions: {
  project: ['./tsconfig.json'], // Single config file
        tsconfigRootDir: import.meta.dirname,
}
```

## License

See the main project LICENSE file.
