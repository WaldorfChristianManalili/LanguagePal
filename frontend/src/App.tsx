import React, { useState } from 'react';
import Login from './components/auth/Login';
import Register from './components/auth/Register';

function App() {
  const [token, setToken] = useState<string | null>(null);
  const [showLogin, setShowLogin] = useState(true);

  const handleLogin = (token: string) => {
    setToken(token);
    localStorage.setItem('token', token); // Persist token
  };

  const handleRegister = () => {
    setShowLogin(true); // Switch to login after registration
  };

  const handleLogout = () => {
    setToken(null);
    localStorage.removeItem('token');
  };

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-r from-blue-100 to-blue-200">
        {showLogin ? (
          <>
            <Login onLogin={handleLogin} />
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
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-r from-blue-100 to-blue-200">
      <div className="text-center p-8 bg-white rounded-xl shadow-2xl">
        <h1 className="text-4xl font-bold text-blue-600 mb-4">Welcome!</h1>
        <p className="text-xl text-gray-700 mb-2">You are logged in.</p>
        <button
          onClick={handleLogout}
          className="mt-4 bg-red-600 text-white p-2 rounded hover:bg-red-700"
        >
          Logout
        </button>
      </div>
    </div>
  );
}

export default App;