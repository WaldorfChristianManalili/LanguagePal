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
import LoadingSpinner from './components/Common/LoadingSpinner';
import { validateToken } from './api/auth';

interface AuthContextType {
  token: string | null;
  setToken: (token: string | null) => void;
  username?: string;
  loading: boolean;
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
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkToken = async () => {
      const storedToken = localStorage.getItem('token');
      if (storedToken) {
        try {
          const response = await validateToken(storedToken);
          setToken(storedToken);
          setUsername(response.username || 'User');
          console.log('Token validated, username:', response.username);
        } catch (error) {
          console.error('Token validation failed:', error);
          setToken(null);
          setUsername(undefined);
          localStorage.removeItem('token');
        }
      }
      setLoading(false);
    };
    checkToken();
  }, []);

  const handleLogin = (newToken: string, newUsername?: string) => {
    setToken(newToken);
    setUsername(newUsername || 'User');
    localStorage.setItem('token', newToken);
  };

  const handleLogout = () => {
    setToken(null);
    setUsername(undefined);
    localStorage.removeItem('token');
  };

  if (loading) {
    return <LoadingSpinner message="Validating session..." />;
  }

  return (
    <AuthContext.Provider value={{ token, setToken, username, loading }}>
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
          <Route
            path="/register"
            element={<Register onRegister={() => {}} />}
          />
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