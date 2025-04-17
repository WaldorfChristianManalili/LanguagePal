import { useState, useCallback } from 'react';
import * as sentenceApi from '../api/sentence';

interface SentenceData {
  scrambledWords: string[];
  originalSentence: string;
  sentenceId: number;
}

interface FeedbackData {
  isCorrect: boolean;
  feedback: string;
  correctSentence: string;
  resultId: number;
  isPinned: boolean;
}

export function useSentence() {
  const [category, setCategory] = useState<string>('');
  const [sentence, setSentence] = useState<SentenceData | null>(null);
  const [feedback, setFeedback] = useState<FeedbackData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSentence = useCallback(async (selectedCategory: string) => {
    setLoading(true);
    setError(null);
    setFeedback(null);
    try {
      const response = await sentenceApi.getScrambledSentence(selectedCategory);
      setSentence({
        scrambledWords: response.scrambled_words,
        originalSentence: response.original_sentence,
        sentenceId: response.sentence_id,
      });
      setCategory(selectedCategory);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch sentence. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  const submitSentence = useCallback(
    async (constructedSentence: string) => {
      if (!sentence) return;
      setLoading(true);
      setError(null);
      try {
        const response = await sentenceApi.submitSentence(
          constructedSentence,
          sentence.originalSentence,
          sentence.sentenceId
        );
        setFeedback({
          isCorrect: response.is_correct,
          feedback: response.feedback,
          correctSentence: response.correct_sentence,
          resultId: response.result_id,
          isPinned: response.is_pinned,
        });
      } catch (err: any) {
        setError(err.message || 'Failed to submit sentence. Please try again.');
      } finally {
        setLoading(false);
      }
    },
    [sentence]
  );

  const togglePin = useCallback(async (resultId: number, isPinned: boolean) => {
    setLoading(true);
    setError(null);
    try {
      await sentenceApi.togglePin(resultId, isPinned);
      setFeedback((prev) => (prev ? { ...prev, isPinned } : prev));
    } catch (err: any) {
      setError('Failed to toggle pin. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setSentence(null);
    setFeedback(null);
    if (category) {
      fetchSentence(category);
    }
  }, [category, fetchSentence]);

  return {
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
  };
}