import { useState, useEffect } from 'react';
import { Card } from '../components/Common/Card';
import { Button } from '../components/Common/Button';
import CategorySelect from '../components/SentenceConstruction/CategorySelect';
import ScrambledSentence from '../components/SentenceConstruction/ScrambledSentence';
import Feedback from '../components/SentenceConstruction/Feedback';
import { useSentence } from '../hooks/useSentence';
import { getCategories } from '../api/sentence';

function SentenceConstruction() {
  const {
    category,
    setCategory,
    sentence,
    feedback,
    loading,
    error,
    fetchSentence,
    submitSentence,
    togglePin,
    reset,
  } = useSentence();
  const [categories, setCategories] = useState<string[]>([]);

  // Fetch categories on mount
  useEffect(() => {
    const fetchCategoryList = async () => {
      try {
        const categoryList = await getCategories();
        setCategories(categoryList);
        if (categoryList.length > 0 && !category) {
          setCategory(categoryList[0]);
          fetchSentence(categoryList[0]);
        }
      } catch (err) {
        console.error('Error fetching categories:', err);
      }
    };
    fetchCategoryList();
  }, [setCategory, fetchSentence, category]);

  const handleCategoryChange = (newCategory: string) => {
    setCategory(newCategory);
    fetchSentence(newCategory);
  };

  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-100 to-blue-200 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">Sentence Construction</h1>
        <Card className="mb-6">
          <p className="text-gray-600 mb-4">
            Select a category and rearrange the scrambled words to form a correct sentence.
          </p>
        </Card>
        <CategorySelect
          categories={categories}
          selectedCategory={category}
          onChange={handleCategoryChange}
          disabled={categories.length === 0}
        />
        {loading && <p className="text-gray-600">Loading...</p>}
        {error && <p className="text-red-600">{error}</p>}
        {sentence && (
          <ScrambledSentence
            sentence={sentence}
            onSubmit={submitSentence}
          />
        )}
        <Feedback
          isCorrect={feedback?.isCorrect ?? null}
          feedback={feedback?.feedback ?? null}
          correctSentence={feedback?.correctSentence ?? null}
          resultId={feedback?.resultId ?? null}
          isPinned={feedback?.isPinned ?? null}
          onPinToggle={togglePin}
        />
        {(sentence || feedback) && (
          <Button onClick={reset} variant="outline" className="mt-4">
            Try Another Sentence
          </Button>
        )}
      </div>
    </div>
  );
}

export default SentenceConstruction;