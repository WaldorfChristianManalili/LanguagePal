export interface SentenceData {
  scrambledWords: string[];
  originalSentence: string;
  sentenceId: number;
  englishSentence: string;
  hints: { text: string; usefulness: number }[];
}

export interface SubmitSentenceResponse {
  is_correct: boolean;
  feedback: string;
  translated_sentence: string;
  result_id: number;
  is_pinned: boolean;
  explanation: string;
  sentence_id: number;
  user_answer: string;
}

export interface FeedbackData {
  is_correct: boolean;
  feedback: string;
  correct_sentence: string;
  result_id: number;
  is_pinned: boolean;
  explanation: string;
}