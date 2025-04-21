import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { LessonResponse, LessonActivity } from '../types/lesson';
import { Flashcard as FlashcardType } from '../types/flashcard';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import { Button } from '../components/Common/Button';
import { apiClient } from '../api/client';
import FlashcardComponent from './Flashcard';
import SentenceConstruction from './SentenceConstruction';
import { useAuth } from '../App';

const fetchInitialLesson = async (lessonId: string, token: string): Promise<LessonResponse> => {
  const response = await apiClient.get(`/api/lesson/${lessonId}/initial`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
};

const fetchNextActivity = async (lessonId: string, currentActivityId: string, token: string): Promise<LessonResponse> => {
  const response = await apiClient.get(`/api/lesson/${lessonId}/next`, {
    headers: { Authorization: `Bearer ${token}` },
    params: { current_activity_id: currentActivityId },
  });
  return response.data;
};

const Lesson: React.FC = () => {
  const { lessonId } = useParams<{ lessonId: string }>();
  const navigate = useNavigate();
  const { token, user } = useAuth();
  const [activities, setActivities] = useState<LessonActivity[]>([]);
  const [currentActivityIndex, setCurrentActivityIndex] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isFetchingNext, setIsFetchingNext] = useState(false);
  const [flashcardWords, setFlashcardWords] = useState<string[]>([]);
  const [performance, setPerformance] = useState<{
    correct: number;
    total: number;
    mistakes: { activityId: string; type: string; word?: string }[];
  }>({ correct: 0, total: 0, mistakes: [] });
  const [isCheckpoint, setIsCheckpoint] = useState(false);

  const fetchNext = useCallback(
    async (currentActivityId: string) => {
      if (isFetchingNext) {
        console.log('[Lesson] Skipping fetchNext, already fetching');
        return;
      }
      setIsFetchingNext(true);
      try {
        console.log('[Lesson] Fetching next activity for:', currentActivityId);
        const nextData = await fetchNextActivity(lessonId!, currentActivityId, token!);
        console.log('[Lesson] Received next activities:', nextData.activities);
        if (nextData.activities.length === 0) {
          console.warn('[Lesson] No more activities returned for:', currentActivityId);
          return;
        }
        setActivities((prev) => {
          const newActivities = nextData.activities.filter(
            (newAct) => !prev.some((act) => act.id === newAct.id)
          );
          console.log('[Lesson] Appended activities:', newActivities);
          return [...prev, ...newActivities];
        });
      } catch (err: any) {
        console.error('[Lesson] Failed to fetch next activity:', err);
        setError('Failed to load next activity. Please try again.');
      } finally {
        setIsFetchingNext(false);
      }
    },
    [lessonId, token, isFetchingNext]
  );

  useEffect(() => {
    if (!lessonId) {
      setError('Invalid lesson ID');
      setIsLoading(false);
      return;
    }
    if (!token || !user) {
      setError('Please log in to access this lesson');
      navigate('/login');
      setIsLoading(false);
      return;
    }

    const loadInitial = async () => {
      try {
        const initialData = await fetchInitialLesson(lessonId, token);
        console.log('[Lesson] Loaded initial activities:', initialData.activities);
        setActivities(initialData.activities);
        setIsCheckpoint(initialData.activities.some((a) => a.id.startsWith('review-') || a.id.startsWith('new-')));
        setIsLoading(false);
      } catch (err: any) {
        console.error('[Lesson] Failed to load initial lesson:', err);
        setError('Failed to load lesson. Please try again.');
        setIsLoading(false);
      }
    };

    loadInitial();
  }, [lessonId, token, user, navigate]);

  useEffect(() => {
    if (isLoading || isFetchingNext || currentActivityIndex >= activities.length || activities.length === 0) {
      console.log('[Lesson] Skipping preload, conditions not met:', {
        isLoading,
        isFetchingNext,
        currentActivityIndex,
        activitiesLength: activities.length,
      });
      return;
    }

    const currentActivity = activities[currentActivityIndex];
    const nextIndex = currentActivityIndex + 1;
    if (currentActivity.type === 'sentence' || nextIndex >= activities.length) {
      console.log('[Lesson] Preloading next set for:', currentActivity.id);
      fetchNext(currentActivity.id);
    }
  }, [currentActivityIndex, activities, isLoading, isFetchingNext, fetchNext]);

  const handleActivityComplete = (
    result: { word?: string; isCorrect: boolean; activityId: string },
    activityType: string
  ) => {
    setPerformance((prev) => {
      const newTotal = prev.total + 1;
      const newCorrect = prev.correct + (result.isCorrect ? 1 : 0);
      const newMistakes = result.isCorrect
        ? prev.mistakes
        : [...prev.mistakes, { activityId: result.activityId, type: activityType, word: result.word }];
      return { correct: newCorrect, total: newTotal, mistakes: newMistakes };
    });

    if (activityType === 'flashcard' && result.word && result.isCorrect) {
      setFlashcardWords((prev) => [...prev, result.word!]);
    }

    if (!result.isCorrect) {
      apiClient.post(
        `/api/lesson/${lessonId}/mistake`,
        { activity_id: result.activityId, activity_type: activityType, word: result.word },
        { headers: { Authorization: `Bearer ${token}` } }
      ).catch((err) => console.error('[Lesson] Failed to report mistake:', err));
    }

    apiClient.post(
      `/api/lesson/${lessonId}/complete`,
      { activityId: result.activityId, result: result.isCorrect ? 'correct' : 'incorrect' },
      { headers: { Authorization: `Bearer ${token}` } }
    ).catch((err) => console.error('[Lesson] Failed to report completion:', err));

    console.log('[Lesson] Completing:', { activityType, currentActivityIndex, isCorrect: result.isCorrect, activitiesLength: activities.length });

    // Only advance for flashcards
    if (activityType === 'flashcard') {
      setCurrentActivityIndex((prev) => prev + 1);
    }
  };

  const handleLessonComplete = () => {
    const score = performance.total > 0 ? (performance.correct / performance.total) * 100 : 0;
    if (isCheckpoint && score < 80) {
      setError('You need at least 80% to pass the checkpoint. Try again.');
      setCurrentActivityIndex(0);
      setFlashcardWords([]);
      setPerformance({ correct: 0, total: 0, mistakes: [] });
      setActivities([]);
      setIsLoading(true);
      fetchInitialLesson(lessonId!, token!).then((data) => {
        setActivities(data.activities);
        setIsLoading(false);
      });
    } else {
      navigate('/dashboard');
    }
  };

  if (error) {
    return (
      <div className="min-h-screen bg-[#FFFFFF] flex items-center justify-center">
        <div className="text-center text-red-600 text-lg">{error}</div>
      </div>
    );
  }

  if (isLoading) {
    return <LoadingSpinner message="Loading activity..." />;
  }

  if (currentActivityIndex >= activities.length) {
    if (isFetchingNext) {
      return <LoadingSpinner message="Loading next activity..." />;
    }
    console.log('[Lesson] Lesson completed, performance:', performance);
    return (
      <div className="min-h-screen bg-[#FFFFFF] flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-[#252B2F] mb-4">
            {isCheckpoint ? 'Checkpoint Completed!' : 'Lesson Completed!'}
          </h2>
          {isCheckpoint && (
            <p className="text-lg mb-4">
              Score: {((performance.correct / performance.total) * 100).toFixed(1)}%
            </p>
          )}
          <Button onClick={handleLessonComplete}>
            {isCheckpoint ? 'View Results' : 'Return to Dashboard'}
          </Button>
        </div>
      </div>
    );
  }

  const currentActivity = activities[currentActivityIndex];
  const nextActivity = currentActivityIndex + 1 < activities.length ? activities[currentActivityIndex + 1] : undefined;
  const lessonIdNum = parseInt(lessonId!);
  const lessonName = currentActivity.type === 'flashcard' ? (currentActivity.data.title || 'Lesson') : 'Sentence Practice';
  const nextFlashcard = nextActivity && nextActivity.type === 'flashcard' ? (nextActivity.data as FlashcardType) : undefined;

  const currentSet = Math.floor(currentActivityIndex / 3);
  const activityInSet = currentActivityIndex % 3;
  const flashcardCountInSet = activityInSet < 2 ? activityInSet + 1 : 1;
  const totalFlashcardsInSet = isCheckpoint ? activities.filter((a) => a.type === 'flashcard').length : 2;

  console.log('[Lesson] Rendering activity:', {
    id: currentActivity.id,
    type: currentActivity.type,
    index: currentActivityIndex,
    activitiesLength: activities.length,
    activities: activities.map((a) => a.id),
  });

  return (
    <div className="min-h-screen bg-[#FFFFFF] p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-[#252B2F] mb-4">
          {isCheckpoint ? 'Checkpoint Review' : lessonName}
        </h1>
        <p className="text-[#252B2F] mb-6">{currentActivity.data.subtitle || ''}</p>
        <div className="bg-[#FFFFFF] p-6 rounded-lg shadow-sm border border-[#DAE1EA]">
          {currentActivity.type === 'flashcard' && (
            <FlashcardComponent
              flashcard={currentActivity.data as FlashcardType}
              lessonName={lessonName}
              flashcardCount={flashcardCountInSet}
              totalFlashcards={totalFlashcardsInSet}
              activityId={currentActivity.id}
              onComplete={(result) => handleActivityComplete(result, 'flashcard')}
              nextFlashcard={nextFlashcard}
            />
          )}
          {currentActivity.type === 'sentence' && (
            <SentenceConstruction
              lessonId={lessonIdNum}
              flashcardWords={flashcardWords}
              sentenceData={currentActivity.data}
              activityId={currentActivity.id}
              onComplete={(result) => handleActivityComplete(result, 'sentence')}
              onNext={() => setCurrentActivityIndex((prev) => prev + 1)}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default Lesson;