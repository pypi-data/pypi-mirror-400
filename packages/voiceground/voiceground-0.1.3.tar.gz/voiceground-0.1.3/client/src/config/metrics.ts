/**
 * Centralized configuration for metrics display.
 */

export interface MetricConfig {
  /** Display label */
  label: string;
  /** Short label for compact display */
  shortLabel: string;
  /** Description of what this metric measures */
  description: string;
}

export const METRIC_CONFIG: Record<string, MetricConfig> = {
  responseTime: {
    label: 'Response',
    shortLabel: 'Response',
    description: 'Time from user speech end to bot speech start',
  },
  sttLatency: {
    label: 'STT',
    shortLabel: 'STT',
    description: 'Speech-to-text processing latency',
  },
  aggregationLatency: {
    label: 'System',
    shortLabel: 'System',
    description: 'Context aggregation latency',
  },
  llmTTFB: {
    label: 'TTFB',
    shortLabel: 'TTFB',
    description: 'LLM time to first byte',
  },
  ttsLatency: {
    label: 'TTS',
    shortLabel: 'TTS',
    description: 'Text-to-speech synthesis latency',
  },
};

/**
 * Get metric configuration
 */
export function getMetricConfig(metricKey: string): MetricConfig | undefined {
  return METRIC_CONFIG[metricKey];
}

/**
 * Get metric label
 */
export function getMetricLabel(metricKey: string): string {
  return METRIC_CONFIG[metricKey]?.label || metricKey;
}

