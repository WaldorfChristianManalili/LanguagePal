import { Flashcard } from '../types/flashcard';

const API_URL = '/api/flashcard';

export const getFlashcard = async (lessonId: number): Promise<Flashcard> => {
  const response = await fetch(`${API_URL}/generate?lesson_id=${lessonId}`, {
    method: 'GET',
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  });
  if (!response.ok) throw new Error('Failed to fetch flashcard');
  return response.json();
};

export const getFlashcards = async (lessonId: number): Promise<Flashcard[]> => {
  const flashcards: Flashcard[] = [];
  for (let i = 0; i < 2; i++) {
    const flashcard = await getFlashcard(lessonId);
    flashcards.push(flashcard);
  }
  return flashcards;
};