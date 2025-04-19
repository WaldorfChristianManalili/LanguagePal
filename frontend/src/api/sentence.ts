import axios, { AxiosError } from 'axios';
import { SentenceData, SubmitSentenceResponse } from '../types/sentence';

const API_URL = 'http://localhost:8000/sentence';
const CATEGORIES_URL = 'http://localhost:8000/category';

export async function getScrambledSentence(category: string): Promise<SentenceData> {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('No authentication token found');
  const response = await axios.get(`${API_URL}/scramble`, {
    headers: { Authorization: `Bearer ${token}` },
    params: { category },
  });
  const data = response.data;
  return {
    scrambledWords: data.scrambled_words || [],
    originalSentence: data.original_sentence || '',
    sentenceId: data.sentence_id || 0,
    englishSentence: data.english_sentence || '',
    hints: Array.isArray(data.hints)
      ? data.hints.map((hint: any, index: number) =>
          typeof hint === 'string'
            ? { text: hint, usefulness: Math.max(3 - index, 1) }
            : { text: hint.text, usefulness: hint.usefulness }
        )
      : [],
  };
}

export async function submitSentence(
  constructedSentence: string,
  originalSentence: string,
  sentenceId: number
): Promise<SubmitSentenceResponse> {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('No authentication token found');
  if (!sentenceId || isNaN(sentenceId)) {
    throw new Error('Invalid sentence ID');
  }
  const payload = {
    sentence_id: Number(sentenceId),
    user_answer: constructedSentence || '',
    original_sentence: originalSentence || '',
  };
  console.log('Submitting payload:', payload);
  try {
    const response = await axios.post(
      `${API_URL}/submit`,
      payload,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    const data = response.data;
    console.log('Submit response:', data);
    // Normalize response
    return {
      is_correct: data.is_correct,
      feedback: data.feedback,
      translated_sentence: data.translated_sentence,
      result_id: data.result_id || data.id,
      is_pinned: data.is_pinned,
      explanation: data.explanation,
      sentence_id: data.sentence_id,
      user_answer: data.user_answer,
    };
  } catch (error) {
    const axiosError = error as AxiosError<{ detail?: any }>;
    console.error('Submit error:', axiosError.response?.data || axiosError.message);
    throw error;
  }
}

export const togglePin = async (resultId: number, isPinned: boolean, sentenceId?: number): Promise<{ is_pinned: boolean }> => {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('No authentication token found');
  try {
    const payload = { is_pinned: isPinned, sentence_id: sentenceId ?? null };
    console.log('togglePin payload:', payload);
    const response = await axios.patch(
      `${API_URL}/result/${resultId}/pin`,
      payload,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    console.log('togglePin response:', response.data);
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError<{ detail?: any }>;
    console.error('togglePin error:', axiosError.response?.data || axiosError.message);
    throw error;
  }
};

export async function getPinnedResults(): Promise<SubmitSentenceResponse[]> {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('No authentication token found');
  const response = await axios.get(`${API_URL}/results/pinned`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  console.log('Raw pinned results response:', JSON.stringify(response.data, null, 2));
  return response.data.map((data: any) => ({
    is_correct: data.is_correct,
    feedback: data.feedback,
    translated_sentence: data.translated_sentence,
    result_id: data.result_id || data.id,
    is_pinned: data.is_pinned,
    explanation: data.explanation,
    sentence_id: data.sentence_id,
    user_answer: data.user_answer,
  }));
}

export async function getCategories(): Promise<string[]> {
  const response = await axios.get(CATEGORIES_URL);
  return response.data;
}