```
languagepal/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py          # Makes api a package
│   │   │   ├── auth.py              # Authentication endpoints (login, register)
│   │   │   ├── sentence.py          # Sentence Construction endpoints
│   │   │   ├── flashcard.py         # Flashcard Vocabulary endpoints
│   │   │   ├── daily_word.py        # Word of the Day endpoints
│   │   │   ├── dialogue.py          # Simulated Dialogues endpoints
│   │   │   └── review.py            # Review endpoints for past results
│   │   ├── models/
│   │   │   ├── __init__.py          # Makes models a package
│   │   │   ├── user.py              # User model (id, username, password, language, etc.)
│   │   │   ├── sentence.py          # Sentence model (id, difficulty, text, language)
│   │   │   ├── category.py          # Category model (id, name)
│   │   │   ├── flashcard.py         # Flashcard session and word models
│   │   │   ├── daily_word.py        # Daily word model (id, word, definition, date)
│   │   │   ├── situation.py         # Situation model (id, description, language)
│   │   │   └── dialogue.py          # Dialogue session model (id, thread_id, user_id)
│   │   ├── schemas/
│   │   │   ├── __init__.py          # Makes schemas a package
│   │   │   ├── user.py              # Pydantic schema for user data
│   │   │   ├── sentence.py          # Schema for sentences
│   │   │   ├── category.py          # Schema for categories
│   │   │   ├── flashcard.py         # Schema for flashcards
│   │   │   ├── daily_word.py        # Schema for daily words
│   │   │   ├── situation.py         # Schema for situations
│   │   │   └── dialogue.py          # Schema for dialogues
│   │   ├── crud/
│   │   │   ├── __init__.py          # Makes crud a package
│   │   │   ├── user.py              # CRUD operations for users
│   │   │   ├── sentence.py          # CRUD for sentences
│   │   │   ├── category.py          # CRUD for categories
│   │   │   ├── flashcard.py         # CRUD for flashcards
│   │   │   ├── daily_word.py        # CRUD for daily words
│   │   │   ├── situation.py         # CRUD for situations
│   │   │   └── dialogue.py          # CRUD for dialogues
│   │   ├── utils/
│   │   │   ├── __init__.py          # Makes utils a package
│   │   │   ├── openai.py            # OpenAI API integration (translations, dialogues)
│   │   │   ├── pexels.py            # Pexels API integration (image fetching)
│   │   │   └── jwt.py               # JWT token creation and validation
│   │   ├── __init__.py              # Makes app a Python package
│   │   ├── main.py                  # FastAPI app entry point
│   │   └── database.py              # SQLAlchemy setup (engine, session, base)
│   ├── requirements.txt             # Python dependencies (fastapi, sqlalchemy, etc.)
│   ├── .env                         # Environment variables (API keys, DB URL)
│   └── Dockerfile                   # Docker configuration for backend
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Auth/
│   │   │   │   ├── Login.tsx        # Login form component
│   │   │   │   └── Register.tsx     # Registration form component
│   │   │   ├── SentenceConstruction/
│   │   │   │   ├── DifficultySelect.tsx # Dropdown for difficulty
│   │   │   │   ├── ScrambledSentence.tsx # Draggable scrambled sentence
│   │   │   │   └── Feedback.tsx     # Display AI feedback
│   │   │   ├── Flashcards/
│   │   │   │   ├── CategorySelect.tsx # Dropdown for category selection
│   │   │   │   └── Flashcard.tsx    # Flip card with word, definition, image
│   │   │   ├── WordOfTheDay/
│   │   │   │   ├── WordleGame.tsx   # Wordle minigame interface
│   │   │   │   └── WordReveal.tsx   # Show word, definition, usage
│   │   │   ├── Dialogues/
│   │   │   │   ├── SituationDisplay.tsx # Display selected situation
│   │   │   │   ├── ChatInterface.tsx # Chat UI with translate button
│   │   │   │   └── Evaluation.tsx   # Show conversation evaluation
│   │   │   ├── Reviews/
│   │   │   │   ├── SentenceReview.tsx # Display past sentence results
│   │   │   │   └── FlashcardReview.tsx # Display past flashcard results
│   │   │   └── Common/
│   │   │       ├── Button.tsx       # Reusable button component
│   │   │       ├── Card.tsx         # Reusable card component
│   │   │       └── PinnedToggle.tsx # Reusable toggle for pinning results
│   │   ├── pages/
│   │   │   ├── Home.tsx             # Home page with login and register
│   │   │   ├── Dashboard.tsx        # Dashboard with feature selection after login
│   │   │   ├── SentenceConstruction.tsx # Dedicated page for Sentence Construction
│   │   │   ├── Flashcards.tsx       # Dedicated page for Flashcards
│   │   │   ├── WordOfTheDay.tsx     # Dedicated page for Word of the Day
│   │   │   ├── Dialogues.tsx        # Dedicated page for Dialogues
│   │   │   └── Review.tsx           # Review pinned and past results
│   │   ├── api/
│   │   │   ├── client.ts            # Base API client (axios/fetch)
│   │   │   ├── auth.ts              # Auth-specific API calls
│   │   │   ├── sentence.ts          # Sentence Construction API calls
│   │   │   ├── flashcard.ts         # Flashcard Vocabulary API calls
│   │   │   ├── dailyWord.ts         # Word of the Day API calls
│   │   │   ├── dialogue.ts          # Simulated Dialogues API calls
│   │   │   └── review.ts            # Review API calls
│   │   ├── hooks/
│   │   │   ├── useAuth.ts           # Hook for authentication state
│   │   │   ├── useSentence.ts       # Hook for sentence construction logic
│   │   │   ├── useFlashcard.ts      # Hook for flashcard logic
│   │   │   ├── useDailyWord.ts      # Hook for Word of the Day logic
│   │   │   └── useDialogue.ts       # Hook for dialogue logic
│   │   ├── types/
│   │   │   ├── index.ts             # Export all types
│   │   │   ├── user.ts              # User-related types (e.g., language)
│   │   │   ├── sentence.ts          # Sentence-related types
│   │   │   ├── flashcard.ts         # Flashcard-related types
│   │   │   ├── dailyWord.ts         # Daily word-related types
│   │   │   └── dialogue.ts          # Dialogue-related types
│   │   ├── App.tsx                  # Main app component (routing)
│   │   ├── index.tsx                # Entry point for React
│   │   └── store.ts                 # State management (Redux or Context)
│   ├── public/
│   │   └── vite.svg
│   ├── package.json                 # Node dependencies and scripts
│   ├── vite.config.ts               # Vite configuration
│   ├── tsconfig.json                # TypeScript configuration
│   ├── tsconfig.node.json           # TypeScript configuration for Node
│   └── Dockerfile                   # Docker configuration for frontend
├── docker-compose.yml               # Docker Compose for frontend, backend, DB
├── README.md                        # Project documentation
└── .gitignore                       # Git ignore file (node_modules, .env, etc.)
```