import { useState, useCallback } from 'react';
import { getFlashcard } from '../api/flashcard';
import { Flashcard } from '../types/flashcard';

interface UseFlashcardReturn {
  flashcard: Flashcard | null;
  flashcardLoading: boolean;
  error: string | null;
  fetchFlashcard: (lessonId: number) => Promise<void>;
  reset: () => void;
}

export const useFlashcard = (): UseFlashcardReturn => {
  const [state, setState] = useState<{
    flashcard: Flashcard | null;
    flashcardLoading: boolean;
    error: string | null;
  }>({
    flashcard: null,
    flashcardLoading: false,
    error: null,
  });

  const fetchFlashcard = useCallback(async (lessonId: number) => {
    setState((prev) => ({ ...prev, flashcardLoading: true, error: null }));
    try {
      const response = await getFlashcard(lessonId);
      setState((prev) => ({
        ...prev,
        flashcard: response,
        flashcardLoading: false,
      }));
    } catch (err: any) {
      setState((prev) => ({
        ...prev,
        error: `Failed to fetch flashcard: ${err.message || 'Unknown error'}`,
        flashcardLoading: false,
      }));
    }
  }, []);

  const reset = useCallback(() => {
    setState({
      flashcard: null,
      flashcardLoading: false,
      error: null,
    });
  }, []);

  return {
    flashcard: state.flashcard,
    flashcardLoading: state.flashcardLoading,
    error: state.error,
    fetchFlashcard,
    reset,
  };
};