import { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import Register from './components/Auth/Register';
import SentenceConstruction from './pages/SentenceConstruction';
import Flashcards from './pages/Flashcards';
import WordOfTheDay from './pages/WordOfTheDay';
import Dialogues from './pages/Dialogues';
import Review from './pages/Review';

// Auth context to manage token
interface AuthContextType {
  token: string | null;
  setToken: (token: string | null) => void;
  username?: string; // Optional, as username may not be available
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

function App() {
  const [token, setToken] = useState<string | null>(null);
  const [username, setUsername] = useState<string | undefined>(undefined);

  // Check for token in localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
      // Optionally fetch username from backend using token
      // Example: fetchUsername(storedToken).then(setUsername);
    }
  }, []);

  const handleLogin = (newToken: string) => {
    setToken(newToken);
    localStorage.setItem('token', newToken);
    // Optionally set username if provided by Login component
    // setUsername(username);
  };

  const handleLogout = () => {
    setToken(null);
    setUsername(undefined);
    localStorage.removeItem('token');
  };

  return (
    <AuthContext.Provider value={{ token, setToken, username }}>
      <Router>
        <Routes>
          <Route
            path="/"
            element={token ? <Navigate to="/dashboard" /> : <Home onLogin={handleLogin} />}
          />
          <Route
            path="/login"
            element={token ? <Navigate to="/dashboard" /> : <Home onLogin={handleLogin} />}
          />
          <Route path="/register" element={<Register onRegister={() => {}} />} />
          <Route
            path="/dashboard"
            element={
              token ? (
                <Dashboard onLogout={handleLogout} username={username} />
              ) : (
                <Navigate to="/" />
              )
            }
          />
          <Route
            path="/sentence-construction"
            element={token ? <SentenceConstruction /> : <Navigate to="/" />}
          />
          <Route
            path="/flashcards"
            element={token ? <Flashcards /> : <Navigate to="/" />}
          />
          <Route
            path="/word-of-the-day"
            element={token ? <WordOfTheDay /> : <Navigate to="/" />}
          />
          <Route
            path="/dialogues"
            element={token ? <Dialogues /> : <Navigate to="/" />}
          />
          <Route
            path="/review"
            element={token ? <Review /> : <Navigate to="/" />}
          />
        </Routes>
      </Router>
    </AuthContext.Provider>
  );
}

export default App;