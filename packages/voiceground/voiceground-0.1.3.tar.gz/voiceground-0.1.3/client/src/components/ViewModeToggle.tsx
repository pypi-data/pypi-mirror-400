interface ViewModeToggleProps {
  viewMode: 'turns' | 'events';
  onViewModeChange: (mode: 'turns' | 'events') => void;
}

export function ViewModeToggle({ viewMode, onViewModeChange }: ViewModeToggleProps) {
  return (
    <div className="flex items-center gap-1">
      <button
        onClick={() => onViewModeChange('turns')}
        className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
          viewMode === 'turns'
            ? 'bg-primary text-primary-foreground'
            : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
        }`}
      >
        Turns
      </button>
      <button
        onClick={() => onViewModeChange('events')}
        className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
          viewMode === 'events'
            ? 'bg-primary text-primary-foreground'
            : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
        }`}
      >
        Events
      </button>
    </div>
  );
}

