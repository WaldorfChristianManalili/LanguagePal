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