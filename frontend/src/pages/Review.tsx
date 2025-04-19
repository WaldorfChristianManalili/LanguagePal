import { useState, useEffect, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Card } from '../components/Common/Card';
import { Button } from '../components/Common/Button';
import Feedback from '../components/SentenceConstruction/Feedback';
import { SubmitSentenceResponse } from '../types/sentence';
import { getPinnedResults, togglePin } from '../api/sentence';
import { useAuth } from '../App';

function Review() {
  const [pinnedResults, setPinnedResults] = useState<SubmitSentenceResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { token } = useAuth();
  const location = useLocation();

  const fetchPinnedResults = useCallback(async () => {
    setLoading(true);
    try {
      const results = await getPinnedResults();
      console.log('Review: Fetched pinned results:', results);
      setPinnedResults(results);
      setError(null);
    } catch (err) {
      console.error('Review: Error fetching pinned results:', err);
      setError('Failed to fetch pinned results');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let isMounted = true;
    if (token) {
      fetchPinnedResults().then(() => {
        if (!isMounted) return;
        console.log('Review: fetchPinnedResults completed');
      });
    } else {
      setPinnedResults([]);
    }
    return () => {
      isMounted = false;
    };
  }, [fetchPinnedResults, token]);

  useEffect(() => {
    if (location.pathname === '/review' && token) {
      fetchPinnedResults();
    }
  }, [location.pathname, fetchPinnedResults, token]);

  const handlePinToggle = async (resultId: number, isPinned: boolean) => {
    try {
      console.log('Review: handlePinToggle:', { resultId, isPinned });
      await togglePin(resultId, isPinned);
      await fetchPinnedResults();
    } catch (error) {
      console.error('Review: Failed to toggle pin:', error);
      setError('Failed to update pin status');
    }
  };

  const handleReturn = () => {
    navigate('/dashboard');
  };

  const handleRefresh = () => {
    fetchPinnedResults();
  };

  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-100 to-blue-200 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">Pinned Results</h1>
        <Card className="mb-6 bg-white shadow-md">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-800">Your Pinned Sentences</h2>
            <div className="flex space-x-2">
              <Button
                onClick={handleRefresh}
                variant="outline"
                className="border-gray-300 text-gray-700 hover:bg-gray-100"
              >
                Refresh
              </Button>
              <Button
                onClick={handleReturn}
                variant="outline"
                className="border-gray-300 text-gray-700 hover:bg-gray-100"
              >
                Return
              </Button>
            </div>
          </div>
          {loading && <p className="text-gray-600">Loading...</p>}
          {error && <p className="text-red-600">{error}</p>}
          {!loading && pinnedResults.length === 0 && (
            <p className="text-gray-600">No pinned results yet.</p>
          )}
          {pinnedResults.map(result => (
            <Feedback
              key={result.result_id}
              resultId={result.result_id}
              isCorrect={result.is_correct}
              feedback={result.feedback}
              correctSentence={result.translated_sentence}
              explanation={result.explanation}
              sentencePinned={true}
              onPinToggle={handlePinToggle}
            />
          ))}
        </Card>
      </div>
    </div>
  );
}

export default Review;