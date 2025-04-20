import { useState, useRef } from 'react';
import { Card } from '../components/Common/Card';
import { Button } from '../components/Common/Button';
import Login from '../components/Auth/Login';
import Register from '../components/Auth/Register';
import { User, BookOpen, MessageSquare, Check } from 'lucide-react';

interface HomeProps {
  onLogin: (username: string, password: string) => Promise<void>;
  onRegister: (
    email: string,
    username: string,
    password: string,
    learning_language: string
  ) => Promise<void>;
}

function Home({ onLogin, onRegister }: HomeProps) {
  const [showLogin, setShowLogin] = useState(true);
  const loginSectionRef = useRef<HTMLDivElement>(null);

  const scrollToLogin = () => {
    loginSectionRef.current?.scrollIntoView({ behavior: 'smooth' });
    setShowLogin(true);
  };

  return (
    <div className="bg-[#FFFFFF]">
      {/* Hero Section */}
      <section className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-r from-[#1079F1] to-[#0EBE75] text-center p-6">
        <h1 className="text-5xl font-bold text-[#FFFFFF] mb-4">Learn Any Language with LanguagePal</h1>
        <p className="text-xl text-[#FFFFFF] mb-8 max-w-2xl">
          Master your chosen language with AI-driven lessons, interactive dialogues, and personalized reviews—all tailored to your learning journey.
        </p>
        <Button
          className="bg-[#0EBE75] text-[#252B2F] hover:bg-[#0EBE75] hover:text-[#FFFFFF] text-lg px-6 py-3"
          onClick={scrollToLogin}
        >
          Start Learning for Free
        </Button>
      </section>

      {/* Features Section */}
      <section className="py-16 px-6 bg-[#FFFFFF]">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-4xl font-bold text-[#252B2F] text-center mb-12">Why Choose LanguagePal?</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1: Personalized Learning */}
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-[#1079F1] rounded-full flex items-center justify-center">
                <User className="w-8 h-8 text-[#FFFFFF]" />
              </div>
              <h3 className="text-xl font-semibold text-[#252B2F] mb-2">Personalized Learning</h3>
              <p className="text-[#252B2F]">
                Choose your language (e.g., Japanese) and enjoy lessons tailored to your progress with user-specific AI sessions.
              </p>
            </div>
            {/* Feature 2: Interactive Lessons */}
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-[#1079F1] rounded-full flex items-center justify-center">
                <BookOpen className="w-8 h-8 text-[#FFFFFF]" />
              </div>
              <h3 className="text-xl font-semibold text-[#252B2F] mb-2">Interactive Lessons</h3>
              <p className="text-[#252B2F]">
                Learn through AI-generated flashcards, sentence construction, and simulated dialogues in real-world scenarios.
              </p>
            </div>
            {/* Feature 3: Smart Reviews */}
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-[#1079F1] rounded-full flex items-center justify-center">
                <Check className="w-8 h-8 text-[#FFFFFF]" />
              </div>
              <h3 className="text-xl font-semibold text-[#252B2F] mb-2">Smart Reviews</h3>
              <p className="text-[#252B2F]">
                Master your skills with AI-crafted reviews and checkpoints using spaced repetition.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-16 px-6 bg-gradient-to-b from-[#FFFFFF] to-[#F5F7FA]">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-4xl font-bold text-[#252B2F] text-center mb-12">How LanguagePal Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Step 1: Flashcard Vocabulary */}
            <div className="flex items-start">
              <div className="w-12 h-12 mr-4 bg-[#0EBE75] rounded-full flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-[#FFFFFF]" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-[#252B2F] mb-2">Flashcard Vocabulary</h3>
                <p className="text-[#252B2F]">
                  Learn with AI-generated flashcards, multiple-choice options, and detailed feedback, including images from Pexels.
                </p>
              </div>
            </div>
            {/* Step 2: Sentence Construction */}
            <div className="flex items-start">
              <div className="w-12 h-12 mr-4 bg-[#0EBE75] rounded-full flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-[#FFFFFF]" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-[#252B2F] mb-2">Sentence Construction</h3>
                <p className="text-[#252B2F]">
                  Reorder scrambled sentences in your chosen language, with AI providing feedback and explanations.
                </p>
              </div>
            </div>
            {/* Step 3: Simulated Dialogues */}
            <div className="flex items-start">
              <div className="w-12 h-12 mr-4 bg-[#0EBE75] rounded-full flex items-center justify-center">
                <MessageSquare className="w-6 h-6 text-[#FFFFFF]" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-[#252B2F] mb-2">Simulated Dialogues</h3>
                <p className="text-[#252B2F]">
                  Practice real-world conversations with AI, translate messages, and get evaluated on your performance.
                </p>
              </div>
            </div>
            {/* Step 4: AI-Focused Reviews */}
            <div className="flex items-start">
              <div className="w-12 h-12 mr-4 bg-[#0EBE75] rounded-full flex items-center justify-center">
                <Check className="w-6 h-6 text-[#FFFFFF]" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-[#252B2F] mb-2">AI-Focused Reviews</h3>
                <p className="text-[#252B2F]">
                  Review mistakes with spaced repetition, or tackle new challenges to progress with an 80% passing threshold.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Login/Register Section */}
      <section ref={loginSectionRef} className="py-16 px-6">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-[#252B2F] mb-8">Get Started Today</h2>
          <Card className="bg-[#FFFFFF] border-[#5438DC]">
            {showLogin ? (
              <>
                <Login onLogin={onLogin} />
                <p className="mt-4 text-[#252B2F]">
                  Don’t have an account?{' '}
                  <button
                    onClick={() => setShowLogin(false)}
                    className="text-[#1079F1] hover:underline"
                  >
                    Register
                  </button>
                </p>
              </>
            ) : (
              <>
                <Register onRegister={onRegister} />
                <p className="mt-4 text-[#252B2F]">
                  Already have an account?{' '}
                  <button
                    onClick={() => setShowLogin(true)}
                    className="text-[#1079F1] hover:underline"
                  >
                    Login
                  </button>
                </p>
              </>
            )}
          </Card>
        </div>
      </section>
    </div>
  );
}

export default Home;