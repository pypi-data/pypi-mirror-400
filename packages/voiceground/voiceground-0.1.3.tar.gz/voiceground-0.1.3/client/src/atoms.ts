import { atom } from 'jotai';
import type { EventCategory, EventType, VoicegroundEvent } from '@/types';

/**
 * Unified highlight state for timeline highlighting.
 * Supports both segment highlighting (2 event IDs) and single event highlighting.
 */
export interface SegmentHighlightData {
  type: 'segment';
  startEventId: string;
  endEventId: string;
  turnIndex?: number;
  metric?: string;
}

export interface EventHighlightData {
  type: 'event';
  eventId: string;
}

export type HighlightData = SegmentHighlightData | EventHighlightData | null;

export const highlightAtom = atom<HighlightData>(null);

/**
 * Events atom for managing conversation events
 */
export const eventsAtom = atom<VoicegroundEvent[]>([]);

/**
 * Conversation ID atom for the current conversation session
 */
export const conversationIdAtom = atom<string | null>(null);

/**
 * Version atom for the Voiceground package version
 */
export const versionAtom = atom<string | null>(null);

/**
 * Helper functions for creating highlight data
 */
export function createSegmentHighlight(
  startEventId: string,
  endEventId: string,
  turnIndex?: number,
  metric?: string
): SegmentHighlightData {
  return {
    type: 'segment',
    startEventId,
    endEventId,
    turnIndex,
    metric,
  };
}

export function createEventHighlight(eventId: string): EventHighlightData {
  return {
    type: 'event',
    eventId,
  };
}

