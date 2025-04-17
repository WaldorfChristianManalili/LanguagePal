import axios from 'axios';

const API_URL = 'http://localhost:8000/sentence';
const CATEGORIES_URL = 'http://localhost:8000/category';

export async function getScrambledSentence(category: string) {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('No authentication token found');
  const response = await axios.get(`${API_URL}/scramble`, {
    headers: { Authorization: `Bearer ${token}` },
    params: { category },
  });
  return response.data;
}

export async function submitSentence(
  constructedSentence: string,
  originalSentence: string,
  sentenceId: number
) {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('No authentication token found');
  const response = await axios.post(
    `${API_URL}/submit`,
    {
      sentence_id: sentenceId,
      constructed_sentence: constructedSentence,
      original_sentence: originalSentence,
    },
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return response.data;
}

export async function togglePin(resultId: number, isPinned: boolean) {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('No authentication token found');
  const response = await axios.patch(
    `${API_URL}/result/${resultId}/pin`,
    { is_pinned: isPinned },
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return response.data;
}

export async function getCategories(): Promise<string[]> {
  const response = await axios.get(CATEGORIES_URL);
  return response.data;
}