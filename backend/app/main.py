from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello, LanguagePal!"}

@app.get("/hello")
def hello_world():
    return {
        "greeting": "Welcome to LanguagePal!",
        "description": "Your language learning journey starts here.",
        "motivation": "Let's learn together!"
    }