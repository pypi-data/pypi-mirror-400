import { useMemo, useCallback } from 'react';
import { useSetAtom } from 'jotai';
import { highlightAtom, createSegmentHighlight } from '@/atoms';
import { formatDuration } from '@/components/SessionTimeline';
import { getCategoryConfig } from '@/config';
import { DataTable } from '@/components/DataTable';
import type { Turn } from '@/types';

function getMetricEventIds(turn: Turn, metric: string): { startEventId: string; endEventId: string } | null {
  const findEvent = (category: string, type: string) =>
    turn.events.find((e) => e.category === category && e.type === type);
  
  const findAllEvents = (category: string, type: string) =>
    turn.events.filter((e) => e.category === category && e.type === type);

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

  switch (metric) {
    case 'response':
      if (userSpeakEnd && botSpeakStart) {
        // Normal case: user spoke first
        return { startEventId: userSpeakEnd.id, endEventId: botSpeakStart.id };
      } else if (!userSpeakEnd && botSpeakStart) {
        // Conversation started with bot speech: from first event to bot speak start
        const firstEvent = turn.events.sort((a, b) => a.timestamp - b.timestamp)[0];
        if (firstEvent) {
          return { startEventId: firstEvent.id, endEventId: botSpeakStart.id };
        }
      }
      break;
    case 'stt':
      if (userSpeakEnd && sttEnd) return { startEventId: userSpeakEnd.id, endEventId: sttEnd.id };
      break;
    case 'llm':
      if (llmStart && llmFirstByte) return { startEventId: llmStart.id, endEventId: llmFirstByte.id };
      break;
    case 'tts':
      if (ttsStart && botSpeakStart) return { startEventId: ttsStart.id, endEventId: botSpeakStart.id };
      break;
  }
  return null;
}

export interface TurnsTableProps {
  turns: Turn[];
}

export function TurnsTable({ turns }: TurnsTableProps) {
  const setHighlight = useSetAtom(highlightAtom);

  const handleTurnHover = (turnIndex: number) => {
    const turn = turns[turnIndex];
    // Find the first and last events of the turn
    const sortedEvents = [...turn.events].sort((a, b) => a.timestamp - b.timestamp);
    if (sortedEvents.length >= 2) {
      const firstEvent = sortedEvents[0];
      const lastEvent = sortedEvents[sortedEvents.length - 1];
      setHighlight(createSegmentHighlight(firstEvent.id, lastEvent.id, turnIndex, 'turn'));
    }
  };

  const handleTurnLeave = () => {
    setHighlight(null);
  };

  const handleMetricHover = useCallback((turnIndex: number, metric: string) => {
    const turn = turns[turnIndex];
    const eventIds = getMetricEventIds(turn, metric);
    if (eventIds) {
      setHighlight(createSegmentHighlight(eventIds.startEventId, eventIds.endEventId, turnIndex, metric));
    }
  }, [turns, setHighlight]);

  const handleMetricLeave = useCallback(() => {
    setHighlight(null);
  }, [setHighlight]);

  const columns = useMemo(() => [
    {
      header: 'Turn',
      cell: (_turn: Turn, index: number) => (
        <div
          className="w-full h-full flex items-center"
          onMouseEnter={(e) => {
            e.stopPropagation();
            handleTurnHover(index);
          }}
          onMouseLeave={(e) => {
            e.stopPropagation();
            handleTurnLeave();
          }}
        >
          <span className="font-medium">#{index + 1}</span>
        </div>
      ),
      className: 'w-[60px]',
      cellClassName: 'hover:bg-muted/50 transition-colors',
    },
    {
      header: 'Response',
      cell: (turn: Turn, index: number) => (
        <div
          className="w-full h-full flex items-center"
          onMouseEnter={(e) => {
            e.stopPropagation();
            handleMetricHover(index, 'response');
          }}
          onMouseLeave={(e) => {
            e.stopPropagation();
            handleMetricLeave();
          }}
        >
          <span className="text-primary font-semibold cursor-pointer">
            {formatDuration(turn.metrics.responseTime)}
          </span>
        </div>
      ),
      cellClassName: 'hover:bg-primary/10 transition-colors cursor-pointer',
    },
    {
      header: 'STT',
      cell: (turn: Turn, index: number) => (
        <div
          className="w-full h-full flex items-center"
          onMouseEnter={(e) => {
            e.stopPropagation();
            handleMetricHover(index, 'stt');
          }}
          onMouseLeave={(e) => {
            e.stopPropagation();
            handleMetricLeave();
          }}
        >
          <span className={`${getCategoryConfig('stt').metricColor} cursor-pointer`}>
            {formatDuration(turn.metrics.sttLatency)}
          </span>
        </div>
      ),
      cellClassName: `${getCategoryConfig('stt').metricHoverColor} transition-colors cursor-pointer`,
    },
    {
      header: 'LLM TTFB',
      cell: (turn: Turn, index: number) => (
        <div
          className="w-full h-full flex items-center"
          onMouseEnter={(e) => {
            e.stopPropagation();
            handleMetricHover(index, 'llm');
          }}
          onMouseLeave={(e) => {
            e.stopPropagation();
            handleMetricLeave();
          }}
        >
          <span className={`${getCategoryConfig('llm').metricColor} cursor-pointer`}>
            {formatDuration(turn.metrics.llmTTFB)}
          </span>
        </div>
      ),
      cellClassName: `${getCategoryConfig('llm').metricHoverColor} transition-colors cursor-pointer`,
    },
    {
      header: 'TTS',
      cell: (turn: Turn, index: number) => (
        <div
          className="w-full h-full flex items-center"
          onMouseEnter={(e) => {
            e.stopPropagation();
            handleMetricHover(index, 'tts');
          }}
          onMouseLeave={(e) => {
            e.stopPropagation();
            handleMetricLeave();
          }}
        >
          <span className={`${getCategoryConfig('tts').metricColor} cursor-pointer`}>
            {formatDuration(turn.metrics.ttsLatency)}
          </span>
        </div>
      ),
      cellClassName: `${getCategoryConfig('tts').metricHoverColor} transition-colors cursor-pointer`,
    },
    {
      header: 'Total',
      cell: (turn: Turn, index: number) => (
        <div
          className="w-full h-full flex items-center justify-end"
          onMouseEnter={(e) => {
            e.stopPropagation();
            handleTurnHover(index);
          }}
          onMouseLeave={(e) => {
            e.stopPropagation();
            handleTurnLeave();
          }}
        >
          <span className="text-right text-muted-foreground">
            {formatDuration(turn.metrics.totalDuration)}
          </span>
        </div>
      ),
      className: 'text-right w-[100px]',
      cellClassName: 'hover:bg-muted/50 transition-colors',
    },
  ], [handleMetricHover, handleMetricLeave]);

  if (turns.length === 0) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center text-muted-foreground">
          <p className="font-medium mb-1">No turns recorded</p>
          <p className="text-xs">No conversation turns have been detected yet.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col min-h-0 overflow-hidden">
      <DataTable
        columns={columns}
        data={turns}
        emptyMessage="No turns recorded"
        onRowMouseEnter={(_turn, index) => handleTurnHover(index)}
        onRowMouseLeave={() => handleTurnLeave()}
        rowClassName={() => 'cursor-pointer'}
        getRowKey={(turn) => turn.id}
      />
      <p className="text-xs text-muted-foreground mt-4 flex-shrink-0">
        Hover over metrics to highlight in timeline
      </p>
    </div>
  );
}

