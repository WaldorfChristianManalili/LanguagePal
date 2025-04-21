import React, { useEffect, useState } from 'react';
import { Button } from '../components/Common/Button';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import { useFlashcard } from '../hooks/useFlashcard';

interface FlashcardProps {
  lessonId: number;
  onComplete: (result: { word: string }) => void;
}

const fetchPexelsImage = async (query: string): Promise<string | null> => {
  if (!query || query.includes('Error')) return null;
  try {
    const response = await fetch(`/api/pexels/image?query=${encodeURIComponent(query)}`, {
      method: 'GET',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
    });
    if (!response.ok) throw new Error('Failed to fetch image');
    const data = await response.json();
    return data.image_url || null;
  } catch (error) {
    return null;
  }
};

const Flashcard: React.FC<FlashcardProps> = ({ lessonId, onComplete }) => {
  const { flashcard, flashcardLoading, error, fetchFlashcard, reset } = useFlashcard();
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [flashcardCount, setFlashcardCount] = useState(1);

  useEffect(() => {
    const loadFlashcard = async () => {
      reset();
      await fetchFlashcard(lessonId);
      if (flashcard?.word && !flashcard.word.includes('Error')) {
        const image = await fetchPexelsImage(flashcard.word);
        setImageUrl(image);
      }
    };
    loadFlashcard();
  }, [lessonId, fetchFlashcard, reset]);

  const handleOptionClick = (optionId: string) => {
    if (!isSubmitted) {
      setSelectedOption(optionId);
    }
  };

  const handleSubmit = () => {
    if (!flashcard || !selectedOption) return;
    const selectedOptionText = flashcard.options.find((opt) => opt.id === selectedOption)?.option_text || '';
    const correct = selectedOptionText.toLowerCase() === flashcard.translation.toLowerCase();
    setIsCorrect(correct);
    setIsSubmitted(true);
  };

  const handleNext = () => {
    setIsSubmitted(false);
    setSelectedOption(null);
    setIsCorrect(null);
    setImageUrl(null);
    if (flashcardCount >= 2) {
      onComplete({ word: flashcard?.word || '' });
    } else {
      setFlashcardCount((prev) => prev + 1);
      fetchFlashcard(lessonId);
    }
  };

  if (error) {
    return (
      <div className="text-red-600 text-center p-6">
        Failed to load flashcard. Please try again.
        <Button onClick={() => fetchFlashcard(lessonId)} className="mt-4 text-[#252B2F] hover:text-[#252B2F]">
          Retry
        </Button>
      </div>
    );
  }

  if (flashcardLoading || !flashcard) {
    return <LoadingSpinner message="Loading flashcard..." />;
  }

  return (
    <div className="p-6 bg-[#FFFFFF] max-w-md mx-auto rounded-lg">
      <h3 className="text-lg font-semibold text-[#252B2F] mb-4">Flashcard {flashcardCount}/2</h3>
      {!isSubmitted ? (
        <>
          {imageUrl && (
            <img
              src={imageUrl}
              alt={flashcard.word}
              className="w-full h-48 object-contain rounded-lg mb-4"
            />
          )}
          <p className="text-[#252B2F] mb-4">
            Select the correct translation for: <strong>{flashcard.word}</strong>
          </p>
          <div className="grid grid-cols-2 gap-4">
            {flashcard.options.map((option) => (
              <Button
                key={option.id}
                className={`${
                  selectedOption === option.id
                    ? 'bg-[#1079F1] text-[#252B2F] hover:text-[#252B2F]'
                    : 'bg-[#FFFFFF] text-[#252B2F] hover:text-[#252B2F] border border-[#1079F1]'
                }`}
                onClick={() => handleOptionClick(option.id)}
                disabled={isSubmitted}
              >
                {option.option_text}
              </Button>
            ))}
          </div>
          <Button
            className="mt-4 text-[#252B2F] hover:text-[#252B2F]"
            onClick={handleSubmit}
            disabled={!selectedOption}
          >
            Submit
          </Button>
        </>
      ) : (
        <div className="bg-[#FFFFFF] p-4 rounded-lg border border-[#DAE1EA]">
          <p className={`text-${isCorrect ? '[#0EBE75]' : 'red-600'} mb-2`}>
            {isCorrect ? 'Correct!' : `Incorrect. The correct translation is: ${flashcard.translation}`}
          </p>
          <p className="text-[#252B2F]">
            <strong>Word:</strong> {flashcard.word}
          </p>
          <p className="text-[#252B2F]">
            <strong>Type:</strong> {flashcard.type}
          </p>
          <p className="text-[#252B2F]">
            <strong>English Equivalent(s):</strong> {flashcard.english_equivalents.join(', ')}
          </p>
          <p className="text-[#252B2F]">
            <strong>Definition:</strong> {flashcard.definition}
          </p>
          <p className="text-[#252B2F]">
            <strong>English Definition:</strong> {flashcard.english_definition}
          </p>
          <p className="text-[#252B2F]">
            <strong>Example Sentence:</strong> {flashcard.example_sentence}
          </p>
          <p className="text-[#252B2F]">
            <strong>English Sentence:</strong> {flashcard.english_sentence}
          </p>
          <Button
            className="mt-4 text-[#252B2F] hover:text-[#252B2F]"
            onClick={handleNext}
          >
            {flashcardCount >= 2 ? 'Proceed to Sentence Construction' : 'Next Flashcard'}
          </Button>
        </div>
      )}
    </div>
  );
};

export default Flashcard;