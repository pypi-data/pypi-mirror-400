import type { EventCategory } from '@/types';

/**
 * Centralized configuration for event categories.
 * This is the single source of truth for category definitions, colors, labels, and ordering.
 */

export interface CategoryConfig {
  /** Display label for the category */
  label: string;
  /** Background color for timeline segments (OKLCH format) */
  timelineColor: string;
  /** Text color for metrics display (OKLCH format) */
  metricColor: string;
  /** Hover background color for metrics (OKLCH format with opacity) */
  metricHoverColor: string;
  /** Description of what this category measures */
  description?: string;
  /** Display order in timeline and other UI elements */
  order: number;
}

export const CATEGORY_CONFIG: Record<EventCategory, CategoryConfig> = {
  user_speak: {
    label: 'User',
    timelineColor: 'bg-[oklch(0.7_0.15_250)]',
    metricColor: 'text-primary',
    metricHoverColor: 'hover:bg-primary/10',
    description: 'User speech events',
    order: 0,
  },
  stt: {
    label: 'STT',
    timelineColor: 'bg-[oklch(0.75_0.15_85)]',
    metricColor: 'text-[oklch(0.82_0.15_85)]',
    metricHoverColor: 'hover:bg-[oklch(0.75_0.15_85/0.1)]',
    description: 'Speech-to-text processing',
    order: 1,
  },
  system: {
    label: 'System',
    timelineColor: 'bg-[oklch(0.6_0.12_45)]',
    metricColor: 'text-[oklch(0.7_0.12_45)]',
    metricHoverColor: 'hover:bg-[oklch(0.6_0.12_45/0.1)]',
    description: 'Context aggregation timeout',
    order: 2,
  },
  llm: {
    label: 'LLM',
    timelineColor: 'bg-[oklch(0.7_0.18_300)]',
    metricColor: 'text-[oklch(0.78_0.18_300)]',
    metricHoverColor: 'hover:bg-[oklch(0.7_0.18_300/0.1)]',
    description: 'LLM response generation',
    order: 3,
  },
  tts: {
    label: 'TTS',
    timelineColor: 'bg-[oklch(0.72_0.18_350)]',
    metricColor: 'text-[oklch(0.8_0.18_350)]',
    metricHoverColor: 'hover:bg-[oklch(0.72_0.18_350/0.1)]',
    description: 'Text-to-speech synthesis',
    order: 4,
  },
  bot_speak: {
    label: 'Bot',
    timelineColor: 'bg-[oklch(0.72_0.19_142)]',
    metricColor: 'text-primary',
    metricHoverColor: 'hover:bg-primary/10',
    description: 'Bot speech events',
    order: 5,
  },
  tool_call: {
    label: 'Tool Call',
    timelineColor: 'bg-[oklch(0.68_0.2_25)]',
    metricColor: 'text-[oklch(0.75_0.2_25)]',
    metricHoverColor: 'hover:bg-[oklch(0.68_0.2_25/0.1)]',
    description: 'LLM function/tool calling',
    order: 3.5, // Between LLM and TTS
  },
};

/**
 * Get category configuration
 */
export function getCategoryConfig(category: EventCategory): CategoryConfig {
  return CATEGORY_CONFIG[category];
}

/**
 * Get category label
 */
export function getCategoryLabel(category: EventCategory): string {
  return CATEGORY_CONFIG[category].label;
}

/**
 * Get category description
 */
export function getCategoryDescription(category: EventCategory): string | undefined {
  return CATEGORY_CONFIG[category].description;
}

/**
 * Get all categories in display order
 */
export function getCategoriesInOrder(): EventCategory[] {
  return Object.entries(CATEGORY_CONFIG)
    .sort(([, a], [, b]) => a.order - b.order)
    .map(([category]) => category as EventCategory);
}

/**
 * Get categories for filtering (includes 'all' option)
 */
export function getFilterCategories(): (EventCategory | 'all')[] {
  return ['all', ...getCategoriesInOrder()];
}

