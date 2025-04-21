import axios, { AxiosError } from 'axios';
import { SentenceResponse, SubmitSentenceResponse } from '../types/sentence';

const API_URL = '/api/sentence';
const CATEGORIES_URL = '/api/category';

export async function getScrambledSentence(lessonId: number, flashcardWords: string[] = []): Promise<SentenceResponse> {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('No authentication token found');
  try {
    const response = await axios.get(`${API_URL}/scramble`, {
      headers: { Authorization: `Bearer ${token}` },
      params: { lesson_id: lessonId, flashcard_words: flashcardWords.join(',') },
    });
    const data = response.data;
    return {
      scrambled_words: data.scrambled_words || [],
      original_sentence: data.original_sentence || '',
      sentence_id: data.sentence_id || 0,
      english_sentence: data.english_sentence || '',
      hints: Array.isArray(data.hints)
        ? data.hints.map((hint: any, index: number) =>
            typeof hint === 'string'
              ? { text: hint, usefulness: Math.max(3 - index, 1) }
              : { text: hint.text, usefulness: hint.usefulness }
          )
        : [],
    };
  } catch (error) {
    const axiosError = error as AxiosError<{ detail?: any }>;
    throw new Error(`Failed to fetch scrambled sentence: ${axiosError.response?.data?.detail || axiosError.message}`);
  }
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
  };
  try {
    const response = await axios.post(`${API_URL}/submit`, payload, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = response.data;
    return {
      is_correct: data.is_correct,
      feedback: data.feedback,
      translated_sentence: data.translated_sentence,
      result_id: data.result_id || data.id,
      explanation: data.explanation,
      sentence_id: data.sentence_id,
      user_answer: data.user_answer,
    };
  } catch (error) {
    const axiosError = error as AxiosError<{ detail?: any }>;
    throw new Error(`Failed to submit sentence: ${axiosError.response?.data?.detail || axiosError.message}`);
  }
}

export async function getCategories(): Promise<string[]> {
  try {
    const response = await axios.get(CATEGORIES_URL);
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError<{ detail?: any }>;
    throw new Error(`Failed to fetch categories: ${axiosError.response?.data?.detail || axiosError.message}`);
  }
}