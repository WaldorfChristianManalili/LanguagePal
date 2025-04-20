import { client } from './client';

export const getDialogue = async (lessonId: number) => {
  const response = await client.get(`/dialogue/generate?lesson_id=${lessonId}`);
  return response.data;
};

export const chat = async (dialogueId: number, conversation: any[]) => {
  const response = await client.post('/dialogue/chat', { dialogue_id: dialogueId, conversation });
  return response.data;
};

export const translate = async (message: string) => {
  const response = await client.post('/dialogue/translate', { message });
  return response.data;
};

export const submitDialogue = async (dialogueId: number, conversation: any[]) => {
  const response = await client.post('/dialogue/submit', { dialogue_id: dialogueId, conversation });
  return response.data;
};