import { useAtomValue } from 'jotai';
import { MetricsSummary } from './MetricsSummary';
import { conversationIdAtom } from '@/atoms';
import type { Turn } from '@/types';

interface AppHeaderProps {
  turns: Turn[];
  isMockData: boolean;
}

export function AppHeader({ turns, isMockData }: AppHeaderProps) {
  const conversationId = useAtomValue(conversationIdAtom);

  return (
    <header className="flex-shrink-0 border-b border-border/50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="max-w-6xl mx-auto px-8 py-4">
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold tracking-tight text-primary">
                Voiceground {isMockData ? '[MOCK]' : ''}
              </h1>
              {conversationId && (
                <span className="text-xs text-muted-foreground font-mono bg-secondary/50 px-2 py-1 rounded">
                  Conversation: {conversationId}
                </span>
              )}
            </div>
            <p className="text-muted-foreground text-xs">
              Post Conversation Report
            </p>
          </div>
          {turns.length > 0 && (
            <MetricsSummary turns={turns} />
          )}
        </div>
      </div>
    </header>
  );
}

