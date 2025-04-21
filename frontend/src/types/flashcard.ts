export interface Flashcard {
  flashcard_id: number;
  word: string;
  translation: string;
  type: string;
  english_equivalents: string[];
  definition: string;
  english_definition: string;
  example_sentence: string;
  english_sentence: string;
  category: string;
  lesson_id: number;
  options: { id: string; option_text: string }[];
}