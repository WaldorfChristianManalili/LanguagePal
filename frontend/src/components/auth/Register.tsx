import React, { useState } from 'react';
import { Button } from '../Common/Button';

interface RegisterProps {
  onRegister: (
    email: string,
    username: string,
    password: string,
    learning_language: string
  ) => Promise<void>;
}

const Register: React.FC<RegisterProps> = ({ onRegister }) => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [learningLanguage, setLearningLanguage] = useState('Spanish');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await onRegister(email, username, password, learningLanguage);
    } catch (err) {
      setError('Registration failed. Username or email may already exist.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-[#FFFFFF] rounded-lg shadow-md border border-[#5438DC]">
      <h2 className="text-2xl font-bold text-center mb-4 text-[#252B2F]">Register</h2>
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
          <label className="block text-[#252B2F]">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
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
        <div className="mb-4">
          <label className="block text-[#252B2F]">Learning Language</label>
          <select
            value={learningLanguage}
            onChange={(e) => setLearningLanguage(e.target.value)}
            className="w-full p-2 border border-[#1079F1] rounded-lg focus:ring-2 focus:ring-[#0EBE75]"
          >
            <option value="English">English</option>
            <option value="Spanish">Spanish</option>
            <option value="French">French</option>
            <option value="German">German</option>
            <option value="Japanese">Japanese</option>
            <option value="Chinese (Simplified)">Chinese (Simplified)</option>
            <option value="Portuguese">Portuguese</option>
            <option value="Italian">Italian</option>
            <option value="Korean">Korean</option>
            <option value="Filipino (Tagalog)">Filipino (Tagalog)</option>
          </select>
        </div>
        {error && <p className="text-red-500 mb-4">{error}</p>}
        <Button
          type="submit"
          disabled={loading}
          className="w-full"
        >
          {loading ? 'Registering...' : 'Register'}
        </Button>
      </form>
    </div>
  );
};

export default Register;