import React, { useState } from 'react';
import { Button } from '../components/Common/Button';

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
  onComplete: (isCorrect: boolean) => void;
}

const SentenceConstruction: React.FC<SentenceConstructionProps> = ({
  lessonId,
  flashcardWords,
  sentenceData,
  activityId,
  onComplete,
}) => {
  const [error, setError] = useState<string | null>(null);
  const [constructedSentence, setConstructedSentence] = useState<string[]>([]);
  const [availableWords, setAvailableWords] = useState<string[]>(sentenceData.scrambled_words || []);
  const [showEnglish, setShowEnglish] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);

  // Validate sentenceData
  if (
    !sentenceData ||
    !Array.isArray(sentenceData.scrambled_words) ||
    sentenceData.scrambled_words.length < 2 ||
    !sentenceData.original_sentence ||
    !sentenceData.english_sentence ||
    !Array.isArray(sentenceData.hints)
  ) {
    console.error('[SentenceConstruction] Invalid sentence data:', sentenceData);
    setError('Unable to load sentence. Please try again.');
  }

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

  const handleSubmit = () => {
    if (isSubmitted) return;
    const userSentence = constructedSentence.join(' ');
    const correctSentence = sentenceData.original_sentence.trim();
    const isCorrect = userSentence === correctSentence;
    setIsCorrect(isCorrect);
    setIsSubmitted(true);
    onComplete(isCorrect);
    console.log('[SentenceConstruction] Submitted:', { userSentence, correctSentence, isCorrect });
  };

  const handleReset = () => {
    setConstructedSentence([]);
    setAvailableWords(sentenceData.scrambled_words || []);
    setIsSubmitted(false);
    setIsCorrect(null);
  };

  if (error) {
    return (
      <div className="text-center text-red-600 text-lg">{error}</div>
    );
  }

  return (
    <div className="bg-[#FFFFFF] p-6 rounded-lg shadow-sm border border-[#DAE1EA]">
      <h3 className="text-xl font-semibold text-[#252B2F] mb-4">Sentence Construction</h3>
      <p className="text-[#252B2F] mb-4">
        Arrange the words to form the correct sentence:
      </p>
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
      {isSubmitted && (
        <div className="mb-4">
          <p className={`text-${isCorrect ? '[#0EBE75]' : 'red-600'} text-lg`}>
            {isCorrect ? 'Correct!' : `Incorrect. The correct sentence is: ${sentenceData.original_sentence}`}
          </p>
          <p className="text-[#252B2F]"><strong>Explanation:</strong> {sentenceData.explanation}</p>
          {sentenceData.hints.length > 0 && (
            <div>
              <strong>Hints:</strong>
              <ul className="list-disc pl-5 text-[#252B2F]">
                {sentenceData.hints.map((hint, index) => (
                  <li key={index}>{hint.text}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
      <div className="flex gap-4">
        <Button
          className="text-[#252B2F] hover:text-[#252B2F] py-2 px-4"
          onClick={handleSubmit}
          disabled={isSubmitted || constructedSentence.length === 0}
        >
          Submit
        </Button>
        <Button
          className="text-[#252B2F] hover:text-[#252B2F] py-2 px-4"
          onClick={handleReset}
          disabled={!isSubmitted}
        >
          Try Again
        </Button>
      </div>
    </div>
  );
};

export default SentenceConstruction;