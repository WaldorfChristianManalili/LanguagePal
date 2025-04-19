import { FaSpinner } from 'react-icons/fa';

interface LoadingSpinnerProps {
  message?: string;
}

function LoadingSpinner({ message = 'Loading...' }: LoadingSpinnerProps) {
  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <FaSpinner className="animate-spin text-4xl text-blue-600 mb-4" />
      <p className="text-gray-600 text-lg">{message}</p>
    </div>
  );
}

export default LoadingSpinner;