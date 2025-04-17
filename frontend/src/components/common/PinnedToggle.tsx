import { Button } from './Button';

interface PinnedToggleProps {
  isPinned: boolean | null;
  onToggle: () => void;
}

function PinnedToggle({ isPinned, onToggle }: PinnedToggleProps) {
  return (
    <Button onClick={onToggle} variant="outline">
      {isPinned ? 'Unpin' : 'Pin'} Result
    </Button>
  );
}

export { PinnedToggle };