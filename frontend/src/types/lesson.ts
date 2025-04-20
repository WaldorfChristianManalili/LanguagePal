export interface Lesson {
    id: string;
    title: string;
    subtitle: string;
    image: string;
    completed: boolean;
    categoryId: string;
  }
  
  export interface Category {
    id: string;
    name: string;
    chapter: number;
    difficulty: string;
    progress: number;
    lessons: Lesson[];
  }
  
  export interface LessonActivity {
    id: string;
    type: 'flashcard' | 'sentence' | 'dialogue';
    data: any;
    completed: boolean;
  }
  
  export interface LessonResponse {
    activities: LessonActivity[];
  }