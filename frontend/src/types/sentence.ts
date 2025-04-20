export interface SentenceResponse {
  scrambled_words: string[];
  original_sentence: string;
  sentence_id: number;
  english_sentence: string;
  hints: { text: string; usefulness: number }[];
}

export interface SubmitSentenceRequest {
  sentence_id: number;
  user_answer: string;
}

export interface SubmitSentenceResponse {
  is_correct: boolean;
  feedback: string;
  translated_sentence: string;
  result_id: number;
  explanation: string;
  sentence_id: number;
  user_answer: string;
}