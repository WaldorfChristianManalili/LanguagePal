import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../Common/Button';

interface NavbarProps {
  onLogout: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ onLogout }) => {
  const navigate = useNavigate();

  return (
    <nav className="bg-white shadow-md p-4 flex justify-between items-center">
      <div className="flex items-center">
        <Link to="/" className="text-2xl font-bold text-blue-600">
          LanguagePal
        </Link>
        <div className="ml-8 space-x-4">
          <Link to="/dashboard" className="text-gray-700 hover:text-blue-600">
            Lessons
          </Link>
          <Link to="/review" className="text-gray-700 hover:text-blue-600">
            Review
          </Link>
        </div>
      </div>
      <Button variant="outline" onClick={() => { onLogout(); navigate('/login'); }}>
        Logout
      </Button>
    </nav>
  );
};

export default Navbar;