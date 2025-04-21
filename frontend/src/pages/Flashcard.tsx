import React, { useEffect, useState } from 'react';
import { Button } from '../components/Common/Button';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import { Flashcard as FlashcardType } from '../types/flashcard';

interface FlashcardProps {
  flashcard: FlashcardType;
  lessonName: string;
  flashcardCount: number;
  totalFlashcards: number;
  activityId: string;
  onComplete: (result: { word: string; isCorrect: boolean; activityId: string }) => void;
  nextFlashcard?: FlashcardType;
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
    console.error('[fetchPexelsImage] Error:', error);
    return null;
  }
};

const debounce = <F extends (...args: any[]) => Promise<any>>(
  func: F,
  wait: number
) => {
  let timeout: NodeJS.Timeout | null = null;
  return (...args: Parameters<F>): Promise<ReturnType<F>> => {
    return new Promise((resolve) => {
      if (timeout) clearTimeout(timeout);
      timeout = setTimeout(async () => {
        const result = await func(...args);
        resolve(result);
      }, wait);
    });
  };
};

const debouncedFetchPexelsImage = debounce(fetchPexelsImage, 300);

const Flashcard: React.FC<FlashcardProps> = ({ flashcard, lessonName, flashcardCount, totalFlashcards, activityId, onComplete }) => {
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadImage = async () => {
      if (flashcard.translation && !flashcard.word.includes('Error')) {
        console.log('[Flashcard] Querying Pexels with:', flashcard.translation);
        const url = await debouncedFetchPexelsImage(flashcard.translation);
        setImageUrl(url);
      } else {
        setImageUrl(null);
      }
      setLoading(false);
    };
    loadImage();
    console.log(`[Flashcard] Rendering ${flashcardCount}/${totalFlashcards}, word: ${flashcard.word}, activityId: ${activityId}`);
  }, [flashcard, flashcardCount, totalFlashcards, activityId]);

  const handleOptionClick = (optionId: string) => {
    if (!isSubmitted) {
      setSelectedOption(optionId);
      console.log('[Flashcard] Selected option:', optionId);
    }
  };

  const handleSubmit = () => {
    if (!selectedOption || isSubmitted) return;
    const selectedOptionText = flashcard.options.find((opt) => opt.id === selectedOption)?.option_text || '';
    const correct = selectedOptionText.toLowerCase() === flashcard.translation.toLowerCase();
    setIsCorrect(correct);
    setIsSubmitted(true);
    console.log(`[Flashcard] Submitted ${flashcardCount}/${totalFlashcards}, word: ${flashcard.word}, correct: ${correct}`);
  };

  const handleNext = () => {
    console.log('[Flashcard] Advancing, isCorrect:', isCorrect, 'activityId:', activityId);
    onComplete({ word: flashcard.word, isCorrect: isCorrect ?? false, activityId });
    setIsSubmitted(false);
    setSelectedOption(null);
    setIsCorrect(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#FFFFFF]">
        <LoadingSpinner message="Loading flashcard..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-[#FFFFFF] p-6">
      <div className="w-full max-w-lg bg-[#FFFFFF] rounded-lg shadow-lg p-6 flex flex-col justify-between min-h-[80vh]">
        <h3 className="text-xl font-semibold text-[#252B2F] mb-4">Flashcard {flashcardCount}/{totalFlashcards}</h3>
        {!isSubmitted ? (
          <div className="flex flex-col flex-grow">
            {imageUrl && imageUrl !== 'https://placehold.co/600x400' ? (
              <img
                src={imageUrl}
                alt={flashcard.word}
                className="w-full h-48 object-contain rounded-lg mb-4"
              />
            ) : (
              <div className="w-full h-48 bg-gray-200 rounded-lg mb-4 flex items-center justify-center">
                <span className="text-gray-500">No image available</span>
              </div>
            )}
            <p className="text-[#252B2F] mb-4 text-lg">
              Select the correct translation for: <strong>{flashcard.word}</strong>
            </p>
            <div className="grid grid-cols-2 gap-4 mb-6">
              {flashcard.options.map((option) => (
                <Button
                  key={option.id}
                  className={`${
                    selectedOption === option.id
                      ? 'bg-[#1079F1] text-[#252B2F] hover:text-[#252B2F]'
                      : 'bg-[#FFFFFF] !text-[#252B2F] hover:bg-[#E6F0FA] border border-[#1079F1]'
                  } py-3 text-base`}
                  onClick={() => handleOptionClick(option.id)}
                  disabled={isSubmitted}
                >
                  {option.option_text}
                </Button>
              ))}
            </div>
            <Button
              className="mt-auto text-[#252B2F] hover:text-[#252B2F] py-3 text-base"
              onClick={handleSubmit}
              disabled={!selectedOption || isSubmitted}
            >
              Submit
            </Button>
          </div>
        ) : (
          <div className="flex flex-col flex-grow">
            <p className={`text-${isCorrect ? '[#0EBE75]' : 'red-600'} mb-4 text-lg`}>
              {isCorrect ? 'Correct!' : `Incorrect. The correct translation is: ${flashcard.translation}`}
            </p>
            <div className="space-y-2 text-[#252B2F] text-base">
              <p><strong>Word:</strong> {flashcard.word}</p>
              <p><strong>Type:</strong> {flashcard.type}</p>
              <p><strong>English Equivalent(s):</strong> {flashcard.english_equivalents.join(', ')}</p>
              <p><strong>Definition:</strong> {flashcard.definition}</p>
              <p><strong>English Definition:</strong> {flashcard.english_definition}</p>
              <p><strong>Example Sentence:</strong> {flashcard.example_sentence}</p>
              <p><strong>English Sentence:</strong> {flashcard.english_sentence}</p>
            </div>
            <Button
              className="mt-auto text-[#252B2F] hover:text-[#252B2F] py-3 text-base"
              onClick={handleNext}
            >
              {flashcardCount >= totalFlashcards ? 'Proceed to Sentence' : 'Next Flashcard'}
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Flashcard;