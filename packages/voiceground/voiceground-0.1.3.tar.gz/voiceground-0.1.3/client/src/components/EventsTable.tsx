import { useMemo, useState, useRef, useEffect } from 'react';
import { useSetAtom } from 'jotai';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { highlightAtom, createEventHighlight } from '@/atoms';
import { getFilterCategories, getCategoryLabel, getCategoryDescription, getEventTypeLabel } from '@/config';
import { categoryDescriptions } from './SessionTimeline';
import { DataTableColumnHeader } from '@/components/data-table-column-header';
import { DataTable } from '@/components/DataTable';
import type { VoicegroundEvent, EventCategory } from '@/types';

interface EventsTableProps {
  events: VoicegroundEvent[];
}

function formatRelativeTime(timestamp: number, baseTimestamp: number): string {
  const diff = timestamp - baseTimestamp;
  if (diff < 1) {
    return `+${(diff * 1000).toFixed(0)}ms`;
  }
  return `+${diff.toFixed(3)}s`;
}


export function EventsTable({ events }: EventsTableProps) {
  const [sortAsc, setSortAsc] = useState(true);
  const [filterCategory, setFilterCategory] = useState<EventCategory | 'all'>('all');
  const setHighlight = useSetAtom(highlightAtom);

  const baseTimestamp = useMemo(() => {
    if (events.length === 0) return 0;
    return Math.min(...events.map((e) => e.timestamp));
  }, [events]);

  const filteredEvents = useMemo(() => {
    let result = [...events];
    
    if (filterCategory !== 'all') {
      result = result.filter((e) => e.category === filterCategory);
    }
    
    result.sort((a, b) => {
      const diff = a.timestamp - b.timestamp;
      return sortAsc ? diff : -diff;
    });
    
    return result;
  }, [events, filterCategory, sortAsc]);

  const categories = getFilterCategories();
  const filterOptions = categories.map((cat) => ({
    value: cat,
    label: cat === 'all' ? 'All Categories' : getCategoryLabel(cat),
  }));

  const columns = useMemo(() => [
    {
      header: (
        <DataTableColumnHeader
          title="Time"
          sortAsc={sortAsc}
          onSortChange={(asc) => setSortAsc(asc)}
        />
      ),
      cell: (event: VoicegroundEvent) => (
        <span className="text-primary font-semibold">
          {formatRelativeTime(event.timestamp, baseTimestamp)}
        </span>
      ),
      className: 'w-[120px]',
    },
    {
      header: (
        <DataTableColumnHeader
          title="Category"
          sortAsc={null}
          filterOptions={filterOptions}
          filterValue={filterCategory}
          onFilterChange={(value) => setFilterCategory(value as EventCategory | 'all')}
        />
      ),
      cell: (event: VoicegroundEvent) => (
        <Badge variant="outline" className={`badge-${event.category}`}>
          {getCategoryLabel(event.category)}
        </Badge>
      ),
      className: 'w-[120px]',
    },
    {
      header: 'Type',
      cell: (event: VoicegroundEvent) => (
        <span className="text-muted-foreground">
          {getEventTypeLabel(event.type)}
        </span>
      ),
      className: 'w-[100px]',
    },
    {
      header: 'Description',
      cell: (event: VoicegroundEvent) => {
        const description = event.data.text
          ? (event.data.text as string)
          : event.data.operation
          ? (event.data.operation as string)
          : getCategoryDescription(event.category) || categoryDescriptions[event.category] || '—';
        
        const DescriptionCell = () => {
          const [isOverflowing, setIsOverflowing] = useState(false);
          const spanRef = useRef<HTMLSpanElement>(null);
          
          useEffect(() => {
            const checkOverflow = () => {
              if (spanRef.current) {
                setIsOverflowing(spanRef.current.scrollWidth > spanRef.current.clientWidth);
              }
            };
            
            checkOverflow();
            window.addEventListener('resize', checkOverflow);
            return () => window.removeEventListener('resize', checkOverflow);
          }, []);
          
          return (
            <Tooltip open={isOverflowing ? undefined : false}>
              <TooltipTrigger asChild>
                <div
                  className="w-full h-full"
                  onMouseEnter={(e) => {
                    const target = e.currentTarget.querySelector('span');
                    if (target) {
                      setIsOverflowing(target.scrollWidth > target.clientWidth);
                    }
                  }}
                >
                  <span
                    ref={spanRef}
                    className="text-muted-foreground italic truncate block"
                  >
                    {description}
                  </span>
                </div>
              </TooltipTrigger>
              {isOverflowing && (
                <TooltipContent side="top" className="max-w-md whitespace-normal break-words">
                  <p>{description}</p>
                </TooltipContent>
              )}
            </Tooltip>
          );
        };
        
        return <DescriptionCell />;
      },
    },
  ], [sortAsc, filterCategory, filterOptions, baseTimestamp]);

  if (events.length === 0) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center text-muted-foreground">
          <p className="font-medium mb-1">No events recorded</p>
          <p className="text-xs">No conversation events have been captured yet.</p>
        </div>
      </div>
    );
  }

  return (
    <TooltipProvider>
      <div className="h-full flex flex-col min-h-0 overflow-hidden">
        <DataTable
          columns={columns}
          data={filteredEvents}
          emptyMessage="No events match the selected filter"
          onRowMouseEnter={(event) => setHighlight(createEventHighlight(event.id))}
          onRowMouseLeave={() => setHighlight(null)}
          rowClassName={() => 'font-mono text-sm cursor-pointer'}
          getRowKey={(event) => event.id}
        />
        <p className="text-xs text-muted-foreground mt-4 flex-shrink-0">
          Showing {filteredEvents.length} of {events.length} events
        </p>
      </div>
    </TooltipProvider>
  );
}

