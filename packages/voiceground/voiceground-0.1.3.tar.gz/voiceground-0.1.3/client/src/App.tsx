import { useMemo, useState } from 'react';
import { EventsTable } from '@/components/EventsTable';
import { TurnsTable } from '@/components/TurnsTable';
import { AppHeader } from '@/components/AppHeader';
import { AppFooter } from '@/components/AppFooter';
import { EmptyState } from '@/components/EmptyState';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { parseTurns } from '@/components/TurnsView';
import { useEvents } from '@/hooks/useEvents';

type ViewMode = 'turns' | 'events';

function App() {
  const { events, isMockData } = useEvents();
  const [viewMode, setViewMode] = useState<ViewMode>('turns');

  const turns = useMemo(() => parseTurns(events), [events]);

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header - Fixed */}
      <AppHeader 
        turns={turns}
        isMockData={isMockData}
      />

      {/* Main Content - Takes remaining space between header and footer */}
      <main className="flex-1 overflow-hidden min-h-0">
        <div className="h-full w-full max-w-6xl mx-auto px-8 py-4 flex flex-col">
          {events.length === 0 ? (
            <EmptyState />
          ) : (
            <>
              {/* View Mode Tabs */}
              <Tabs value={viewMode} onValueChange={(value) => setViewMode(value as ViewMode)} className="flex-1 min-h-0 flex flex-col gap-0">
                <div className="flex-shrink-0 pb-2">
                  <TabsList className="w-fit">
                    <TabsTrigger value="turns" className="px-4">Per-Turn Breakdown</TabsTrigger>
                    <TabsTrigger value="events" className="px-4">Events Timeline</TabsTrigger>
                  </TabsList>
                </div>

                {/* Tables */}
                <TabsContent value="turns" className="flex-1 min-h-0 mt-0 overflow-hidden">
                  <TurnsTable turns={turns} />
                </TabsContent>
                <TabsContent value="events" className="flex-1 min-h-0 mt-0 overflow-hidden">
                  <EventsTable events={events} />
                </TabsContent>
              </Tabs>
            </>
          )}
        </div>
      </main>

      {/* Timeline Footer - Fixed */}
      <AppFooter 
              events={events} 
        turns={turns.length}
            />
    </div>
  );
}

export default App;
