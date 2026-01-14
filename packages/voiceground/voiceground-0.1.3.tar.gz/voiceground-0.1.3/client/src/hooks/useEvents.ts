import { useEffect } from 'react';
import { useAtomValue, useSetAtom } from 'jotai';
import { eventsAtom, conversationIdAtom, versionAtom } from '@/atoms';
import type { VoicegroundEvent } from '@/types';

// Mock data for development - real data from actual run
const mockEvents: VoicegroundEvent[] = [
  {"id": "mock-1", "timestamp": 0.290882416, "category": "llm", "type": "start", "source": "PipelineTask#0::Source", "data": {}},
  {"id": "mock-2", "timestamp": 0.291378125, "category": "system", "type": "end", "source": "OpenAIUserContextAggregator#0", "data": {"operation": "context_aggregation_timeout"}},
  {"id": "mock-3", "timestamp": 1.076857541, "category": "llm", "type": "first_byte", "source": "OpenAILLMService#0", "data": {}},
  {"id": "mock-4", "timestamp": 1.132370583, "category": "tts", "type": "start", "source": "ElevenLabsTTSService#0", "data": {}},
  {"id": "mock-5", "timestamp": 1.254451958, "category": "llm", "type": "end", "source": "OpenAILLMService#0", "data": {"text": "How can I assist you today? Would you like to know the weather for a specific location or the current time in a particular timezone?"}},
  {"id": "mock-6", "timestamp": 1.6670395, "category": "tts", "type": "first_byte", "source": "ElevenLabsTTSService#0", "data": {}},
  {"id": "mock-7", "timestamp": 1.667501416, "category": "bot_speak", "type": "start", "source": "LocalAudioOutputTransport#0", "data": {}},
  {"id": "mock-8", "timestamp": 4.080993541, "category": "tts", "type": "end", "source": "ElevenLabsTTSService#0", "data": {}},
  {"id": "mock-9", "timestamp": 9.257692333, "category": "bot_speak", "type": "end", "source": "LocalAudioOutputTransport#0", "data": {}},
  {"id": "mock-10", "timestamp": 10.636748666, "category": "stt", "type": "start", "source": "LocalAudioInputTransport#0", "data": {}},
  {"id": "mock-11", "timestamp": 10.637166666, "category": "user_speak", "type": "start", "source": "LocalAudioInputTransport#0", "data": {}},
  {"id": "mock-12", "timestamp": 14.257418083, "category": "user_speak", "type": "end", "source": "LocalAudioInputTransport#0", "data": {}},
  {"id": "mock-13", "timestamp": 15.269120833, "category": "stt", "type": "end", "source": "ElevenLabsSTTService#0", "data": {"text": "Uh, yeah. What's the time right now in San Francisco?"}},
  {"id": "mock-14", "timestamp": 15.269120833, "category": "system", "type": "start", "source": "ElevenLabsSTTService#0", "data": {"operation": "context_aggregation_timeout"}},
  {"id": "mock-15", "timestamp": 15.771704583, "category": "llm", "type": "start", "source": "OpenAIUserContextAggregator#0", "data": {}},
  {"id": "mock-16", "timestamp": 15.771704583, "category": "system", "type": "end", "source": "OpenAIUserContextAggregator#0", "data": {"operation": "context_aggregation_timeout"}},
  {"id": "mock-17", "timestamp": 16.424664666, "category": "tool_call", "type": "start", "source": "OpenAILLMService#0", "data": {"description": "get_current_time", "operation": "get_current_time"}},
  {"id": "mock-18", "timestamp": 16.424751583, "category": "llm", "type": "end", "source": "OpenAILLMService#0", "data": {}},
  {"id": "mock-19", "timestamp": 16.726329583, "category": "tool_call", "type": "end", "source": "OpenAILLMService#0", "data": {"operation": "get_current_time"}},
  {"id": "mock-20", "timestamp": 16.726383916, "category": "tool_call", "type": "end", "source": "OpenAILLMService#0", "data": {"operation": "get_current_time"}},
  {"id": "mock-21", "timestamp": 16.727469416, "category": "llm", "type": "start", "source": "OpenAIAssistantContextAggregator#0", "data": {}},
  {"id": "mock-22", "timestamp": 17.234462666, "category": "llm", "type": "first_byte", "source": "OpenAILLMService#0", "data": {}},
  {"id": "mock-23", "timestamp": 17.333043125, "category": "tts", "type": "start", "source": "ElevenLabsTTSService#0", "data": {}},
  {"id": "mock-24", "timestamp": 17.3737825, "category": "llm", "type": "end", "source": "OpenAILLMService#0", "data": {"text": "The current time in San Francisco is 4:25 PM. Anything else you need?"}},
  {"id": "mock-25", "timestamp": 17.749930333, "category": "tts", "type": "first_byte", "source": "ElevenLabsTTSService#0", "data": {}},
  {"id": "mock-26", "timestamp": 17.752082875, "category": "bot_speak", "type": "start", "source": "LocalAudioOutputTransport#0", "data": {}},
  {"id": "mock-27", "timestamp": 19.864860333, "category": "tts", "type": "end", "source": "ElevenLabsTTSService#0", "data": {}},
  {"id": "mock-28", "timestamp": 22.501305541, "category": "bot_speak", "type": "end", "source": "LocalAudioOutputTransport#0", "data": {}},
  {"id": "mock-29", "timestamp": 22.656265833, "category": "stt", "type": "start", "source": "LocalAudioInputTransport#0", "data": {}},
  {"id": "mock-30", "timestamp": 22.656596625, "category": "user_speak", "type": "start", "source": "LocalAudioInputTransport#0", "data": {}},
  {"id": "mock-31", "timestamp": 25.696341708, "category": "user_speak", "type": "end", "source": "LocalAudioInputTransport#0", "data": {}},
  {"id": "mock-32", "timestamp": 26.444263333, "category": "stt", "type": "end", "source": "ElevenLabsSTTService#0", "data": {"text": "Yeah, and, uh, what's the weather tomorrow?"}},
  {"id": "mock-33", "timestamp": 26.444263333, "category": "system", "type": "start", "source": "ElevenLabsSTTService#0", "data": {"operation": "context_aggregation_timeout"}},
  {"id": "mock-34", "timestamp": 26.949366958, "category": "llm", "type": "start", "source": "OpenAIUserContextAggregator#0", "data": {}},
  {"id": "mock-35", "timestamp": 26.949366958, "category": "system", "type": "end", "source": "OpenAIUserContextAggregator#0", "data": {"operation": "context_aggregation_timeout"}},
  {"id": "mock-36", "timestamp": 27.639192083, "category": "tool_call", "type": "start", "source": "OpenAILLMService#0", "data": {"description": "get_weather", "operation": "get_weather"}},
  {"id": "mock-37", "timestamp": 27.639321541, "category": "llm", "type": "end", "source": "OpenAILLMService#0", "data": {}},
  {"id": "mock-38", "timestamp": 27.940094958, "category": "tool_call", "type": "end", "source": "OpenAILLMService#0", "data": {"operation": "get_weather"}},
  {"id": "mock-39", "timestamp": 27.940170291, "category": "tool_call", "type": "end", "source": "OpenAILLMService#0", "data": {"operation": "get_weather"}},
  {"id": "mock-40", "timestamp": 27.942631458, "category": "llm", "type": "start", "source": "OpenAIAssistantContextAggregator#0", "data": {}},
  {"id": "mock-41", "timestamp": 28.473226833, "category": "llm", "type": "first_byte", "source": "OpenAILLMService#0", "data": {}},
  {"id": "mock-42", "timestamp": 28.609573083, "category": "tts", "type": "start", "source": "ElevenLabsTTSService#0", "data": {}},
  {"id": "mock-43", "timestamp": 28.668592, "category": "llm", "type": "end", "source": "OpenAILLMService#0", "data": {"text": "Tomorrow's weather in San Francisco is expected to be sunny with a temperature of 72°F. Let me know if you need anything else!"}},
  {"id": "mock-44", "timestamp": 29.116634958, "category": "tts", "type": "first_byte", "source": "ElevenLabsTTSService#0", "data": {}},
  {"id": "mock-45", "timestamp": 29.121004208, "category": "bot_speak", "type": "start", "source": "LocalAudioOutputTransport#0", "data": {}},
  {"id": "mock-46", "timestamp": 31.259360041, "category": "tts", "type": "end", "source": "ElevenLabsTTSService#0", "data": {}},
  {"id": "mock-47", "timestamp": 36.667614625, "category": "bot_speak", "type": "end", "source": "LocalAudioOutputTransport#0", "data": {}},
  {"id": "mock-48", "timestamp": 38.276199833, "category": "stt", "type": "start", "source": "LocalAudioInputTransport#0", "data": {}},
  {"id": "mock-49", "timestamp": 38.276563166, "category": "user_speak", "type": "start", "source": "LocalAudioInputTransport#0", "data": {}},
  {"id": "mock-50", "timestamp": 40.195933875, "category": "user_speak", "type": "end", "source": "LocalAudioInputTransport#0", "data": {}},
  {"id": "mock-51", "timestamp": 40.838493333, "category": "stt", "type": "end", "source": "ElevenLabsSTTService#0", "data": {"text": "That would be all. Thank you."}},
  {"id": "mock-52", "timestamp": 40.838493333, "category": "system", "type": "start", "source": "ElevenLabsSTTService#0", "data": {"operation": "context_aggregation_timeout"}},
  {"id": "mock-53", "timestamp": 41.343478916, "category": "llm", "type": "start", "source": "OpenAIUserContextAggregator#0", "data": {}},
  {"id": "mock-54", "timestamp": 41.343478916, "category": "system", "type": "end", "source": "OpenAIUserContextAggregator#0", "data": {"operation": "context_aggregation_timeout"}},
  {"id": "mock-55", "timestamp": 41.868119833, "category": "llm", "type": "first_byte", "source": "OpenAILLMService#0", "data": {}},
  {"id": "mock-56", "timestamp": 41.887865083, "category": "tts", "type": "start", "source": "ElevenLabsTTSService#0", "data": {}},
  {"id": "mock-57", "timestamp": 42.023623958, "category": "llm", "type": "end", "source": "OpenAILLMService#0", "data": {"text": "You're welcome! If you have any more questions in the future, feel free to ask. Have a great day! 😊"}},
  {"id": "mock-58", "timestamp": 42.231152791, "category": "tts", "type": "first_byte", "source": "ElevenLabsTTSService#0", "data": {}},
  {"id": "mock-59", "timestamp": 42.2321385, "category": "bot_speak", "type": "start", "source": "LocalAudioOutputTransport#0", "data": {}},
  {"id": "mock-60", "timestamp": 44.728557666, "category": "tts", "type": "end", "source": "ElevenLabsTTSService#0", "data": {}},
  {"id": "mock-61", "timestamp": 48.858700375, "category": "bot_speak", "type": "end", "source": "LocalAudioOutputTransport#0", "data": {}}
] as VoicegroundEvent[];

/**
 * Hook for managing events state using Jotai atoms.
 * Initializes events from window.__VOICEGROUND_EVENTS__ or uses mock data in development.
 */
export function useEvents() {
  const events = useAtomValue(eventsAtom);
  const setEvents = useSetAtom(eventsAtom);
  const setConversationId = useSetAtom(conversationIdAtom);
  const setVersion = useSetAtom(versionAtom);

  useEffect(() => {
    // Check for embedded events from HTMLReporter
    if (window.__VOICEGROUND_EVENTS__) {
      setEvents(window.__VOICEGROUND_EVENTS__);
    } else if (import.meta.env.DEV) {
      // Use mock data only in development mode
      setEvents(mockEvents);
    } else {
      // In production, start with empty array if no events are provided
      setEvents([]);
    }

    // Load conversation ID if available
    if (typeof window !== 'undefined' && window.__VOICEGROUND_CONVERSATION_ID__) {
      setConversationId(window.__VOICEGROUND_CONVERSATION_ID__);
    }

    // Load version if available
    if (typeof window !== 'undefined' && window.__VOICEGROUND_VERSION__) {
      setVersion(window.__VOICEGROUND_VERSION__);
    }
  }, [setEvents, setConversationId, setVersion]);

  const isMockData = !window.__VOICEGROUND_EVENTS__ && import.meta.env.DEV;

  return {
    events,
    isMockData,
  };
}

