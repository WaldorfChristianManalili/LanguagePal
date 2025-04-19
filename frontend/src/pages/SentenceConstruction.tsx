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
  const [isCategoryChanging, setIsCategoryChanging] = useState(false); // Track category change
  const navigate = useNavigate();

  // Fetch categories only once on mount
  useEffect(() => {
    const fetchCategoryList = async () => {
      try {
        const categoryList = await getCategories();
        setCategories(categoryList);
        if (categoryList.length > 0 && !category) {
          setCategory(categoryList[0]);
          await fetchSentence(categoryList[0]); // Initial load
        }
      } catch (err) {
        console.error('Error fetching categories:', err);
      }
    };
    fetchCategoryList();
  }, [setCategory, fetchSentence]);

  // Handle category change with immediate state reset
  const handleCategoryChange = useCallback(
    async (newCategory: string) => {
      setIsCategoryChanging(true); // Prevent rendering stale sentence
      setCategory(newCategory);
      reset(); // Clear sentence and feedback
      setShowEnglish(false);
      try {
        await fetchSentence(newCategory); // Fetch new sentence
      } finally {
        setIsCategoryChanging(false); // Allow rendering after fetch
      }
    },
    [setCategory, fetchSentence, reset]
  );

  const handleReset = () => {
    reset();
    setShowEnglish(false);
    fetchSentence(category || categories[0] || 'greeting'); // Fetch new sentence for current category
  };

  const handleEndSession = () => {
    navigate('/dashboard');
  };

  const toggleEnglishSentence = () => {
    setShowEnglish((prev) => !prev);
  };

  // Show loading spinner during sentence loading or category change
  if (sentenceLoading || isCategoryChanging) {
    return <LoadingSpinner message="Loading sentence..." />;
  }

  // Show error state
  if (error) {
    return (
      <div className="flex flex-col items-center p-6">
        <p className="text-red-600 text-lg mb-4">Error: {error}</p>
        <Button onClick={() => fetchSentence(category || categories[0] || 'greeting')}>
          Retry
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
          disabled={categories.length === 0 || sentenceLoading || submitLoading || pinLoading || isCategoryChanging}
        />
        {sentence && !isCategoryChanging && (
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
                  ></div>
                </div>
              </label>
            </div>
            {showEnglish && <p className="text-gray-600 mt-2">{sentence.englishSentence}</p>}
          </Card>
        )}
        {sentence && !isCategoryChanging && (
          <ScrambledSentence sentence={sentence} onSubmit={submitSentence} />
        )}
        {feedback && !isCategoryChanging && (
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
              disabled={sentenceLoading || submitLoading || pinLoading || isCategoryChanging}
            >
              Next Sentence
            </Button>
          )}
          <Button
            onClick={handleEndSession}
            variant="outline"
            className="mt-4 border-gray-300 text-gray-700 hover:bg-gray-100"
            disabled={sentenceLoading || submitLoading || pinLoading || isCategoryChanging}
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