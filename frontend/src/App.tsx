import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [message, setMessage] = useState({
    greeting: 'Loading...',
    description: '',
    motivation: ''
  });

  useEffect(() => {
    const fetchMessage = async () => {
      try {
        const response = await axios.get('http://localhost:8000/hello');
        setMessage(response.data);
      } catch (error) {
        setMessage({
          greeting: 'Error fetching message',
          description: 'Could not connect to backend',
          motivation: 'Check your server connection'
        });
      }
    };

    fetchMessage();
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-r from-blue-100 to-blue-200">
      <div className="text-center p-8 bg-white rounded-xl shadow-2xl">
        <h1 className="text-4xl font-bold text-blue-600 mb-4">
          {message.greeting}
        </h1>
        <p className="text-xl text-gray-700 mb-2">
          {message.description}
        </p>
        <p className="italic text-green-600">
          {message.motivation}
        </p>
      </div>
    </div>
  );
}

export default App;