import React, { useEffect, useState } from 'react';
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

const fetchRemainingLesson = async (lessonId: string, token: string): Promise<LessonResponse> => {
  const response = await apiClient.get(`/api/lesson/${lessonId}/remaining`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
};

const Lesson: React.FC = () => {
  const { lessonId } = useParams<{ lessonId: string }>();
  const navigate = useNavigate();
  const { token, user } = useAuth();
  const [lesson, setLesson] = useState<LessonResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [currentSet, setCurrentSet] = useState(0);
  const [currentActivityInSet, setCurrentActivityInSet] = useState(0);
  const [flashcardWords, setFlashcardWords] = useState<string[]>([]);
  const [flashcardCount, setFlashcardCount] = useState(1);
  const [performance, setPerformance] = useState<{
    correct: number;
    total: number;
    mistakes: { activityId: string; type: string; word?: string }[];
  }>({ correct: 0, total: 0, mistakes: [] });
  const [isCheckpoint, setIsCheckpoint] = useState(false);
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [isRemainingLoading, setIsRemainingLoading] = useState(false);

  useEffect(() => {
    if (!lessonId) {
      setError('Invalid lesson ID');
      setIsInitialLoading(false);
      return;
    }
    if (!token || !user) {
      setError('Please log in to access this lesson');
      navigate('/login');
      setIsInitialLoading(false);
      return;
    }

    const loadLesson = async () => {
      try {
        // Load initial flashcard
        const initialData = await fetchInitialLesson(lessonId, token);
        setLesson(initialData);
        setIsInitialLoading(false);
        console.log('[Lesson] Loaded initial activities:', initialData.activities);

        // Immediately load remaining activities in the background
        setIsRemainingLoading(true);
        try {
          const remainingData = await fetchRemainingLesson(lessonId, token);
          setLesson((prev) => ({
            activities: [...(prev?.activities || []), ...remainingData.activities],
          }));
          setIsCheckpoint(
            [...initialData.activities, ...remainingData.activities].some((a) =>
              a.id.startsWith('review-') || a.id.startsWith('new-')
            )
          );
          console.log('[Lesson] Loaded remaining activities:', remainingData.activities);
        } catch (err: any) {
          console.error('[Lesson] Failed to load remaining activities:', err);
          // Non-critical error; proceed with initial activities
        } finally {
          setIsRemainingLoading(false);
        }
      } catch (err: any) {
        console.error('[Lesson] Failed to load initial lesson:', err);
        setError('Failed to load lesson. Please try again.');
        setIsInitialLoading(false);
      }
    };

    loadLesson();
  }, [lessonId, token, user, navigate]);

  const handleActivityComplete = (
    result: { word: string; isCorrect: boolean; activityId: string } | { isCorrect: boolean; activityId: string },
    activityType: string
  ) => {
    setPerformance((prev) => {
      const newTotal = prev.total + 1;
      const newCorrect = prev.correct + (result.isCorrect ? 1 : 0);
      const newMistakes = result.isCorrect
        ? prev.mistakes
        : [...prev.mistakes, { activityId: result.activityId, type: activityType, word: 'word' in result ? result.word : undefined }];
      return { correct: newCorrect, total: newTotal, mistakes: newMistakes };
    });

    if (activityType === 'flashcard' && 'word' in result && result.isCorrect) {
      setFlashcardWords((prev) => [...prev, result.word]);
    }

    if (!result.isCorrect) {
      apiClient.post(
        `/api/lesson/${lessonId}/mistake`,
        { activity_id: result.activityId, activity_type: activityType, word: 'word' in result ? result.word : undefined },
        { headers: { Authorization: `Bearer ${token}` } }
      ).catch((err) => console.error('[Lesson] Failed to report mistake:', err));
    }

    apiClient.post(
      `/api/lesson/${lessonId}/complete`,
      { activityId: result.activityId, result: result.isCorrect ? 'correct' : 'incorrect' },
      { headers: { Authorization: `Bearer ${token}` } }
    ).catch((err) => console.error('[Lesson] Failed to report completion:', err));

    console.log('[Lesson] Completing:', { activityType, currentSet, currentActivityInSet, isCorrect: result.isCorrect });
    if (activityType === 'flashcard' && currentActivityInSet === 0) {
      setCurrentActivityInSet(1);
      setFlashcardCount(2);
    } else if (activityType === 'flashcard' && currentActivityInSet === 1) {
      setCurrentActivityInSet(2);
      setFlashcardCount(1);
    } else if (activityType === 'sentence') {
      setCurrentSet((prev) => prev + 1);
      setCurrentActivityInSet(0);
      setFlashcardCount(1);
      setFlashcardWords([]); // Reset flashcardWords for next set
    }
  };

  const handleLessonComplete = () => {
    const score = performance.total > 0 ? (performance.correct / performance.total) * 100 : 0;
    if (isCheckpoint && score < 80) {
      setError('You need at least 80% to pass the checkpoint. Try again.');
      setCurrentSet(0);
      setCurrentActivityInSet(0);
      setFlashcardCount(1);
      setFlashcardWords([]);
      setPerformance({ correct: 0, total: 0, mistakes: [] });
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

  if (isInitialLoading) {
    return <LoadingSpinner message="Loading first activity..." />;
  }

  if (!lesson || !lessonId) {
    return <LoadingSpinner message="Loading lesson..." />;
  }

  const flashcardActivities = lesson.activities.filter((a: LessonActivity) => a.type === 'flashcard');
  const sentenceActivities = lesson.activities.filter((a: LessonActivity) => a.type === 'sentence');

  const flashcardStartIndex = isCheckpoint ? 0 : currentSet * 2;
  const currentFlashcards = isCheckpoint
    ? flashcardActivities
    : flashcardActivities.slice(flashcardStartIndex, flashcardStartIndex + 2);
  const currentSentence = isCheckpoint ? sentenceActivities[0] : sentenceActivities[currentSet];

  if (!currentFlashcards.length || (currentActivityInSet === 2 && !currentSentence)) {
    if (isRemainingLoading) {
      return <LoadingSpinner message="Loading remaining activities..." />;
    }
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

  const lessonIdNum = parseInt(lessonId);
  let activity: LessonActivity;
  let lessonName: string;
  let nextFlashcard: FlashcardType | undefined;

  if (currentActivityInSet < 2 && currentFlashcards[currentActivityInSet]) {
    activity = currentFlashcards[currentActivityInSet];
    lessonName = lesson.activities[0]?.data.title || 'Lesson';
    // Set next flashcard for preloading
    if (currentActivityInSet === 0 && currentFlashcards[1]) {
      nextFlashcard = currentFlashcards[1].data as FlashcardType;
    } else if (currentActivityInSet === 1 && sentenceActivities[currentSet]) {
      // No next flashcard for sentence
      nextFlashcard = undefined;
    }
  } else if (currentActivityInSet === 2 && currentSentence) {
    activity = currentSentence;
    lessonName = 'Sentence Practice';
    // Set next flashcard for the next set
    const nextSetFlashcardIndex = (currentSet + 1) * 2;
    if (flashcardActivities[nextSetFlashcardIndex]) {
      nextFlashcard = flashcardActivities[nextSetFlashcardIndex].data as FlashcardType;
    }
  } else {
    return <LoadingSpinner message="Loading activity..." />;
  }

  return (
    <div className="min-h-screen bg-[#FFFFFF] p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-[#252B2F] mb-4">
          {isCheckpoint ? 'Checkpoint Review' : lessonName}
        </h1>
        <p className="text-[#252B2F] mb-6">{activity.data.subtitle || ''}</p>
        <div className="bg-[#FFFFFF] p-6 rounded-lg shadow-sm border border-[#DAE1EA]">
          {activity.type === 'flashcard' && (
            <FlashcardComponent
              flashcard={activity.data as FlashcardType}
              lessonName={lessonName}
              flashcardCount={currentActivityInSet + 1}
              totalFlashcards={isCheckpoint ? currentFlashcards.length : 2}
              activityId={activity.id}
              onComplete={(result) => handleActivityComplete(result, 'flashcard')}
              nextFlashcard={nextFlashcard}
            />
          )}
          {activity.type === 'sentence' && (
            <SentenceConstruction
              lessonId={lessonIdNum}
              flashcardWords={flashcardWords}
              sentenceData={activity.data}
              activityId={activity.id}
              onComplete={(isCorrect: boolean) =>
                handleActivityComplete(
                  { isCorrect, activityId: activity.id },
                  'sentence'
                )
              }
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default Lesson;