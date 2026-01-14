import { formatDuration } from './SessionTimeline';
import { getMetricConfig, getCategoryConfig } from '@/config';
import type { Turn } from '@/types';

interface MetricsSummaryProps {
  turns: Turn[];
}

export function MetricsSummary({ turns }: MetricsSummaryProps) {
  const avgMetrics = {
    responseTime: average(turns.map(t => t.metrics.responseTime)),
    sttLatency: average(turns.map(t => t.metrics.sttLatency)),
    aggregationLatency: average(turns.map(t => t.metrics.aggregationLatency)),
    llmTTFB: average(turns.map(t => t.metrics.llmTTFB)),
    ttsLatency: average(turns.map(t => t.metrics.ttsLatency)),
  };

  const metrics = [
    { 
      key: 'responseTime', 
      value: avgMetrics.responseTime, 
      color: 'text-primary', // Composite metric, uses primary color
    },
    { 
      key: 'sttLatency', 
      value: avgMetrics.sttLatency, 
      color: getCategoryConfig('stt').metricColor,
    },
    { 
      key: 'aggregationLatency', 
      value: avgMetrics.aggregationLatency, 
      color: getCategoryConfig('system').metricColor,
    },
    { 
      key: 'llmTTFB', 
      value: avgMetrics.llmTTFB, 
      color: getCategoryConfig('llm').metricColor,
    },
    { 
      key: 'ttsLatency', 
      value: avgMetrics.ttsLatency, 
      color: getCategoryConfig('tts').metricColor,
    },
  ];

  return (
    <div className="flex items-center gap-4 text-sm">
      {metrics.map(({ key, value, color }) => {
        const config = getMetricConfig(key);
        return (
          <div key={key} className="flex items-center gap-1.5">
            <span className="text-muted-foreground text-xs">{config?.shortLabel || key}:</span>
            <span className={`font-semibold ${color}`}>{formatDuration(value)}</span>
          </div>
        );
      })}
      <span className="text-muted-foreground text-xs">({turns.length} turns)</span>
    </div>
  );
}

function average(values: (number | null)[]): number | null {
  const valid = values.filter((v): v is number => v !== null);
  if (valid.length === 0) return null;
  return valid.reduce((a, b) => a + b, 0) / valid.length;
}

