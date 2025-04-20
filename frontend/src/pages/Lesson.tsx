import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Lesson, LessonResponse } from '../types/lesson';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import { getFlashcard, submitFlashcard } from '../api/flashcard';
import { getScrambledSentence, submitSentence } from '../api/sentence';
import { getDialogue, submitDialogue, translate } from '../api/dialogue';
import { apiClient } from '../api/client';

interface Lesson {
    id: string;
    title: string;
    subtitle: string;
    completed: boolean;
    categoryId: string;
  }
  
  interface Activity {
    type: string;
    data: any;
  }
  
  interface LessonResponse {
    title: string;
    subtitle: string;
    categoryId: string;
    activities: Activity[];
  }
  
  const fetchLessonActivities = async (lessonId: string): Promise<LessonResponse> => {
    const response = await apiClient.get(`/lesson/${lessonId}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
    });
    return response.data;
  };
  
  const Lesson: React.FC = () => {
    const { lessonId } = useParams<{ lessonId: string }>();
    const [lesson, setLesson] = useState<Lesson | null>(null);
    const [activities, setActivities] = useState<LessonResponse | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [currentActivity, setCurrentActivity] = useState<number>(0);
    const [userInput, setUserInput] = useState<string>('');
    const [conversation, setConversation] = useState<any[]>([]);
    const [translations, setTranslations] = useState<{ [key: string]: string }>({});
    const [feedback, setFeedback] = useState<{ is_correct: boolean; feedback: string } | null>(null);
  
    useEffect(() => {
      const fetchLesson = async () => {
        try {
          const response = await apiClient.get(`/lesson/${lessonId}`, {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
          });
          const data = await response.data;
          setLesson({ id: lessonId!, title: data.title, subtitle: data.subtitle, completed: false, categoryId: data.categoryId });
        } catch (err) {
          setError('Failed to load lesson');
        }
      };
  
      if (lessonId) {
        fetchLesson();
        fetchLessonActivities(lessonId).then(setActivities).catch(() => setError('Failed to load activities'));
      }
    }, [lessonId]);
  
    const handleSubmit = async () => {
      if (!activities || currentActivity >= activities.activities.length) return;
      const activity = activities.activities[currentActivity];
      try {
        if (activity.type === 'flashcard') {
          await submitFlashcard(activity.data.flashcard_id, userInput);
          await apiClient.post(`/lesson/${lessonId}/complete`, { activityId: activity.id, result: { userInput } }, {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
          });
          setCurrentActivity(currentActivity + 1);
          setUserInput('');
        } else if (activity.type === 'sentence') {
          await submitSentence(activity.data.sentence_id, userInput);
          await apiClient.post(`/lesson/${lessonId}/complete`, { activityId: activity.id, result: { userInput } }, {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
          });
          setCurrentActivity(currentActivity + 1);
          setUserInput('');
        } else if (activity.type === 'dialogue') {
          if (userInput.trim()) {
            const newConversation = [...conversation, { speaker: 'user', text: userInput }];
            const response = await apiClient.post('/dialogue/chat', { dialogue_id: activity.data.dialogue_id, conversation: newConversation }, {
              headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
            });
            setConversation(response.data.conversation);
            if (response.data.is_complete) {
              await apiClient.post(`/lesson/${lessonId}/complete`, { activityId: activity.id, result: response.data }, {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
              });
              setFeedback({ is_correct: response.data.is_correct, feedback: response.data.feedback });
              setConversation([]);
            }
            setUserInput('');
          }
        }
      } catch (err) {
        setError('Failed to submit activity');
      }
    };
  
    const handleTranslate = async (message: string) => {
      try {
        const response = await translate(message);
        setTranslations({ ...translations, [message]: response.translation });
      } catch (err) {
        setError('Failed to translate message');
      }
    };
  
    if (error) {
      return <div className="text-center text-red-600">{error}</div>;
    }
  
    if (!lesson || !activities) {
      return <LoadingSpinner message="Loading lesson..." />;
    }
  
    if (currentActivity >= activities.activities.length) {
      return <div className="text-center">Lesson completed!</div>;
    }
  
    const activity = activities.activities[currentActivity];
  
    return (
      <div className="min-h-screen bg-gradient-to-r from-blue-100 to-blue-200 p-6">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-800 mb-4">{lesson.title}</h1>
          <p className="text-gray-600 mb-6">{lesson.subtitle}</p>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <h3 className="text-lg font-semibold mb-2">{activity.type}</h3>
            {activity.type === 'flashcard' && (
              <div>
                <p>Word: {activity.data.word}</p>
                <input
                  type="text"
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  className="border p-2 w-full mb-2"
                  placeholder="Enter translation"
                />
                <button
                  onClick={handleSubmit}
                  className="bg-blue-600 text-white px-4 py-2 rounded"
                >
                  Submit
                </button>
              </div>
            )}
            {activity.type === 'sentence' && (
              <div>
                <p>Scrambled: {activity.data.scrambled_words.join(', ')}</p>
                <input
                  type="text"
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  className="border p-2 w-full mb-2"
                  placeholder="Enter sentence"
                />
                <button
                  onClick={handleSubmit}
                  className="bg-blue-600 text-white px-4 py-2 rounded"
                >
                  Submit
                </button>
              </div>
            )}
            {activity.type === 'dialogue' && (
              <div>
                <p className="mb-2"><strong>Situation:</strong> {activity.data.situation}</p>
                <div className="max-h-64 overflow-y-auto mb-4">
                  {conversation.length > 0 ? (
                    conversation.map((message: any, index: number) => (
                      <div key={index} className={`mb-2 ${message.speaker === 'user' ? 'text-right' : 'text-left'}`}>
                        <p className="inline-block bg-gray-100 p-2 rounded">
                          <strong>{message.speaker}:</strong> {message.text}
                        </p>
                        {message.speaker === 'AI' && (
                          <button
                            onClick={() => handleTranslate(message.text)}
                            className="ml-2 text-blue-600 text-sm"
                          >
                            Translate
                          </button>
                        )}
                        {translations[message.text] && (
                          <p className="text-sm text-gray-600">{translations[message.text]}</p>
                        )}
                      </div>
                    ))
                  ) : (
                    activity.data.conversation.map((message: any, index: number) => (
                      <div key={index} className="mb-2 text-left">
                        <p className="inline-block bg-gray-100 p-2 rounded">
                          <strong>{message.speaker}:</strong> {message.text}
                        </p>
                        <button
                          onClick={() => handleTranslate(message.text)}
                          className="ml-2 text-blue-600 text-sm"
                        >
                          Translate
                        </button>
                        {translations[message.text] && (
                          <p className="text-sm text-gray-600">{translations[message.text]}</p>
                        )}
                      </div>
                    ))
                  )}
                </div>
                {feedback ? (
                  <div className="mb-4">
                    <p className={`font-semibold ${feedback.is_correct ? 'text-green-600' : 'text-red-600'}`}>
                      {feedback.is_correct ? 'Satisfactory!' : 'Needs Improvement'}
                    </p>
                    <p>{feedback.feedback}</p>
                  </div>
                ) : (
                  <>
                    <textarea
                      value={userInput}
                      onChange={(e) => setUserInput(e.target.value)}
                      className="border p-2 w-full mb-2"
                      placeholder="Enter your response"
                    />
                    <button
                      onClick={handleSubmit}
                      className="bg-blue-600 text-white px-4 py-2 rounded"
                    >
                      Send
                    </button>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };
  
  export default Lesson;