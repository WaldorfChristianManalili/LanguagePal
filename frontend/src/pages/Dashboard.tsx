import { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Card } from '../components/Common/Card';
import { Button } from '../components/Common/Button';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import { useAuth } from '../App'; // Import useAuth to access token

interface DashboardProps {
  onLogout: () => void;
  username?: string;
}

function Dashboard({ onLogout, username = 'User' }: DashboardProps) {
  const navigate = useNavigate();
  const { token, loading } = useAuth();

  useEffect(() => {
    if (!loading && !token) {
      console.log('No token found, logging out');
      onLogout();
      navigate('/', { replace: true });
    } else if (!loading) {
      console.log('Token found, staying on dashboard');
    }
  }, [navigate, onLogout, token, loading]);

  if (loading) {
    return <LoadingSpinner message="Validating session..." />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-100 to-blue-200 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800">
            Welcome, {username}!
          </h1>
          <Button variant="outline" onClick={onLogout}>
            Logout
          </Button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <h2 className="text-xl font-semibold mb-4">Sentence Construction</h2>
            <p className="mb-4">Practice building sentences by rearranging scrambled words.</p>
            <Link to="/sentence-construction">
              <Button variant="primary">Start Now</Button>
            </Link>
          </Card>
          <Card>
            <h2 className="text-xl font-semibold mb-4">Flashcard Vocabulary</h2>
            <p className="mb-4">Learn new words with interactive flashcards.</p>
            <Link to="/flashcards">
              <Button variant="primary">Start Now</Button>
            </Link>
          </Card>
          <Card>
            <h2 className="text-xl font-semibold mb-4">Word of the Day</h2>
            <p className="mb-4">Play a Wordle-style game to learn a new word daily.</p>
            <Link to="/word-of-the-day">
              <Button variant="primary">Start Now</Button>
            </Link>
          </Card>
          <Card>
            <h2 className="text-xl font-semibold mb-4">Simulated Dialogues</h2>
            <p className="mb-4">Practice conversations in real-world scenarios.</p>
            <Link to="/dialogues">
              <Button variant="primary">Start Now</Button>
            </Link>
          </Card>
        </div>
        <div className="mt-6 text-center">
          <Link to="/review">
            <Button variant="outline">View Past Results</Button>
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;