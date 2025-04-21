import { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import Register from './components/Auth/Register';
import Lesson from './pages/Lesson'; // Import Lesson.tsx
import Review from './pages/Review';
import LoadingSpinner from './components/Common/LoadingSpinner';
import { validateToken, login, signup } from './api/auth';

interface AuthContextType {
  token: string | null;
  setToken: (token: string | null) => void;
  user: { username: string; learning_language: string } | null;
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
  const [user, setUser] = useState<{ username: string; learning_language: string } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkToken = async () => {
      const storedToken = localStorage.getItem('token');
      if (storedToken) {
        try {
          const userData = await validateToken(storedToken);
          setToken(storedToken);
          setUser({ username: userData.username, learning_language: userData.learning_language });
        } catch (error) {
          console.error('Token validation failed:', error);
          setToken(null);
          setUser(null);
          localStorage.removeItem('token');
        }
      }
      setLoading(false);
    };
    checkToken();

    const interval = setInterval(async () => {
      const storedToken = localStorage.getItem('token');
      if (storedToken) {
        try {
          await validateToken(storedToken);
        } catch (error) {
          console.error('Periodic token validation failed:', error);
          setToken(null);
          setUser(null);
          localStorage.removeItem('token');
        }
      }
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const handleLogin = async (username: string, password: string) => {
    try {
      setLoading(true);
      const { access_token } = await login(username, password);
      localStorage.setItem('token', access_token);
      const userData = await validateToken(access_token);
      setToken(access_token);
      setUser({ username: userData.username, learning_language: userData.learning_language });
    } catch (error) {
      console.error('Login failed:', error);
      setToken(null);
      setUser(null);
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
      const userData = await validateToken(access_token);
      setToken(access_token);
      setUser({ username: userData.username, learning_language: userData.learning_language });
    } catch (error) {
      console.error('Registration failed:', error);
      setToken(null);
      setUser(null);
      localStorage.removeItem('token');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
  };

  if (loading) {
    return <LoadingSpinner message="Validating session..." />;
  }

  return (
    <AuthContext.Provider value={{ token, setToken, user, loading }}>
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
                <Dashboard onLogout={handleLogout} username={user?.username} />
              ) : (
                <Navigate to="/login" />
              )
            }
          />
          <Route
            path="/lesson/:lessonId"
            element={token ? <Lesson /> : <Navigate to="/login" />}
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