import {
  DialogueResponse,
  ChatRequest,
  ChatResponse,
  TranslateResponse,
  SubmitDialogueRequest,
  SubmitDialogueResponse,
} from '../types/dialogue';

const API_URL = '/api/dialogue';

export const getDialogue = async (lessonId: number): Promise<DialogueResponse> => {
  const response = await fetch(`${API_URL}/generate?lesson_id=${lessonId}`, {
    method: 'GET',
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  });
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to fetch dialogue: ${error}`);
  }
  return response.json();
};

export const submitDialogue = async (
  dialogueId: number,
  conversation: ChatRequest['conversation']
): Promise<ChatResponse> => {
  const response = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({ dialogue_id: dialogueId, conversation }),
  });
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to submit dialogue: ${error}`);
  }
  const data: ChatResponse = await response.json();
  if (!data.conversation) {
    throw new Error('Invalid response: No conversation returned');
  }
  return data;
};

export const translateMessage = async (text: string): Promise<TranslateResponse> => {
  const response = await fetch(`${API_URL}/translate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({ message: text }),
  });
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to translate message: ${error}`);
  }
  const data: TranslateResponse = await response.json();
  if (!data.translation) {
    throw new Error('Invalid response: No translation returned');
  }
  return data;
};

export const submitFinalDialogue = async (
  dialogueId: number,
  conversation: SubmitDialogueRequest['conversation']
): Promise<SubmitDialogueResponse> => {
  const response = await fetch(`${API_URL}/submit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({ dialogue_id: dialogueId, conversation }),
  });
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to submit final dialogue: ${error}`);
  }
  return response.json();
};