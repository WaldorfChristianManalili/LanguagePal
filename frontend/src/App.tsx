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
import { validateToken, login, signup } from './api/auth';

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
          const user = await validateToken(storedToken);
          setToken(storedToken);
          setUsername(user.username);
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

    // Periodic token validation
    const interval = setInterval(async () => {
      const storedToken = localStorage.getItem('token');
      if (storedToken) {
        try {
          await validateToken(storedToken);
        } catch (error) {
          console.error('Periodic token validation failed:', error);
          setToken(null);
          setUsername(undefined);
          localStorage.removeItem('token');
        }
      }
    }, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const handleLogin = async (token: string) => {
    try {
      setLoading(true);
      localStorage.setItem('token', token);
      const user = await validateToken(token);
      setToken(token);
      setUsername(user.username);
    } catch (error) {
      console.error('Login failed:', error);
      setToken(null);
      setUsername(undefined);
      localStorage.removeItem('token');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (
    email: string,
    username: string,
    password: string,
    learning_language: string
  ) => {
    try {
      setLoading(true);
      await signup(email, username, password, learning_language);
      const { access_token } = await login(username, password);
      localStorage.setItem('token', access_token);
      const user = await validateToken(access_token);
      setToken(access_token);
      setUsername(user.username);
    } catch (error) {
      console.error('Registration failed:', error);
      setToken(null);
      setUsername(undefined);
      localStorage.removeItem('token');
      throw error;
    } finally {
      setLoading(false);
    }
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
            element={token ? <Navigate to="/dashboard" /> : <Home onLogin={handleLogin} onRegister={handleRegister} />}
          />
          <Route
            path="/login"
            element={token ? <Navigate to="/dashboard" /> : <Home onLogin={handleLogin} onRegister={handleRegister} />}
          />
          <Route
            path="/register"
            element={<Register onRegister={handleRegister} />}
          />
          <Route
            path="/dashboard"
            element={
              token ? (
                <Dashboard onLogout={handleLogout} username={username} />
              ) : (
                <Navigate to="/login" />
              )
            }
          />
          <Route
            path="/sentence-construction"
            element={token ? <SentenceConstruction /> : <Navigate to="/login" />}
          />
          <Route
            path="/flashcards"
            element={token ? <Flashcards /> : <Navigate to="/login" />}
          />
          <Route
            path="/word-of-the-day"
            element={token ? <WordOfTheDay /> : <Navigate to="/login" />}
          />
          <Route
            path="/dialogues"
            element={token ? <Dialogues /> : <Navigate to="/login" />}
          />
          <Route
            path="/review"
            element={token ? <Review /> : <Navigate to="/login" />}
          />
        </Routes>
      </Router>
    </AuthContext.Provider>
  );
}

export default App;