import { useState, useCallback } from 'react';
import { SentenceData, SubmitSentenceResponse } from '../types/sentence';
import { getScrambledSentence, submitSentence as submitSentenceApi, togglePin, getPinnedResults } from '../api/sentence';

interface SentenceState {
  category: string | null;
  sentence: SentenceData | null;
  feedback: SubmitSentenceResponse | null;
  sentencePinned: boolean;
  sentenceLoading: boolean;
  submitLoading: boolean;
  pinLoading: boolean;
  error: string | null;
}

interface UseSentenceReturn {
  category: string | null;
  setCategory: (category: string) => void;
  sentence: SentenceData | null;
  feedback: SubmitSentenceResponse | null;
  sentencePinned: boolean;
  sentenceLoading: boolean;
  submitLoading: boolean;
  pinLoading: boolean;
  error: string | null;
  fetchSentence: (category: string) => Promise<void>;
  submitSentence: (constructedSentence: string) => Promise<void>;
  togglePin: (resultId: number, isPinned: boolean, sentenceId?: number) => Promise<void>;
  reset: () => void;
}

export const useSentence = (): UseSentenceReturn => {
  const [state, setState] = useState<SentenceState>({
    category: null,
    sentence: null,
    feedback: null,
    sentencePinned: false,
    sentenceLoading: false,
    submitLoading: false,
    pinLoading: false,
    error: null,
  });

  const setCategory = useCallback((category: string) => {
    setState(prev => ({ ...prev, category }));
  }, []);

  const fetchSentence = useCallback(async (category: string) => {
    console.log(`Fetching sentence for category: ${category}`);
    setState(prev => ({
      ...prev,
      sentence: null, // Clear sentence immediately
      feedback: null, // Clear feedback
      sentenceLoading: true,
      error: null,
    }));
    try {
      const response = await getScrambledSentence(category);
      let sentencePinned = false;
      try {
        const pinnedResults = await getPinnedResults();
        sentencePinned = pinnedResults.some(result => result.sentence_id === response.sentenceId);
        console.log('useSentence: fetchSentence pinned check:', { sentenceId: response.sentenceId, sentencePinned });
      } catch (err) {
        console.error('useSentence: Error fetching pinned results:', err);
      }
      setState(prev => ({
        ...prev,
        sentence: response,
        feedback: null,
        sentencePinned,
        sentenceLoading: false,
      }));
    } catch (err: any) {
      const errorMessage = err.message || 'Unknown error';
      console.error('useSentence: fetchSentence error:', { category, error: errorMessage });
      setState(prev => ({
        ...prev,
        error: `Failed to fetch sentence: ${errorMessage}`,
        sentenceLoading: false,
      }));
    }
  }, []);

  const submitSentence = useCallback(async (constructedSentence: string) => {
    if (!state.sentence || !state.sentence.sentenceId) {
      setState(prev => ({ ...prev, error: 'No valid sentence available' }));
      return;
    }
    setState(prev => ({ ...prev, submitLoading: true, error: null })); // Fixed typo: true443 -> true
    try {
      const response = await submitSentenceApi(
        constructedSentence,
        state.sentence.originalSentence,
        state.sentence.sentenceId
      );
      let sentencePinned = false;
      try {
        const pinnedResults = await getPinnedResults();
        sentencePinned = pinnedResults.some(result => result.sentence_id === response.sentence_id);
        console.log('useSentence: submitSentence pinned check:', { sentenceId: response.sentence_id, sentencePinned });
      } catch (err) {
        console.error('useSentence: Error fetching pinned results:', err);
      }
      setState(prev => ({
        ...prev,
        feedback: response,
        sentencePinned,
        submitLoading: false,
      }));
    } catch (err: any) {
      const errorMessage = err.message || 'Unknown error';
      console.error('useSentence: submitSentence error:', errorMessage);
      setState(prev => ({
        ...prev,
        error: 'Failed to submit sentence: ' + errorMessage,
        submitLoading: false,
      }));
    }
  }, [state.sentence]);

  const handleTogglePin = useCallback(async (resultId: number, isPinned: boolean, sentenceId?: number) => {
    setState(prev => ({ ...prev, pinLoading: true, error: null }));
    try {
      console.log('useSentence: togglePin called:', { resultId, isPinned, sentenceId });
      const response = await togglePin(resultId, isPinned, sentenceId);
      console.log('useSentence: togglePin response:', { resultId, is_pinned: response.is_pinned });
      let sentencePinned = false;
      try {
        const pinnedResults = await getPinnedResults();
        sentencePinned = pinnedResults.some(result => result.sentence_id === state.sentence?.sentenceId);
        console.log('useSentence: Post-toggle pinned check:', { sentenceId: state.sentence?.sentenceId, sentencePinned });
      } catch (err) {
        console.error('useSentence: Error fetching pinned results:', err);
      }
      setState(prev => ({
        ...prev,
        sentencePinned,
        pinLoading: false,
      }));
    } catch (err: any) {
      const errorMessage = err.message || 'Unknown error';
      console.error('useSentence: togglePin error:', { resultId, error: errorMessage });
      setState(prev => ({
        ...prev,
        error: `Failed to toggle pin: ${errorMessage}`,
        pinLoading: false,
      }));
    }
  }, [state.sentence]);

  const reset = useCallback(() => {
    console.log('Resetting sentence state');
    setState(prev => ({
      ...prev,
      sentence: null, // Clear sentence
      feedback: null,
      sentencePinned: false,
      error: null,
    }));
  }, []);

  return {
    category: state.category,
    setCategory,
    sentence: state.sentence,
    feedback: state.feedback,
    sentencePinned: state.sentencePinned,
    sentenceLoading: state.sentenceLoading,
    submitLoading: state.submitLoading,
    pinLoading: state.pinLoading,
    error: state.error,
    fetchSentence,
    submitSentence,
    togglePin: handleTogglePin,
    reset,
  };
};