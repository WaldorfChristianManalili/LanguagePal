import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/Common/Card';
import { Button } from '../components/Common/Button';
import CategorySelect from '../components/SentenceConstruction/CategorySelect';
import ScrambledSentence from '../components/SentenceConstruction/ScrambledSentence';
import Feedback from '../components/SentenceConstruction/Feedback';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import { useSentence } from '../hooks/useSentence';
import { getCategories } from '../api/sentence';

function SentenceConstruction() {
  const {
    category,
    setCategory,
    sentence,
    feedback,
    sentencePinned,
    sentenceLoading,
    submitLoading,
    pinLoading,
    error,
    fetchSentence,
    submitSentence,
    togglePin,
    reset,
  } = useSentence();
  const [categories, setCategories] = useState<string[]>([]);
  const [showEnglish, setShowEnglish] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchInitialData = async () => {
      const categoryList = await getCategories();
      setCategories(categoryList);
      if (categoryList.length > 0 && !category) {
        setCategory(categoryList[0]);
        await fetchSentence(categoryList[0]);
      }
      setIsLoading(false);
    };
    fetchInitialData();
  }, [setCategory, fetchSentence]);

  const handleCategoryChange = useCallback(
    async (newCategory: string) => {
      setIsLoading(true);
      setCategory(newCategory);
      reset();
      setShowEnglish(false);
      await fetchSentence(newCategory);
      setIsLoading(false);
    },
    [setCategory, fetchSentence, reset]
  );

  const handleReset = useCallback(async () => {
    reset();
    setShowEnglish(false);
    await fetchSentence(category || categories[0] || 'greeting');
  }, [category, categories, fetchSentence, reset]);

  const toggleEnglishSentence = useCallback(() => {
    setShowEnglish((prev) => !prev);
  }, []);

  const isDisabled = sentenceLoading || submitLoading || pinLoading || isLoading;

  if (isLoading || sentenceLoading) {
    return <LoadingSpinner message="Loading sentence..." />;
  }

  if (error) {
    return (
      <div className="flex flex-col items-center p-6">
        <p className="text-red-600 text-lg mb-4">{error}</p>
        <Button onClick={() => fetchSentence(category || categories[0] || 'greeting')}>
          Try Again
        </Button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-100 to-blue-200 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">Sentence Construction</h1>
        <Card className="mb-6 bg-white shadow-md">
          <p className="text-gray-600 mb-4">
            Select a category and rearrange the scrambled words to form a correct sentence.
          </p>
        </Card>
        <CategorySelect
          categories={categories}
          selectedCategory={category}
          onChange={handleCategoryChange}
          disabled={categories.length === 0 || isDisabled}
        />
        {sentence && (
          <>
            <Card className="mb-4 p-6 bg-white shadow-md">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-800">English Sentence</h2>
                <label className="flex items-center cursor-pointer">
                  <span className="mr-2 text-gray-600">Show English</span>
                  <input
                    type="checkbox"
                    checked={showEnglish}
                    onChange={toggleEnglishSentence}
                    className="hidden"
                  />
                  <div
                    className={`w-12 h-6 bg-gray-300 rounded-full p-1 transition-colors duration-300 ${
                      showEnglish ? 'bg-green-500' : ''
                    }`}
                  >
                    <div
                      className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform duration-300 ${
                        showEnglish ? 'translate-x-6' : ''
                      }`}
                    />
                  </div>
                </label>
              </div>
              {showEnglish && <p className="text-gray-600 mt-2">{sentence.englishSentence}</p>}
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
            resultId={feedback.result_id}
            sentencePinned={sentencePinned}
            onPinToggle={(resultId, isPinned) => togglePin(resultId, isPinned, sentence?.sentenceId)}
          />
        )}
        <div className="flex space-x-4">
          {(sentence || feedback) && (
            <Button
              onClick={handleReset}
              variant="outline"
              className="mt-4 border-gray-300 text-gray-700 hover:bg-gray-100"
              disabled={isDisabled}
            >
              Next Sentence
            </Button>
          )}
          <Button
            onClick={() => navigate('/dashboard')}
            variant="outline"
            className="mt-4 border-gray-300 text-gray-700 hover:bg-gray-100"
            disabled={isDisabled}
          >
            End Session
          </Button>
        </div>
        {submitLoading && <p className="text-gray-600 mt-4">Submitting...</p>}
        {pinLoading && <p className="text-gray-600 mt-4">Pinning...</p>}
      </div>
    </div>
  );
}

export default SentenceConstruction;