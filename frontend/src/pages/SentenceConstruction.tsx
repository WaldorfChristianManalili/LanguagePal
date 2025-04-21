import { useState, useEffect, useCallback } from 'react';
import { Card } from '../components/Common/Card';
import { Button } from '../components/Common/Button';
import ScrambledSentence from '../components/SentenceConstruction/ScrambledSentence';
import Feedback from '../components/SentenceConstruction/Feedback';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import { useSentence } from '../hooks/useSentence';

interface SentenceConstructionProps {
  lessonId: number;
  flashcardWords: string[];
  onComplete: () => void;
}

const SentenceConstruction: React.FC<SentenceConstructionProps> = ({ lessonId, flashcardWords, onComplete }) => {
  const {
    sentence,
    feedback,
    sentenceLoading,
    submitLoading,
    error,
    fetchSentence,
    submitSentence,
    reset,
  } = useSentence();
  const [showEnglish, setShowEnglish] = useState(false);

  useEffect(() => {
    reset();
    fetchSentence(lessonId, flashcardWords);
  }, [lessonId, flashcardWords, fetchSentence, reset]);

  const toggleEnglishSentence = useCallback(() => {
    setShowEnglish((prev) => !prev);
  }, []);

  const handleReset = useCallback(() => {
    reset();
    setShowEnglish(false);
    fetchSentence(lessonId, flashcardWords);
  }, [lessonId, flashcardWords, fetchSentence, reset]);

  const isDisabled = sentenceLoading || submitLoading;

  if (sentenceLoading) {
    return <LoadingSpinner message="Loading sentence..." />;
  }

  if (error) {
    return (
      <div className="flex flex-col items-center p-6">
        <p className="text-red-600 text-lg mb-4">{error}</p>
        <Button onClick={() => fetchSentence(lessonId, flashcardWords)}>
          Try Again
        </Button>
      </div>
    );
  }

  return (
    <div className="p-6 bg-[#FFFFFF]">
      <h2 className="text-xl font-semibold text-[#252B2F] mb-4">Sentence Construction</h2>
      {sentence && (
        <>
          <Card className="mb-4 p-6 bg-[#FFFFFF] shadow-md border border-[#DAE1EA]">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-[#252B2F]">English Sentence</h3>
              <label className="flex items-center cursor-pointer">
                <span className="mr-2 text-[#252B2F]">Show English</span>
                <input
                  type="checkbox"
                  checked={showEnglish}
                  onChange={toggleEnglishSentence}
                  className="hidden"
                />
                <div
                  className={`w-12 h-6 bg-[#DAE1EA] rounded-full p-1 transition-colors duration-300 ${
                    showEnglish ? 'bg-[#0EBE75]' : ''
                  }`}
                >
                  <div
                    className={`bg-[#FFFFFF] w-4 h-4 rounded-full shadow-md transform transition-transform duration-300 ${
                      showEnglish ? 'translate-x-6' : ''
                    }`}
                  />
                </div>
              </label>
            </div>
            {showEnglish && <p className="text-[#252B2F] mt-2">{sentence.english_sentence}</p>}
          </Card>
          <ScrambledSentence
            sentence={sentence}
            onSubmit={(constructedSentence) => submitSentence(constructedSentence)}
          />
        </>
      )}
      {feedback && (
        <Feedback
          isCorrect={feedback.is_correct}
          feedback={feedback.feedback}
          correctSentence={feedback.translated_sentence}
          explanation={feedback.explanation}
        />
      )}
      <div className="flex space-x-4">
        {(sentence || feedback) && (
          <Button
            onClick={feedback ? onComplete : handleReset}
            variant="outline"
            className="mt-4"
            disabled={isDisabled}
          >
            {feedback ? 'Proceed to Dialogue' : 'Next Sentence'}
          </Button>
        )}
      </div>
      {submitLoading && <p className="text-[#252B2F] mt-4">Submitting...</p>}
    </div>
  );
};

export default SentenceConstruction;