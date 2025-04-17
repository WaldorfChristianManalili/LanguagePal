import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Card } from '../components/Common/Card';
import { Button } from '../components/Common/Button';
import Login from '../components/Auth/Login';
import Register from '../components/Auth/Register';

interface HomeProps {
  onLogin: (token: string) => void;
}

function Home({ onLogin }: HomeProps) {
  const [showLogin, setShowLogin] = useState(true);

  const handleRegister = () => {
    setShowLogin(true); // Switch to login after registration
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-r from-blue-100 to-blue-200">
      <div className="max-w-2xl mx-auto text-center p-6">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">Welcome to LanguagePal</h1>
        <Card className="mb-6">
          <p className="text-lg text-gray-600">
            LanguagePal is an interactive AI chatbot designed to make language learning fun and engaging.
            Through dynamic conversations and exciting games, users can practice and improve their
            language skills while receiving real-time feedback.
          </p>
        </Card>
        <Card>
          {showLogin ? (
            <>
              <Login onLogin={onLogin} />
              <p className="mt-4 text-gray-600">
                Don’t have an account?{' '}
                <button
                  onClick={() => setShowLogin(false)}
                  className="text-blue-600 hover:underline"
                >
                  Register
                </button>
              </p>
            </>
          ) : (
            <>
              <Register onRegister={handleRegister} />
              <p className="mt-4 text-gray-600">
                Already have an account?{' '}
                <button
                  onClick={() => setShowLogin(true)}
                  className="text-blue-600 hover:underline"
                >
                  Login
                </button>
              </p>
            </>
          )}
        </Card>
        <div className="mt-6">
          <Link to="/dashboard">
            <Button variant="outline">Explore as Guest</Button>
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Home;