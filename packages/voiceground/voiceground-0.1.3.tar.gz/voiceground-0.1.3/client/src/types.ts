export type EventCategory = 'user_speak' | 'bot_speak' | 'stt' | 'llm' | 'tts' | 'tool_call' | 'system';
export type EventType = 'start' | 'end' | 'first_byte';

export interface VoicegroundEvent {
  id: string;
  timestamp: number;
  category: EventCategory;
  type: EventType;
  source: string;
  data: Record<string, unknown>;
}

export interface Turn {
  id: number;
  startTime: number;
  endTime: number;
  events: VoicegroundEvent[];
  metrics: TurnMetrics;
}

export interface TurnMetrics {
  totalDuration: number;
  /** Response Time: user_speak:end → bot_speak:start */
  responseTime: number | null;
  /** STT Latency: user_speak:end → stt:end */
  sttLatency: number | null;
  /** TTS Latency: tts:start → bot_speak:start */
  ttsLatency: number | null;
  /** LLM TTFB: llm:start → llm:first_byte */
  llmTTFB: number | null;
  /** Context Aggregation: stt:end → llm:start (system category) */
  aggregationLatency: number | null;
}

declare global {
  interface Window {
    __VOICEGROUND_EVENTS__?: VoicegroundEvent[];
    __VOICEGROUND_CONVERSATION_ID__?: string;
    __VOICEGROUND_VERSION__?: string;
  }
}

