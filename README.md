# LanguagePal
LanguagePal is an interactive AI chatbot designed to make language learning fun and engaging. Through dynamic conversations and exciting games, users can practice and improve their language skills while receiving real-time feedback.

*(Currently just spitballing ideas)

## Key Features
1. Sentence Construction & Correction
    - The bot gives a set of words, and the user must rearrange them into a correct sentence
    - The bot provides grammar tips based on mistakes

2. Vocabulary Building
    - Flashcard-style vocabulary learning with spaced repetition
    - Context-based word usage examples
    - Word of the day challenges

3. Conversation Practice
    - Simulated dialogues in chosen language
    - Multiple-choice responses for beginners
    - Free-form text input for advanced learners
    - Pronunciation feedback (text-based)

4. Gamification Elements (OPTIONAL)
    - Points system for completed activities
    - Difficulty-based rewards
    - Daily streaks and achievements
    - Leaderboards for motivation

5. Progress Tracking (OPTIONAL)
    - Visual representation of learning progress
    - Skill level assessment
    - Detailed performance statistics
    - Weak area identification

## Technical Stack
- **Frontend:** React, Vite, TailwindCSS
- **Backend:** FastAPI (Python)  
- **Database:** PostgreSQL with SQLAlchemy ORM  
- **Might need:**  
  - **NLP:** spaCy for basic language processing  
  - **Authentication:** Simple JWT implementation  
- **Optional:**  
  - **Containerization:** Docker with Docker Compose  
  - **Caching:** Redis for performance optimization  

# Setup Instructions
```
# Navigate to the backend
cd backend

# Setup virtual environment
python -m venv env

# Activate the virtual environment
# Windows:
env\Scripts\activate
# macOS/Linux:
source env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm

# Running Both Servers
1. Open two terminal windows.

    In the first terminal, navigate to the backend and run:
    # Windows:
    env\Scripts\activate
    # macOS/Linux:
    source env/bin/activate
    
    # Server will run on http://localhost:8000
    uvicorn app.main:app --reload

2. In the second terminal, navigate to the frontend and run:
    npm install

    # Server will run on http://localhost:5173
    npm run dev
```

![Initial Image](./docs/images/Initial.png)

# Notes
The main goal for this project was to serve as an opportunity to refine my technical skills in both AI and software deployment, ensuring that the application is optimized, accessible, and ready for real-world use. I was really curious about AI and I've seen that Python is pretty good at using it. I also wanted to try Docker for deployment since I saw (from the internet) that developers in the industry use it a lot to ensure that software runs the same way in different systems. 

For my design choices, I've decided to use FastAPI instead of Flask or Django since I might need async requests and websockets for the chatting part. I am using React for interactive user interfaces and also because it (supposedly) works well with FastAPI. I was not sure whether to choose PostgreSQL or MongoDB for this project, ended up going for PostgreSQL because the database will most likely contain structured user information data. I don't think I'll be needing MongoDB's ability to store data without a predefined schema.