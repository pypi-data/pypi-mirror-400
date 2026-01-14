import type { EventType } from '@/types';

/**
 * Centralized configuration for event types.
 */

export interface EventTypeConfig {
  /** Display label for the event type */
  label: string;
}

export const EVENT_TYPE_CONFIG: Record<EventType, EventTypeConfig> = {
  start: {
    label: 'Start',
  },
  end: {
    label: 'End',
  },
  first_byte: {
    label: 'First Byte',
  },
};

/**
 * Get event type label
 */
export function getEventTypeLabel(type: EventType): string {
  return EVENT_TYPE_CONFIG[type].label;
}

