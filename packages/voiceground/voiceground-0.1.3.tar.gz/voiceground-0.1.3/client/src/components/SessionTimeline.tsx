import { useMemo, useRef, useEffect, useState, useCallback } from 'react';
import { useAtomValue } from 'jotai';
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area';
import { getCategoriesInOrder, getCategoryConfig, getCategoryDescription } from '@/config';
import { highlightAtom } from '@/atoms';
import type { VoicegroundEvent, EventCategory } from '@/types';

interface Segment {
  category: EventCategory;
  startTime: number;
  endTime: number;
  operation?: string;
  text?: string;
}

function parseSegments(events: VoicegroundEvent[]): Segment[] {
  if (events.length === 0) return [];

  const sortedEvents = [...events].sort((a, b) => a.timestamp - b.timestamp);
  const segments: Segment[] = [];
  const openSegments: Map<EventCategory, { startTime: number; operation?: string }> = new Map();

  for (const event of sortedEvents) {
    if (event.type === 'start') {
      const operation = event.data.operation as string | undefined;
      openSegments.set(event.category, { startTime: event.timestamp, operation });
    } else if (event.type === 'end') {
      const segmentData = openSegments.get(event.category);
      if (segmentData !== undefined) {
        const text = event.data.text as string | undefined;
        segments.push({
          category: event.category,
          startTime: segmentData.startTime,
          endTime: event.timestamp,
          operation: segmentData.operation,
          text,
        });
        openSegments.delete(event.category);
      }
    }
  }

  return segments;
}

export function formatDuration(ms: number | null): string {
  if (ms === null) return '—';
  if (ms < 1000) return `${Math.round(ms)}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

// Re-export for backward compatibility
export const categoryDescriptions: Partial<Record<EventCategory, string>> = Object.fromEntries(
  getCategoriesInOrder()
    .map(cat => [cat, getCategoryDescription(cat)])
    .filter(([, desc]) => desc !== undefined)
) as Partial<Record<EventCategory, string>>;

const MIN_VISIBLE_DURATION = 10; // 10 seconds visible at max zoom

export interface SessionTimelineProps {
  events: VoicegroundEvent[];
}

interface CursorData {
  time: number;
  intersectedSegments: Segment[];
}

export function SessionTimeline({ events }: SessionTimelineProps) {
  const highlight = useAtomValue(highlightAtom);
  const segments = useMemo(() => parseSegments(events), [events]);
  const scrollRef = useRef<HTMLDivElement>(null);
  const timelineRef = useRef<HTMLDivElement>(null);
  const cursorLineRef = useRef<HTMLDivElement>(null);
  const cursorTimeRef = useRef<HTMLDivElement>(null);
  const popoverRef = useRef<HTMLDivElement>(null);
  const [isHovering, setIsHovering] = useState(false);
  const [cursorData, setCursorData] = useState<CursorData | null>(null);
  const [zoomLevel, setZoomLevel] = useState(1); // 1 = max zoom (10s visible), 0 = min zoom (entire conversation)
  const [viewportWidth, setViewportWidth] = useState(1000);
  const debounceTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  
  // Create a map of event IDs to events for quick lookup
  const eventsById = useMemo(() => {
    const map = new Map<string, VoicegroundEvent>();
    events.forEach(event => map.set(event.id, event));
    return map;
  }, [events]);
  
  const minTime = useMemo(() => Math.min(...events.map((e) => e.timestamp)), [events]);
  const maxTime = useMemo(() => Math.max(...events.map((e) => e.timestamp)), [events]);
  const duration = maxTime - minTime;
  
  // Calculate visible duration and pixels per second based on zoom
  const visibleDuration = useMemo(() => {
    if (duration <= MIN_VISIBLE_DURATION) return MIN_VISIBLE_DURATION;
    return MIN_VISIBLE_DURATION + (duration - MIN_VISIBLE_DURATION) * (1 - zoomLevel);
  }, [duration, zoomLevel]);
  
  const pixelsPerSecond = useMemo(() => {
    return viewportWidth / visibleDuration;
  }, [viewportWidth, visibleDuration]);
  
  // Update viewport width on resize
  useEffect(() => {
    const updateViewportWidth = () => {
      // scrollRef.current is the viewport element (ScrollArea forwards ref to Viewport)
      if (scrollRef.current) {
        const width = scrollRef.current.clientWidth;
        if (width > 0) {
          setViewportWidth(width);
        }
      }
    };
    
    updateViewportWidth();
    const resizeObserver = new ResizeObserver(updateViewportWidth);
    if (scrollRef.current) {
      resizeObserver.observe(scrollRef.current);
    }
    window.addEventListener('resize', updateViewportWidth);
    return () => {
      resizeObserver.disconnect();
      window.removeEventListener('resize', updateViewportWidth);
    };
  }, []);
  
  // Handle zoom with mouse wheel
  const handleWheel = useCallback((e: React.WheelEvent<HTMLDivElement>) => {
    if (!e.ctrlKey && !e.metaKey) return; // Only zoom with Ctrl/Cmd + wheel
    
    e.preventDefault();
    e.stopPropagation();
    
    const zoomDelta = e.deltaY > 0 ? -0.1 : 0.1;
    setZoomLevel((prev) => {
      const newZoom = Math.max(0, Math.min(1, prev + zoomDelta));
      return newZoom;
    });
  }, []);

  // Adjust zoom and scroll to highlight when highlight changes (debounced)
  useEffect(() => {
    if (!highlight || !scrollRef.current) return;
    
    const updateZoomAndScroll = () => {
      if (!scrollRef.current) return;
      
      const viewportWidth = scrollRef.current.clientWidth;
      if (viewportWidth === 0) return;
      
      let highlightStart: number;
      let highlightEnd: number;
      
      if (highlight.type === 'segment') {
        // Find events by ID
        const startEvent = eventsById.get(highlight.startEventId);
        const endEvent = eventsById.get(highlight.endEventId);
        if (!startEvent || !endEvent) return;
        highlightStart = startEvent.timestamp;
        highlightEnd = endEvent.timestamp;
      } else {
        // event type - find event by ID and show a small window around it
        const event = eventsById.get(highlight.eventId);
        if (!event) return;
        highlightStart = event.timestamp - 0.5;
        highlightEnd = event.timestamp + 0.5;
      }
      
      const highlightDuration = highlightEnd - highlightStart;
      
      // Always calculate the minimum required zoom level to show the highlight with some padding
      const padding = 2; // 2 seconds padding on each side
      const requiredVisibleDuration = highlightDuration + (padding * 2);
      
      // Calculate target zoom level
      let targetZoomLevel: number;
      if (duration <= MIN_VISIBLE_DURATION) {
        targetZoomLevel = 1; // Already at max zoom
      } else {
        // Solve: requiredVisibleDuration = MIN_VISIBLE_DURATION + (duration - MIN_VISIBLE_DURATION) * (1 - zoomLevel)
        // Rearranged: zoomLevel = 1 - (requiredVisibleDuration - MIN_VISIBLE_DURATION) / (duration - MIN_VISIBLE_DURATION)
        const zoomRange = duration - MIN_VISIBLE_DURATION;
        const requiredZoomRange = requiredVisibleDuration - MIN_VISIBLE_DURATION;
        targetZoomLevel = Math.max(0, Math.min(1, 1 - (requiredZoomRange / zoomRange)));
      }
      
      // Only update zoom if it's different (to avoid unnecessary re-renders)
      if (Math.abs(targetZoomLevel - zoomLevel) > 0.01) {
        setZoomLevel(targetZoomLevel);
      }
      
      // Scroll to center the highlight after zoom updates
      const centerTime = (highlightStart + highlightEnd) / 2;
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          if (scrollRef.current) {
            const newVisibleDuration = MIN_VISIBLE_DURATION + (duration - MIN_VISIBLE_DURATION) * (1 - targetZoomLevel);
            const newPixelsPerSecond = viewportWidth / newVisibleDuration;
            const scrollPosition = (centerTime - minTime) * newPixelsPerSecond - scrollRef.current.clientWidth / 2;
            scrollRef.current.scrollTo({ left: Math.max(0, scrollPosition), behavior: 'smooth' });
          }
        });
      });
    };
    
    // Debounce the zoom/scroll updates to prevent excessive animations
    const DEBOUNCE_DELAY = 150; // ms
    
    // Clear any existing timeout
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
    }
    
    // Set new timeout
    debounceTimeoutRef.current = setTimeout(() => {
      updateZoomAndScroll();
      debounceTimeoutRef.current = null;
    }, DEBOUNCE_DELAY);
    
    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
        debounceTimeoutRef.current = null;
      }
    };
  }, [highlight, minTime, duration, zoomLevel, eventsById]);

  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    if (!timelineRef.current) return;
    
    const rect = timelineRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const time = minTime + x / pixelsPerSecond;
    
    // Update cursor line position directly via DOM (smooth, no re-render)
    if (cursorLineRef.current) {
      cursorLineRef.current.style.transform = `translateX(${x}px)`;
    }
    if (popoverRef.current) {
      popoverRef.current.style.transform = `translateX(${x + 12}px)`;
    }
    if (cursorTimeRef.current) {
      cursorTimeRef.current.textContent = `${(time - minTime).toFixed(2)}s`;
    }
    
    // Find segments that intersect with the cursor time (debounced via state)
    const intersected = segments.filter(
      (seg) => time >= seg.startTime && time <= seg.endTime
    );
    
    setCursorData({ time, intersectedSegments: intersected });
  }, [minTime, segments, pixelsPerSecond]);

  const handleMouseEnter = useCallback(() => {
    setIsHovering(true);
  }, []);

  const handleMouseLeave = useCallback(() => {
    setIsHovering(false);
    setCursorData(null);
  }, []);

  if (events.length === 0 || duration === 0) return null;

  const totalWidth = duration * pixelsPerSecond;
  const categories = getCategoriesInOrder();

  // Time markers - adjust spacing based on zoom level
  const markerInterval = visibleDuration <= 10 ? 1 : visibleDuration <= 60 ? 5 : visibleDuration <= 300 ? 10 : 30;
  const markers = [];
  for (let t = 0; t <= duration; t += markerInterval) {
    markers.push(t);
  }

  const categorySegments = categories.map((category) => ({
    category,
    segments: segments.filter((s) => s.category === category),
  }));

  return (
    <div className="space-y-2">
      {/* Timeline with fixed labels */}
      <div className="flex">
        {/* Fixed category labels column */}
        <div className="flex-shrink-0 pr-2">
          {/* Spacer for time markers row */}
          <div className="h-7 mb-2" />
          {/* Category labels */}
          <div className="space-y-1">
            {categories.map((category) => {
              const config = getCategoryConfig(category);
              return (
                <div key={category} className="h-6 flex items-center justify-end">
                  <span className="text-xs text-muted-foreground font-medium">
                    {config.label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Scrollable timeline using ScrollArea */}
        <ScrollArea 
          className="flex-1 min-w-0 overflow-hidden rounded-md" 
          ref={scrollRef}
        >
          <div 
            style={{ width: totalWidth, minWidth: '100%' }} 
            className="pb-3 transition-all duration-300 ease-out"
            onWheel={handleWheel}
          >
            {/* Time markers */}
            <div className="h-5 relative border-b border-border/30 mb-2">
              {markers.map((t) => (
                <div
                  key={t}
                  className="absolute text-[10px] text-muted-foreground transition-all duration-300 ease-out"
                  style={{ left: t * pixelsPerSecond }}
                >
                  <div className="h-2 w-px bg-border/50 mb-0.5" />
                  {t}s
                </div>
              ))}
            </div>

            {/* Category rows */}
            <div 
              ref={timelineRef}
              className="space-y-1 relative"
              onMouseMove={handleMouseMove}
              onMouseEnter={handleMouseEnter}
              onMouseLeave={handleMouseLeave}
            >
              {/* Highlight based on highlight type */}
              {highlight && (() => {
                if (highlight.type === 'segment') {
                  const startEvent = eventsById.get(highlight.startEventId);
                  const endEvent = eventsById.get(highlight.endEventId);
                  if (!startEvent || !endEvent) return null;
                  
                  const startTime = startEvent.timestamp;
                  const endTime = endEvent.timestamp;
                  
                  return (
                    <>
                      <div
                        className="absolute top-0 bottom-0 w-px bg-gray-400/30 z-20 pointer-events-none transition-all duration-300 ease-out"
                        style={{ left: (startTime - minTime) * pixelsPerSecond }}
                      />
                      <div
                        className="absolute top-0 bottom-0 w-px bg-gray-400/30 z-20 pointer-events-none transition-all duration-300 ease-out"
                        style={{ left: (endTime - minTime) * pixelsPerSecond }}
                      />
                      <div
                        className="absolute top-0 bottom-0 bg-gray-200/5 z-10 pointer-events-none transition-all duration-300 ease-out"
                        style={{ 
                          left: (startTime - minTime) * pixelsPerSecond,
                          width: (endTime - startTime) * pixelsPerSecond 
                        }}
                      />
                    </>
                  );
                } else {
                  const event = eventsById.get(highlight.eventId);
                  if (!event) return null;
                  
                  return (
                    <div
                      className="absolute top-0 bottom-0 w-0.5 bg-gray-400/30 z-20 pointer-events-none shadow-[0_0_8px_rgba(156,163,175,0.2)] transition-all duration-300 ease-out"
                      style={{ left: (event.timestamp - minTime) * pixelsPerSecond }}
                    />
                  );
                }
              })()}

              {/* Cursor following elements - positioned via transform for smoothness */}
              {isHovering && (
                <>
                  {/* Vertical line */}
                  <div
                    ref={cursorLineRef}
                    className="absolute top-0 bottom-0 w-px bg-foreground/60 z-30 pointer-events-none left-0"
                    style={{ willChange: 'transform' }}
                  />
                  {/* Popover with time and segments */}
                  {cursorData && (
                    <div
                      ref={popoverRef}
                      className="absolute z-50 pointer-events-none left-0"
                      style={{ top: 4, willChange: 'transform' }}
                    >
                      <div className="bg-popover text-popover-foreground border border-border rounded-md shadow-md p-2.5 text-xs min-w-[120px]">
                        {/* Time */}
                        <div 
                          ref={cursorTimeRef}
                          className="font-mono text-sm font-semibold text-foreground mb-1"
                        >
                          0.00s
                        </div>
                        {/* Segments */}
                        {cursorData.intersectedSegments.length > 0 ? (
                          <div className="space-y-1.5 border-t border-border/50 pt-1.5 mt-1.5">
                            {cursorData.intersectedSegments.map((seg, i) => {
                              const config = getCategoryConfig(seg.category);
                              return (
                                <div key={i}>
                                  <div className="flex items-center justify-between gap-3">
                                    <div className="flex items-center gap-1.5">
                                      <div className={`w-2 h-2 rounded-sm ${config.timelineColor}`} />
                                      <span className="font-medium text-[11px]">
                                        {config.label}
                                      </span>
                                    </div>
                                    <span className="text-muted-foreground font-mono text-[10px]">
                                      {formatDuration((seg.endTime - seg.startTime) * 1000)}
                                    </span>
                                  </div>
                                  {seg.text && (
                                    <div 
                                      className="text-muted-foreground text-[10px] ml-3.5 italic max-w-[250px] break-words" 
                                      title={seg.text}
                                    >
                                      {seg.text.length > 100 ? `${seg.text.substring(0, 100)}...` : seg.text}
                                    </div>
                                  )}
                                  {!seg.text && seg.operation && (
                                    <div className="text-muted-foreground text-[10px] ml-3.5 italic">
                                      {seg.operation}
                                    </div>
                                  )}
                                </div>
                              );
                            })}
                          </div>
                        ) : (
                          <div className="text-muted-foreground text-[10px]">No active segments</div>
                        )}
                      </div>
                    </div>
                  )}
                </>
              )}

              {categorySegments.map(({ category, segments: catSegments }) => {
                const config = getCategoryConfig(category);
                return (
                  <div 
                    key={category} 
                    className="h-6 bg-secondary/20 rounded relative"
                    style={{ width: totalWidth }}
                  >
                    {catSegments.map((segment, i) => {
                      const left = (segment.startTime - minTime) * pixelsPerSecond;
                      const width = (segment.endTime - segment.startTime) * pixelsPerSecond;
                      return (
                        <div
                          key={i}
                          className={`absolute h-full rounded ${config.timelineColor} opacity-90 hover:opacity-100 transition-all duration-300 ease-out`}
                          style={{ left, width: Math.max(width, 2) }}
                        />
                      );
                    })}
                  </div>
                );
              })}
            </div>
          </div>
          <ScrollBar orientation="horizontal" />
        </ScrollArea>
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center gap-4 pt-2 flex-wrap">
        {categories.map((category) => {
          const config = getCategoryConfig(category);
          return (
            <div key={category} className="flex items-center gap-1.5">
              <div className={`w-3 h-3 rounded ${config.timelineColor}`} />
              <span className="text-xs text-muted-foreground">{config.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
