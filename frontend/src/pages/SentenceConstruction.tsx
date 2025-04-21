import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import { Button } from '../components/Common/Button';
import ReactMarkdown from 'react-markdown';

interface SentenceData {
  sentence_id: number;
  scrambled_words: string[];
  original_sentence: string;
  english_sentence: string;
  hints: { text: string; usefulness: number }[];
  explanation: string;
}

interface SentenceConstructionProps {
  lessonId: number;
  flashcardWords: string[];
  sentenceData: SentenceData;
  activityId: string;
  onComplete: (result: { isCorrect: boolean; activityId: string }) => void;
  onNext: () => void;
}

const SentenceConstruction: React.FC<SentenceConstructionProps> = ({
  lessonId,
  flashcardWords,
  sentenceData,
  activityId,
  onComplete,
  onNext,
}) => {
  const [error, setError] = useState<string | null>(null);
  const [constructedSentence, setConstructedSentence] = useState<string[]>([]);
  const [availableWords, setAvailableWords] = useState<string[]>(sentenceData.scrambled_words || []);
  const [showEnglish, setShowEnglish] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [submissionResult, setSubmissionResult] = useState<{
    is_correct: boolean;
    feedback: string;
    translated_sentence: string;
    explanation: string;
    user_answer: string;
  } | null>(null);
  const [revealedHints, setRevealedHints] = useState<boolean[]>(new Array(sentenceData.hints.length).fill(false));

  // Validate sentenceData
  useEffect(() => {
    if (
      !sentenceData ||
      !Array.isArray(sentenceData.scrambled_words) ||
      sentenceData.scrambled_words.length < 2 ||
      !sentenceData.original_sentence ||
      !sentenceData.english_sentence ||
      !Array.isArray(sentenceData.hints)
    ) {
      console.error('[SentenceConstruction] Invalid sentence data:', JSON.stringify(sentenceData, null, 2));
      setError('Unable to load sentence. Please try again.');
    }
  }, [sentenceData]);

  const handleWordClick = (word: string, from: 'available' | 'constructed') => {
    if (isSubmitted) return;
    if (from === 'available') {
      setAvailableWords((prev) => prev.filter((w) => w !== word));
      setConstructedSentence((prev) => [...prev, word]);
    } else {
      setConstructedSentence((prev) => prev.filter((w) => w !== word));
      setAvailableWords((prev) => [...prev, word]);
    }
  };

  const handleRevealHint = (index: number) => {
    setRevealedHints((prev) => {
      const newHints = [...prev];
      newHints[index] = true;
      return newHints;
    });
  };

  const handleSubmit = async () => {
    if (isSubmitted) return;
    const userAnswer = constructedSentence.join(' ');
    try {
      const response = await apiClient.post(`/api/sentence/submit`, {
        sentence_id: sentenceData.sentence_id,
        user_answer: userAnswer,
      });
      const result = response.data;
      setSubmissionResult(result);
      setIsSubmitted(true);
      onComplete({ isCorrect: result.is_correct, activityId });
      console.log('[SentenceConstruction] Submission result:', result);
    } catch (err: any) {
      console.error('[SentenceConstruction] Submission failed:', err);
      setError('Failed to submit sentence. Please try again.');
    }
  };

  if (error) {
    return <div className="text-center text-red-600 text-lg">{error}</div>;
  }

  return (
    <div className="bg-[#FFFFFF] p-6 rounded-lg shadow-sm border border-[#DAE1EA]">
      <h3 className="text-xl font-semibold text-[#252B2F] mb-4">Sentence Construction</h3>
      <p className="text-[#252B2F] mb-4">Arrange the words to form the correct sentence:</p>
      <div className="mb-4">
        <div className="flex flex-wrap gap-2 p-2 border border-[#DAE1EA] rounded min-h-[40px]">
          {constructedSentence.map((word, index) => (
            <Button
              key={`${word}-${index}`}
              variant="primary"
              className="bg-[#1079F1] !text-[#FFFFFF] hover:bg-[#0EBE75] hover:!text-[#FFFFFF] py-1 px-2"
              onClick={() => handleWordClick(word, 'constructed')}
              disabled={isSubmitted}
            >
              {word}
            </Button>
          ))}
        </div>
      </div>
      <div className="flex flex-wrap gap-2 mb-4">
        {availableWords.map((word, index) => (
          <Button
            key={`${word}-${index}`}
            variant="outline"
            className="bg-[#FFFFFF] !text-[#252B2F] hover:bg-[#E6F0FA] hover:!text-[#252B2F] border border-[#1079F1] py-1 px-2"
            onClick={() => handleWordClick(word, 'available')}
            disabled={isSubmitted}
          >
            {word}
          </Button>
        ))}
      </div>
      <div className="mb-4">
        <Button
          className="text-[#252B2F] hover:text-[#252B2F] py-2 px-4"
          onClick={() => setShowEnglish(!showEnglish)}
        >
          {showEnglish ? 'Hide English' : 'Show English'}
        </Button>
        {showEnglish && (
          <p className="text-[#252B2F] mt-2">
            <strong>English Sentence:</strong> {sentenceData.english_sentence}
          </p>
        )}
      </div>
      {sentenceData.hints.length > 0 && !isSubmitted && (
        <div className="mb-4">
          <p className="text-[#252B2F] font-semibold">Hints ({sentenceData.hints.length})</p>
          <ul className="list-none pl-0">
            {sentenceData.hints.map((hint, index) => (
              <li key={index} className="mt-2">
                <Button
                  variant="outline"
                  onClick={() => handleRevealHint(index)}
                  disabled={revealedHints[index]}
                  className="text-sm bg-[#F5F7FA] hover:bg-[#DAE1EA] text-[#252B2F] !text-[#252B2F]"
                >
                  {revealedHints[index] ? hint.text : `Reveal Hint ${index + 1}`}
                </Button>
              </li>
            ))}
          </ul>
        </div>
      )}
      {isSubmitted && submissionResult && (
        <div className="mb-4">
          <p className={`text-${submissionResult.is_correct ? '[#0EBE75]' : 'red-600'} text-lg`}>
            {submissionResult.feedback}
          </p>
          <p className="text-[#252B2F] mb-2">
            <strong>Correct Sentence:</strong> {submissionResult.translated_sentence}
          </p>
          <p className="text-[#252B2F] mb-2">
            <strong>Your Answer:</strong> {submissionResult.user_answer}
          </p>
          <div className="text-[#252B2F] mb-4 prose">
            <strong>Explanation:</strong>
            <ReactMarkdown>{submissionResult.explanation}</ReactMarkdown>
          </div>
          <Button
            onClick={onNext}
            className="bg-[#1079F1] !text-[#FFFFFF] hover:bg-[#0EBE75] hover:!text-[#FFFFFF] py-2 px-4"
          >
            Next Sentence
          </Button>
        </div>
      )}
      {!isSubmitted && (
        <div className="flex gap-4">
          <Button
            className="text-[#252B2F] hover:text-[#252B2F] py-2 px-4"
            onClick={handleSubmit}
            disabled={constructedSentence.length === 0}
          >
            Submit
          </Button>
        </div>
      )}
    </div>
  );
};

export default SentenceConstruction;