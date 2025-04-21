import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { LessonResponse, LessonActivity } from '../types/lesson';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import { Button } from '../components/Common/Button';
import { apiClient } from '../api/client';
import Flashcard from '../pages/Flashcard';
import SentenceConstruction from '../pages/SentenceConstruction';
import SimulatedDialogue from '../pages/SimulatedDialogue';

const fetchLesson = async (lessonId: string): Promise<LessonResponse> => {
  const response = await apiClient.get(`/lesson/${lessonId}`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  });
  return response.data;
};

const Lesson: React.FC = () => {
  const { lessonId } = useParams<{ lessonId: string }>();
  const navigate = useNavigate();
  const [lesson, setLesson] = useState<LessonResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [currentActivity, setCurrentActivity] = useState<number>(0);
  const [flashcardWords, setFlashcardWords] = useState<string[]>([]);

  useEffect(() => {
    if (!lessonId) {
      setError('Invalid lesson ID');
      return;
    }

    const loadLesson = async () => {
      try {
        const data = await fetchLesson(lessonId);
        setLesson(data);
      } catch (err) {
        console.error('Failed to load lesson:', err);
        setError('Failed to load lesson. Please try again.');
      }
    };

    loadLesson();
  }, [lessonId]);

  const handleActivityComplete = (result: { word?: string }, activityType: string) => {
    if (activityType === 'flashcard' && result.word) {
      setFlashcardWords((prev) => [...prev, result.word]);
    }
    setCurrentActivity((prev) => prev + 1);
  };

  const handleLessonComplete = () => {
    navigate('/dashboard');
  };

  if (error) {
    return (
      <div className="min-h-screen bg-[#FFFFFF] flex items-center justify-center">
        <div className="text-center text-red-600 text-lg">{error}</div>
      </div>
    );
  }

  if (!lesson || !lessonId) {
    return <LoadingSpinner message="Loading lesson..." />;
  }

  if (currentActivity >= lesson.activities.length) {
    return (
      <div className="min-h-screen bg-[#FFFFFF] flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-[#252B2F] mb-4">Lesson Completed!</h2>
          <Button onClick={handleLessonComplete}>Return to Dashboard</Button>
        </div>
      </div>
    );
  }

  const activity = lesson.activities[currentActivity];
  const lessonIdNum = parseInt(lessonId);

  return (
    <div className="min-h-screen bg-[#FFFFFF] p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-[#252B2F] mb-4">
          {activity.data.title || 'Lesson'}
        </h1>
        <p className="text-[#252B2F] mb-6">{activity.data.subtitle || ''}</p>
        <div className="bg-[#FFFFFF] p-6 rounded-lg shadow-sm border border-[#DAE1EA]">
          {activity.type === 'flashcard' && (
            <Flashcard
              lessonId={lessonIdNum}
              onComplete={(result) => handleActivityComplete(result, 'flashcard')}
            />
          )}
          {activity.type === 'sentence' && (
            <SentenceConstruction
              lessonId={lessonIdNum}
              flashcardWords={flashcardWords}
              onComplete={() => handleActivityComplete({}, 'sentence')}
            />
          )}
          {activity.type === 'dialogue' && (
            <SimulatedDialogue
              lessonId={lessonIdNum}
              onComplete={() => handleActivityComplete({}, 'dialogue')}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default Lesson;