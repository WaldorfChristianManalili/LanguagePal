import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/Common/Card';
import { Button } from '../components/Common/Button';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import { useAuth } from '../App';
import { apiClient } from '../api/client';
import { Check } from 'lucide-react';

interface Lesson {
  id: string;
  title: string;
  subtitle: string;
  completed: boolean;
  categoryId: string;
}

interface Chapter {
  id: string;
  name: string;
  difficulty: string;
  progress: number;
  lessons: Lesson[];
}

interface DashboardResponse {
  chapters: Chapter[];
}

interface DashboardProps {
  onLogout: () => void;
  username?: string;
}

const LessonCard: React.FC<Lesson & { onClick: () => void; completed: boolean }> = ({
  title,
  subtitle,
  completed,
  onClick,
}) => (
  <div className="flex items-center mb-4">
    <div className="w-10 h-10 rounded-full border-2 border-[#1079F1] flex items-center justify-center mr-4">
      {completed && <Check className="w-6 h-6 text-[#0EBE75]" />}
    </div>
    <div
      className="flex-1 p-4 rounded-lg shadow-sm cursor-pointer bg-[#FFFFFF]"
      onClick={onClick}
    >
      <h4 className="text-lg font-semibold text-[#252B2F]">{title}</h4>
      <p className="text-sm text-[#252B2F]">{subtitle}</p>
    </div>
  </div>
);

function Dashboard({ onLogout, username = 'User' }: DashboardProps) {
  const navigate = useNavigate();
  const { token, user, loading } = useAuth();
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [selectedLevel, setSelectedLevel] = useState<string>('A1');
  const [showLevelMenu, setShowLevelMenu] = useState(false);

  useEffect(() => {
    if (!loading && !token) {
      console.log('No token found, logging out');
      onLogout();
      navigate('/login', { replace: true });
    }
  }, [navigate, onLogout, token, loading]);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const response = await apiClient.get('/dashboard', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setDashboard(response.data);
      } catch (error) {
        console.error('Failed to fetch dashboard:', error);
        setFetchError('Unable to load dashboard. Please try again later.');
      }
    };
    if (token && !loading) fetchDashboard();
  }, [token, loading]);

  const handleLevelChange = (level: string) => {
    setSelectedLevel(level);
    setShowLevelMenu(false);
  };

  const handleSkipToNextCategory = async (chapterId: string) => {
    try {
      await apiClient.post(`/chapter/${chapterId}/skip`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const response = await apiClient.get('/dashboard', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setDashboard(response.data);
    } catch (error) {
      console.error('Failed to skip category:', error);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Validating session..." />;
  }

  if (fetchError) {
    return (
      <div className="min-h-screen bg-[#FFFFFF] p-6">
        <div className="max-w-4xl mx-auto text-center text-red-600">{fetchError}</div>
      </div>
    );
  }

  if (!dashboard || !user) {
    return <LoadingSpinner message="Loading your dashboard..." />;
  }

  const handleLessonClick = (lessonId: string) => {
    navigate(`/lesson/${lessonId}`);
  };

  const filteredChapters = dashboard.chapters.filter((chapter) => chapter.difficulty === selectedLevel);

  return (
    <div className="min-h-screen bg-[#FFFFFF]">
      {/* Navbar */}
      <nav className="bg-[#FFFFFF] shadow-md p-4 flex justify-between items-center">
        <div className="flex items-center space-x-6">
          <h1 className="text-2xl font-bold text-[#1079F1]">LanguagePal</h1>
          <a href="/dashboard" className="text-[#252B2F] hover:text-[#1079F1] font-medium">
            Learn
          </a>
          <a href="/review" className="text-[#252B2F] hover:text-[#1079F1] font-medium">
            Review
          </a>
        </div>
        <div className="flex items-center space-x-4">
          <span className="text-[#252B2F]">Welcome, {username}!</span>
          <Button variant="outline" hoverBg="#1079F1" onClick={onLogout}>
            Logout
          </Button>
        </div>
      </nav>

      {/* Main Content */}
      <div className="p-6">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold text-[#252B2F] mb-6">{user.learning_language} Course</h1>
          <div className="mb-6 relative">
            <Button
              className="w-full bg-[#1079F1] text-[#FFFFFF] flex justify-between items-center hover:bg-[#1079F1] hover:text-[#FFFFFF]"
              onClick={() => setShowLevelMenu(!showLevelMenu)}
            >
              <span>
                {selectedLevel === 'A1' ? 'Beginner A1' : selectedLevel === 'A2' ? 'Intermediate A2' : 'Advanced B1'}
              </span>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
              </svg>
            </Button>
            {showLevelMenu && (
              <div className="absolute top-full left-0 w-full bg-[#FFFFFF] border border-[#1079F1] rounded-lg mt-1 shadow-lg z-10">
                {['A1', 'A2', 'B1'].map((level) => (
                  <button
                    key={level}
                    className="w-full text-left px-4 py-2 text-[#252B2F] hover:bg-[#DAE1EA] hover:text-[#252B2F]"
                    onClick={() => handleLevelChange(level)}
                  >
                    {level === 'A1' ? 'Beginner A1' : level === 'A2' ? 'Intermediate A2' : 'Advanced B1'}
                  </button>
                ))}
              </div>
            )}
          </div>

          {filteredChapters.map((chapter) => (
            <Card key={chapter.id} className="mb-6">
              <section className="p-6">
                <header className="mb-6">
                  <h3 className="text-2xl font-semibold text-[#252B2F]">{chapter.name}</h3>
                  <div
                    role="progressbar"
                    aria-valuenow={chapter.progress}
                    aria-valuemin={0}
                    aria-valuemax={100}
                    className="bg-[#DAE1EA] rounded-full h-2.5 mt-2"
                  >
                    <div
                      className="bg-[#0EBE75] h-2.5 rounded-full"
                      style={{ width: `${chapter.progress}%` }}
                    ></div>
                  </div>
                  <p className="text-sm text-[#252B2F] mt-1">{chapter.progress}% completed</p>
                </header>
                {chapter.lessons.map((lesson) => (
                  <LessonCard
                    key={lesson.id}
                    id={lesson.id}
                    title={lesson.title}
                    subtitle={lesson.subtitle}
                    completed={lesson.completed}
                    categoryId={lesson.categoryId}
                    onClick={() => handleLessonClick(lesson.id)}
                  />
                ))}
                {chapter.progress === 100 && (
                  <Button className="mt-4 bg-[#1079F1] text-[#FFFFFF]" onClick={() => handleSkipToNextCategory(chapter.id)}>
                    Skip to Next Category
                  </Button>
                )}
              </section>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;