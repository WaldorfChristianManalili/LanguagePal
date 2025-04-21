import { Card } from '../Common/Card';
import ReactMarkdown from 'react-markdown';

interface FeedbackProps {
  isCorrect: boolean;
  feedback: string;
  correctSentence: string;
  explanation: string;
}

function Feedback({ isCorrect, feedback, correctSentence, explanation }: FeedbackProps) {
  console.log('Feedback props:', {
    isCorrect,
    feedback,
    correctSentence,
    explanation,
  });

  return (
    <Card className="mb-4 p-6 bg-[#FFFFFF] shadow-md border border-[#DAE1EA]">
      <h2 className="text-xl font-semibold text-[#252B2F] mb-4">Feedback</h2>
      <p className={`text-lg ${isCorrect ? 'text-[#0EBE75]' : 'text-red-600'}`}>{feedback}</p>
      {correctSentence && (
        <p className="text-[#252B2F] mt-2">
          <strong>Correct Sentence:</strong> {correctSentence}
        </p>
      )}
      {explanation && (
        <div className="text-[#252B2F] mt-2 prose prose-sm max-w-none">
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
    </Card>
  );
}

export default Feedback;