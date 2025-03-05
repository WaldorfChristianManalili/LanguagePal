```
languagepal/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── language_activities.py
│   │   │   └── progress_tracking.py
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── security.py
│   │   │   └── nlp_processor.py
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── language_activity.py
│   │   │   └── progress.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user_schema.py
│   │   │   ├── activity_schema.py
│   │   │   └── progress_schema.py
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── vocabulary_service.py
│   │   │   └── conversation_service.py
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── validators.py
│   │       └── helpers.py
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   ├── test_activities.py
│   │   └── test_progress.py
│   │
│   ├── requirements.txt
│   ├── .env
│   └── Dockerfile
│
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   └── vite.svg
│   │
│   ├── src/
│   │   ├── components/
│   │   │   ├── auth/
│   │   │   │   ├── Login.tsx
│   │   │   │   ├── Register.tsx
│   │   │   │   └── AuthWrapper.tsx
│   │   │   │
│   │   │   ├── dashboard/
│   │   │   │   ├── UserDashboard.tsx
│   │   │   │   ├── ProgressTracker.tsx
│   │   │   │   └── Achievements.tsx
│   │   │   │
│   │   │   ├── language-activities/
│   │   │   │   ├── SentenceConstructionGame.tsx
│   │   │   │   ├── VocabularyFlashcards.tsx
│   │   │   │   └── ConversationPractice.tsx
│   │   │   │
│   │   │   └── common/
│   │   │       ├── Navbar.tsx
│   │   │       ├── Footer.tsx
│   │   │       └── LoadingSpinner.tsx
│   │   │
│   │   ├── contexts/
│   │   │   ├── AuthContext.tsx
│   │   │   └── LanguageContext.tsx
│   │   │
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   └── useLanguageActivities.ts
│   │   │
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   ├── authService.ts
│   │   │   └── languageService.ts
│   │   │
│   │   ├── utils/
│   │   │   ├── validation.ts
│   │   │   └── gameHelpers.ts
│   │   │
│   │   ├── styles/
│   │   │   ├── index.css
│   │   │   ├── tailwind.css
│   │   │   └── theme.css
│   │   │
│   │   ├── assets/
│   │   │   ├── react.svg
│   │   │   └── (other static assets)
│   │   │
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── vite-env.d.ts
│   │   └── App.css
│   │
│   ├── config/
│   │   ├── vite.config.ts
│   │   └── tsconfig.json
│   │
│   ├── .env
│   ├── .gitignore
│   ├── eslint.config.js
│   ├── index.html
│   ├── package.json
│   ├── README.md
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   └── Dockerfile
│
├── database/
│   └── init.sql
│
├── docs/
│   ├── API_DOCUMENTATION.md
│   ├── DEVELOPMENT_GUIDE.md
│   └── USER_MANUAL.md
│
├── docker-compose.yml
├── .gitignore
├── README.md
└── LICENSE
```