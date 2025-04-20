import React from 'react';

const Review: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-100 to-blue-200 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">Review Past Results</h1>
        <p className="text-gray-600">Review your incorrect answers here.</p>
        {/* Add logic to fetch and display /api/review */}
      </div>
    </div>
  );
};

export default Review;