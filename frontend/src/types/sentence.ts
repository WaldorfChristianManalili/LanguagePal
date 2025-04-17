export interface SentenceData {
  scrambledWords: string[];
  originalSentence: string;
  sentenceId: number;
}

export interface SubmitSentenceRequest {
  sentenceId: number;
  constructedSentence: string;
  originalSentence: string;
}

export interface FeedbackData {
  isCorrect: boolean;
  feedback: string;
  correctSentence: string;
  resultId: number;
  isPinned: boolean;
}