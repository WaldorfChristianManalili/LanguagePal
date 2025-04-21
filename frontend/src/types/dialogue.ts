export interface Message {
  id: string;
  speaker: 'user' | 'AI';
  text: string;
}

export interface DialogueResponse {
  dialogue_id: number;
  situation: string;
  conversation: Message[];
  category: string;
  lesson_id: number;
}

export interface ChatRequest {
  dialogue_id: number;
  conversation: Message[];
}

export interface ChatResponse {
  dialogue_id: number;
  conversation: Message[];
  is_complete: boolean;
}

export interface TranslateResponse {
  translation: string;
}

export interface SubmitDialogueRequest {
  dialogue_id: number;
  conversation: Message[];
}

export interface SubmitDialogueResponse {
  is_correct: boolean;
  feedback: string;
  result_id?: number; // Optional, as it may not be used
  dialogue_id?: number; // Optional, as it may not be used
}