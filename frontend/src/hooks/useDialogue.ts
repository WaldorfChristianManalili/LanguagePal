import { useState, useCallback } from 'react';
import { DialogueResponse, SubmitDialogueResponse, TranslateResponse, ChatResponse, Message } from '../types/dialogue';
import { getDialogue, submitDialogue as apiSubmitDialogue, translateMessage as apiTranslateMessage, submitFinalDialogue as apiSubmitFinalDialogue } from '../api/dialogue';

interface DialogueState {
  dialogue: DialogueResponse | null;
  feedback: SubmitDialogueResponse | null;
  translations: { [key: string]: string };
  dialogueLoading: boolean;
  submitLoading: boolean;
  translateLoading: boolean;
  error: string | null;
}

interface UseDialogueReturn {
  dialogue: DialogueResponse | null;
  feedback: SubmitDialogueResponse | null;
  translations: { [key: string]: string };
  dialogueLoading: boolean;
  submitLoading: boolean;
  translateLoading: boolean;
  error: string | null;
  fetchDialogue: (lessonId: number) => Promise<void>;
  submitDialogue: (dialogueId: number, conversation: Message[]) => Promise<void>;
  translateMessage: (messageId: string, text: string) => Promise<void>;
  submitFinalDialogue: (dialogueId: number, conversation: Message[]) => Promise<void>;
  reset: () => void;
}

export const useDialogue = (): UseDialogueReturn => {
  const [state, setState] = useState<DialogueState>({
    dialogue: null,
    feedback: null,
    translations: {},
    dialogueLoading: false,
    submitLoading: false,
    translateLoading: false,
    error: null,
  });

  const fetchDialogue = useCallback(async (lessonId: number) => {
    setState((prev) => ({
      ...prev,
      dialogue: null,
      feedback: null,
      translations: {},
      dialogueLoading: true,
      error: null,
    }));
    try {
      const response = await getDialogue(lessonId);
      setState((prev) => ({
        ...prev,
        dialogue: response,
        dialogueLoading: false,
      }));
    } catch (err: any) {
      setState((prev) => ({
        ...prev,
        error: `Failed to fetch dialogue: ${err.message || 'Unknown error'}`,
        dialogueLoading: false,
      }));
    }
  }, []);

  const submitDialogue = useCallback(async (dialogueId: number, conversation: Message[]) => {
    setState((prev) => ({ ...prev, submitLoading: true, error: null }));
    try {
      const response = await apiSubmitDialogue(dialogueId, conversation);
      if (!response || !response.conversation) {
        throw new Error('No conversation returned from server');
      }
      setState((prev) => ({
        ...prev,
        dialogue: prev.dialogue
          ? {
              ...prev.dialogue,
              conversation: response.conversation,
            }
          : null,
        feedback: prev.feedback, // Preserve existing feedback
        submitLoading: false,
      }));
    } catch (err: any) {
      setState((prev) => ({
        ...prev,
        error: `Failed to submit dialogue: ${err.message || 'Unknown error'}`,
        submitLoading: false,
      }));
    }
  }, []);

  const submitFinalDialogue = useCallback(async (dialogueId: number, conversation: Message[]) => {
    setState((prev) => ({ ...prev, submitLoading: true, error: null }));
    try {
      const response = await apiSubmitFinalDialogue(dialogueId, conversation);
      setState((prev) => ({
        ...prev,
        feedback: response,
        submitLoading: false,
      }));
    } catch (err: any) {
      setState((prev) => ({
        ...prev,
        error: `Failed to submit dialogue: ${err.message || 'Unknown error'}`,
        submitLoading: false,
      }));
    }
  }, []);

  const translateMessage = useCallback(async (messageId: string, text: string) => {
    setState((prev) => ({ ...prev, translateLoading: true, error: null }));
    try {
      // The API function only accepts text parameter
      const response = await apiTranslateMessage(text);
      setState((prev) => ({
        ...prev,
        translations: { ...prev.translations, [messageId]: response.translation },
        translateLoading: false,
      }));
    } catch (err: any) {
      setState((prev) => ({
        ...prev,
        error: `Failed to translate message: ${err.message || 'Unknown error'}`,
        translateLoading: false,
      }));
    }
  }, []);

  const reset = useCallback(() => {
    setState({
      dialogue: null,
      feedback: null,
      translations: {},
      dialogueLoading: false,
      submitLoading: false,
      translateLoading: false,
      error: null,
    });
  }, []);

  return {
    dialogue: state.dialogue,
    feedback: state.feedback,
    translations: state.translations,
    dialogueLoading: state.dialogueLoading,
    submitLoading: state.submitLoading,
    translateLoading: state.translateLoading,
    error: state.error,
    fetchDialogue,
    submitDialogue,
    submitFinalDialogue,
    translateMessage,
    reset,
  };
};