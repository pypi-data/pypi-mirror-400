import { useMemo } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { SessionTimeline, formatDuration } from '@/components/SessionTimeline';
import { TurnsTable } from '@/components/TurnsTable';
import type { VoicegroundEvent, Turn, TurnMetrics } from '@/types';

interface TurnsViewProps {
  events: VoicegroundEvent[];
}

export function parseTurns(events: VoicegroundEvent[]): Turn[] {
  if (events.length === 0) return [];

  const sortedEvents = [...events].sort((a, b) => a.timestamp - b.timestamp);
  const turns: Turn[] = [];
  let currentTurn: Turn | null = null;
  let turnId = 0;

  for (const event of sortedEvents) {
    if (event.category === 'user_speak' && event.type === 'start') {
      if (currentTurn) {
        // Close the current turn at its last event's timestamp (not the user_speak start)
        // This ensures bot_speak end events that occur after user_speak start but belong
        // to the previous turn are handled correctly
        if (currentTurn.events.length > 0) {
          currentTurn.endTime = currentTurn.events[currentTurn.events.length - 1].timestamp;
        }
        currentTurn.metrics = calculateMetrics(currentTurn.events);
        turns.push(currentTurn);
      }
      currentTurn = {
        id: turnId++,
        startTime: event.timestamp,
        endTime: event.timestamp,
        events: [event],
        metrics: {} as TurnMetrics,
      };
    } else if (currentTurn) {
      // Check if this event belongs to the previous turn (bot_speak end that should close previous turn)
      // This happens when bot_speak end occurs after user_speak start
      if (event.category === 'bot_speak' && event.type === 'end' && turns.length > 0) {
        const lastTurn = turns[turns.length - 1];
        // If this bot_speak end is within 0.1 seconds of the last turn's end, it belongs to that turn
        if (event.timestamp - lastTurn.endTime < 0.1) {
          lastTurn.events.push(event);
          lastTurn.endTime = event.timestamp;
          lastTurn.metrics = calculateMetrics(lastTurn.events);
          continue;
        }
      }
      
      currentTurn.events.push(event);
      currentTurn.endTime = event.timestamp;

      if (event.category === 'bot_speak' && event.type === 'end') {
        currentTurn.metrics = calculateMetrics(currentTurn.events);
        turns.push(currentTurn);
        currentTurn = null;
      }
    } else {
      // If no current turn and no turns yet, start a turn on the first event
      // This handles cases where the conversation starts with bot speech
      if (turns.length === 0) {
        currentTurn = {
          id: turnId++,
          startTime: event.timestamp,
          endTime: event.timestamp,
          events: [event],
          metrics: {} as TurnMetrics,
        };
      } else {
        // If there are existing turns, try to add to the last one if within 2 seconds
        const lastTurn = turns[turns.length - 1];
        if (event.timestamp - lastTurn.endTime < 2) {
          lastTurn.events.push(event);
          lastTurn.endTime = event.timestamp;
          lastTurn.metrics = calculateMetrics(lastTurn.events);
        }
      }
    }
  }

  if (currentTurn) {
    currentTurn.metrics = calculateMetrics(currentTurn.events);
    turns.push(currentTurn);
  }

  return turns;
}

function calculateMetrics(events: VoicegroundEvent[]): TurnMetrics {
  const findEvent = (category: string, type: string) =>
    events.find((e) => e.category === category && e.type === type);
  
  const findAllEvents = (category: string, type: string) =>
    events.filter((e) => e.category === category && e.type === type);

  const userSpeakEnd = findEvent('user_speak', 'end');
  const sttEnd = findEvent('stt', 'end');
  const llmFirstByte = findEvent('llm', 'first_byte');
  const ttsStart = findEvent('tts', 'start');
  const botSpeakStart = findEvent('bot_speak', 'start');

  // Use the first LLM start for metrics (even if there are multiple LLM calls)
  const llmStarts = findAllEvents('llm', 'start');
  const llmStart = llmStarts.length > 0
    ? llmStarts.sort((a, b) => a.timestamp - b.timestamp)[0]  // First LLM start
    : undefined;

  const duration = (start?: VoicegroundEvent, end?: VoicegroundEvent) =>
    start && end ? (end.timestamp - start.timestamp) * 1000 : null;

  const firstEventTime = Math.min(...events.map((e) => e.timestamp));
  const lastEventTime = Math.max(...events.map((e) => e.timestamp));

  // Calculate response time: from user_speak end to bot_speak start
  // If no user_speak end (conversation started with bot), use first event to bot_speak start
  let responseTime: number | null = null;
  if (userSpeakEnd && botSpeakStart) {
    responseTime = duration(userSpeakEnd, botSpeakStart);
  } else if (!userSpeakEnd && botSpeakStart) {
    // Conversation started with bot speech - measure from first event to bot speak start
    responseTime = (botSpeakStart.timestamp - firstEventTime) * 1000;
  }

  return {
    totalDuration: (lastEventTime - firstEventTime) * 1000,
    responseTime,
    sttLatency: duration(userSpeakEnd, sttEnd),
    ttsLatency: duration(ttsStart, botSpeakStart),
    llmTTFB: duration(llmStart, llmFirstByte),
    aggregationLatency: duration(sttEnd, llmStart),
  };
}

export function average(values: (number | null)[]): number | null {
  const valid = values.filter((v): v is number => v !== null);
  if (valid.length === 0) return null;
  return valid.reduce((a, b) => a + b, 0) / valid.length;
}

export function TurnsView({ events }: TurnsViewProps) {
  const turns = useMemo(() => parseTurns(events), [events]);

  if (events.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        No events recorded
      </div>
    );
  }

  const minTime = Math.min(...events.map((e) => e.timestamp));
  const maxTime = Math.max(...events.map((e) => e.timestamp));
  const totalDuration = (maxTime - minTime) * 1000;

  return (
    <div className="space-y-6">
      {/* Session Timeline */}
      <Card className="bg-card border-border/50">
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold">Session Timeline</h3>
            <span className="text-xs text-muted-foreground">
              {formatDuration(totalDuration)} total • {turns.length} turns
            </span>
          </div>
          <SessionTimeline events={events} />
        </CardContent>
      </Card>

      {/* Per-Turn Metrics Table */}
      <TurnsTable turns={turns} />
    </div>
  );
}

// Re-export for convenience
export { formatDuration } from '@/components/SessionTimeline';
export { SessionTimeline } from '@/components/SessionTimeline';
export { TurnsTable } from '@/components/TurnsTable';
