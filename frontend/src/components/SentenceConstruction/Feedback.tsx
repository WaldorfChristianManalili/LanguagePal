import { Card } from '../Common/Card';
import { Button } from '../Common/Button';
import ReactMarkdown from 'react-markdown';

interface FeedbackProps {
  isCorrect: boolean | null;
  feedback: string | null;
  correctSentence: string | null;
  explanation: string | null;
  resultId: number | null;
  sentencePinned: boolean;
  onPinToggle?: (resultId: number, isPinned: boolean, sentenceId?: number) => void;
}

function Feedback({
  isCorrect,
  feedback,
  correctSentence,
  explanation,
  resultId,
  sentencePinned,
  onPinToggle,
}: FeedbackProps) {
  console.log('Feedback props:', {
    isCorrect,
    feedback,
    correctSentence,
    explanation,
    resultId,
    sentencePinned,
    hasOnPinToggle: !!onPinToggle,
  });

  const handlePinToggle = (sentenceId?: number) => {
    if (resultId != null) {
      const newIsPinned = !sentencePinned; // Toggle sentence pinned state
      console.log('Feedback: handlePinToggle called:', { resultId, sentencePinned, newIsPinned, sentenceId });
      onPinToggle?.(resultId, newIsPinned, sentenceId);
    } else {
      console.log('Feedback: handlePinToggle skipped: missing resultId');
    }
  };

  if (isCorrect === null || feedback === null) return null;

  return (
    <Card className="mb-4 p-6 bg-white shadow-md">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Feedback</h2>
      <p className={`text-lg ${isCorrect ? 'text-green-600' : 'text-red-600'}`}>
        {feedback}
      </p>
      {explanation && (
        <div className="text-gray-600 mt-2 prose prose-sm max-w-none">
          <ReactMarkdown
            components={{
              ul: ({ children }) => <ul className="list-disc pl-6 mt-2">{children}</ul>,
              ol: ({ children }) => <ol className="list-decimal pl-6 mt-2">{children}</ol>,
              li: ({ children }) => <li className="mb-1">{children}</li>,
              p: ({ children }) => <p className="mb-2">{children}</p>,
            }}
          >
            {explanation.replace(/^- /gm, '* ')}
          </ReactMarkdown>
        </div>
      )}
      {resultId != null && onPinToggle != null ? (
        <Button
          onClick={() => handlePinToggle()}
          variant="outline"
          className="mt-4 border-gray-300 text-gray-700 hover:bg-gray-100"
        >
          {sentencePinned ? 'Unpin' : 'Pin'}
        </Button>
      ) : (
        <p className="text-red-600 mt-4">Pin button unavailable: Missing props</p>
      )}
    </Card>
  );
}

export default Feedback;