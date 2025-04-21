import { useState, useCallback } from 'react';
import { SentenceResponse, SubmitSentenceResponse } from '../types/sentence';
import { getScrambledSentence, submitSentence as submitSentenceApi } from '../api/sentence';

interface SentenceState {
  lessonId: number | null;
  sentence: SentenceResponse | null;
  feedback: SubmitSentenceResponse | null;
  sentenceLoading: boolean;
  submitLoading: boolean;
  error: string | null;
}

interface UseSentenceReturn {
  lessonId: number | null;
  setLessonId: (lessonId: number) => void;
  sentence: SentenceResponse | null;
  feedback: SubmitSentenceResponse | null;
  sentenceLoading: boolean;
  submitLoading: boolean;
  error: string | null;
  fetchSentence: (lessonId: number, flashcardWords?: string[]) => Promise<void>;
  submitSentence: (constructedSentence: string) => Promise<void>;
  reset: () => void;
}

export const useSentence = (): UseSentenceReturn => {
  const [state, setState] = useState<SentenceState>({
    lessonId: null,
    sentence: null,
    feedback: null,
    sentenceLoading: false,
    submitLoading: false,
    error: null,
  });

  const setLessonId = useCallback((lessonId: number) => {
    setState((prev) => ({ ...prev, lessonId }));
  }, []);

  const fetchSentence = useCallback(async (lessonId: number, flashcardWords: string[] = []) => {
    console.log(`Fetching sentence: lessonId=${lessonId}, flashcardWords=${flashcardWords}`);
    setState((prev) => ({
      ...prev,
      sentence: null,
      feedback: null,
      sentenceLoading: true,
      error: null,
    }));
    try {
      const response = await getScrambledSentence(lessonId, flashcardWords);
      setState((prev) => ({
        ...prev,
        lessonId,
        sentence: response,
        feedback: null,
        sentenceLoading: false,
      }));
    } catch (err: any) {
      const errorMessage = err.message || 'Unknown error';
      console.error('useSentence: fetchSentence error:', { lessonId, error: errorMessage });
      setState((prev) => ({
        ...prev,
        error: `Failed to fetch sentence: ${errorMessage}`,
        sentenceLoading: false,
      }));
    }
  }, []);

  const submitSentence = useCallback(
    async (constructedSentence: string) => {
      if (!state.sentence || !state.sentence.sentence_id) {
        setState((prev) => ({ ...prev, error: 'No valid sentence available' }));
        return;
      }
      setState((prev) => ({ ...prev, submitLoading: true, error: null }));
      try {
        const response = await submitSentenceApi(
          constructedSentence,
          state.sentence.original_sentence,
          state.sentence.sentence_id
        );
        setState((prev) => ({
          ...prev,
          feedback: response,
          submitLoading: false,
        }));
      } catch (err: any) {
        const errorMessage = err.message || 'Unknown error';
        console.error('useSentence: submitSentence error:', errorMessage);
        setState((prev) => ({
          ...prev,
          error: 'Failed to submit sentence: ' + errorMessage,
          submitLoading: false,
        }));
      }
    },
    [state.sentence]
  );

  const reset = useCallback(() => {
    console.log('Resetting sentence state');
    setState((prev) => ({
      ...prev,
      sentence: null,
      feedback: null,
      error: null,
    }));
  }, []);

  return {
    lessonId: state.lessonId,
    setLessonId,
    sentence: state.sentence,
    feedback: state.feedback,
    sentenceLoading: state.sentenceLoading,
    submitLoading: state.submitLoading,
    error: state.error,
    fetchSentence,
    submitSentence,
    reset,
  };
};