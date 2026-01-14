import { useAtomValue } from 'jotai';
import { Github } from 'lucide-react';
import { versionAtom } from '@/atoms';
import { SessionTimeline, formatDuration } from './SessionTimeline';
import type { VoicegroundEvent } from '@/types';

interface AppFooterProps {
  events: VoicegroundEvent[];
  turns: number;
}

const GITHUB_URL = 'https://github.com/poseneror/voiceground';
const GITHUB_ISSUES_URL = 'https://github.com/poseneror/voiceground/issues';

export function AppFooter({ events, turns }: AppFooterProps) {
  const version = useAtomValue(versionAtom);
  const minTime = Math.min(...events.map((e) => e.timestamp));
  const maxTime = Math.max(...events.map((e) => e.timestamp));
  const totalDuration = (maxTime - minTime) * 1000;

  return (
    <footer className="flex-shrink-0 border-t border-border/50 bg-card">
      <div className="max-w-6xl mx-auto px-8">
        {events.length > 0 && (
          <div className="py-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold">Session Timeline</h3>
              <span className="text-xs text-muted-foreground">
                {formatDuration(totalDuration)} total • {turns} turns
              </span>
            </div>
            <SessionTimeline events={events} />
          </div>
        )}
        
        {/* Credits and Links */}
        <div className="py-3 border-t border-border/30 flex items-center justify-between text-xs text-muted-foreground">
          <div className="flex items-center gap-4">
            <a
              href={GITHUB_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 hover:text-foreground transition-colors"
              aria-label="View Voiceground on GitHub"
            >
              <Github className="w-4 h-4" />
              <span>Voiceground</span>
            </a>
            {version && (
              <span className="text-muted-foreground/60">v{version}</span>
            )}
          </div>
          <a
            href={GITHUB_ISSUES_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-foreground transition-colors"
          >
            Report Issue
          </a>
        </div>
      </div>
    </footer>
  );
}

