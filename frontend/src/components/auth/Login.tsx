import React, { useState } from 'react';
import { Button } from '../Common/Button';

interface LoginProps {
  onLogin: (username: string, password: string) => Promise<void>;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await onLogin(username, password);
    } catch (err) {
      setError('Invalid username or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-[#FFFFFF] rounded-lg shadow-md border border-[#5438DC]">
      <h2 className="text-2xl font-bold text-center mb-4 text-[#252B2F]">Login</h2>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-[#252B2F]">Username</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full p-2 border border-[#1079F1] rounded-lg focus:ring-2 focus:ring-[#0EBE75]"
            required
          />
        </div>
        <div className="mb-4">
          <label className="block text-[#252B2F]">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full p-2 border border-[#1079F1] rounded-lg focus:ring-2 focus:ring-[#0EBE75]"
            required
          />
        </div>
        {error && <p className="text-red-500 mb-4">{error}</p>}
        <Button
          type="submit"
          disabled={loading}
          className="w-full"
        >
          {loading ? 'Logging in...' : 'Login'}
        </Button>
      </form>
    </div>
  );
};

export default Login;