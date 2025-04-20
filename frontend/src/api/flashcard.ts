import { client } from './client';

export const getFlashcard = async (lessonId: number) => {
  const response = await client.get(`/flashcard/generate?lesson_id=${lessonId}`);
  return response.data;
};

export const submitFlashcard = async (flashcardId: number, userAnswer: string) => {
  const response = await client.post('/flashcard/submit', { flashcard_id: flashcardId, user_answer: userAnswer });
  return response.data;
};