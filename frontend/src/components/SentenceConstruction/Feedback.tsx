import { Card } from '../Common/Card';
import { PinnedToggle } from '../Common/PinnedToggle';

interface FeedbackProps {
  isCorrect: boolean | null;
  feedback: string | null;
  correctSentence: string | null;
  resultId: number | null;
  isPinned: boolean | null;
  onPinToggle: (resultId: number, isPinned: boolean) => void;
}

function Feedback({ isCorrect, feedback, resultId, isPinned, onPinToggle }: FeedbackProps) {
  if (isCorrect === null || feedback === null || resultId === null || isPinned === null) {
    return null;
  }

  return (
    <Card>
      <h2 className="text-xl font-semibold mb-4">Feedback</h2>
      <p className={`mb-2 ${isCorrect ? 'text-green-600' : 'text-red-600'}`}>
        {feedback}
      </p>
      <div className="mt-4">
        <PinnedToggle isPinned={isPinned} onToggle={() => onPinToggle(resultId, !isPinned)} />
      </div>
    </Card>
  );
}

export default Feedback;