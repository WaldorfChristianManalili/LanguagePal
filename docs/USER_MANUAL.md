# LanguagePal Setup Guide

## Setup

### **Verify PostgreSQL Connection**
Before running the backend, ensure that PostgreSQL is running and accepting connections.

#### **Check Connection Using `pg_isready`**
Run the following command:
```bash
pg_isready -h localhost -p 5432
```
If PostgreSQL is running, you should see:
```
localhost:5432 - accepting connections
```

### 1️. Clone the Repository
```bash
git clone https://github.com/WaldorfChristianManalili/LanguagePal.git
cd languagepal
```

### 2. Configure Environment Variables
The backend requires environment variables to connect to the database and APIs.

#### Copy the example environment file:
```bash
cp backend/.env.example backend/.env
```

#### Open `backend/.env` and update as needed:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/languagepal
SECRET_KEY=generate_a_random_key_here
DEBUG=1
APP_PORT=8000
OPENAI_API_KEY=your_openai_api_key_here
PEXELS_API_KEY=your_pexels_api_key_here
```

#### Generate a secure `SECRET_KEY`:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

#### API Keys
- Replace `OPENAI_API_KEY` and `PEXELS_API_KEY` with your own from OpenAI and Pexels.
- If left as placeholders, features like translations and flashcard images will use **mock data**.

---

## Running with Docker Compose (Recommended)
Run both the backend and frontend with a single command:
```bash
docker-compose up --build
```
- **Backend:** Runs on [http://localhost:8000](http://localhost:8000)
- **Frontend:** Runs on [http://localhost:5173](http://localhost:5173)
- The **PostgreSQL database** is automatically set up in a container.

#### To stop the containers:
```bash
docker-compose down
```

---

## Running Manually (Alternative)
If you prefer not to use Docker, you can run the backend and frontend separately.

### 🔹 Backend Setup
Navigate to the backend directory:
```bash
cd backend
```

#### Set up a virtual environment:
```bash
python -m venv env
```

#### Activate the virtual environment:
- **Windows:**
  ```bash
  env\Scripts\activate
  ```
- **macOS/Linux:**
  ```bash
  source env/bin/activate
  ```

#### Install dependencies:
```bash
pip install -r requirements.txt
```

#### Ensure PostgreSQL is running locally with:
- **User:** `postgres`
- **Password:** `postgres`
- **Database:** `languagepal`
- **Host:** `localhost`
- **Port:** `5432`

If needed, update `.env`:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/languagepal
```

#### Run the backend server:
```bash
uvicorn app.main:app --reload
```
Runs on [http://localhost:8000](http://localhost:8000)

---

### 🔹 Frontend Setup
Open a second terminal and navigate to the frontend directory:
```bash
cd frontend
```

#### Install dependencies:
```bash
npm install
```

#### Run the frontend server:
```bash
npm run dev
```
Runs on [http://localhost:5173](http://localhost:5173)

---

## Notes
- **API Keys:** If `OPENAI_API_KEY` or `PEXELS_API_KEY` are not provided, the app uses **mock data** (e.g., placeholder translations, default images). Sign up for API keys at [OpenAI](https://openai.com/) and [Pexels](https://www.pexels.com/).
- **Development Mode:** Use `DEBUG=1` in `.env` for detailed logs. Set to `0` in production.
- **Database:**
  - **Docker Compose** sets up PostgreSQL automatically.
  - For **manual setup**, ensure the database matches your `.env` configuration.

---

✅ **Your LanguagePal setup is ready! 🎉 Start learning now!**