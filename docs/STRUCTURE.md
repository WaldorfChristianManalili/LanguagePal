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
│   │   ├── favicon.ico
│   │   └── manifest.json
│   │
│   ├── src/
│   │   ├── index.js
│   │   ├── App.js
│   │   │
│   │   ├── components/
│   │   │   ├── auth/
│   │   │   │   ├── Login.js
│   │   │   │   ├── Register.js
│   │   │   │   └── AuthWrapper.js
│   │   │   │
│   │   │   ├── dashboard/
│   │   │   │   ├── UserDashboard.js
│   │   │   │   ├── ProgressTracker.js
│   │   │   │   └── Achievements.js
│   │   │   │
│   │   │   ├── language-activities/
│   │   │   │   ├── SentenceConstructionGame.js
│   │   │   │   ├── VocabularyFlashcards.js
│   │   │   │   └── ConversationPractice.js
│   │   │   │
│   │   │   └── common/
│   │   │       ├── Navbar.js
│   │   │       ├── Footer.js
│   │   │       └── LoadingSpinner.js
│   │   │
│   │   ├── contexts/
│   │   │   ├── AuthContext.js
│   │   │   └── LanguageContext.js
│   │   │
│   │   ├── hooks/
│   │   │   ├── useAuth.js
│   │   │   └── useLanguageActivities.js
│   │   │
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   ├── authService.js
│   │   │   └── languageService.js
│   │   │
│   │   ├── utils/
│   │   │   ├── validation.js
│   │   │   └── gameHelpers.js
│   │   │
│   │   └── styles/
│   │       ├── index.css
│   │       ├── tailwind.css
│   │       └── theme.css
│   │
│   ├── package.json
│   ├── .env
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