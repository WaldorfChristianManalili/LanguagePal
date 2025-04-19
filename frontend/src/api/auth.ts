import { apiClient } from './client';

// Validate token with backend
export const validateToken = async (token: string) => {
  try {
    const response = await apiClient.get('/auth/validate', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data; // Expecting { username: string, email: string, learning_language: string, ... }
  } catch (error) {
    throw new Error('Invalid or expired token');
  }
};

// Login function
export const login = async (username: string, password: string) => {
  const response = await apiClient.post('/auth/login', { username, password });
  return response.data; // Expecting { access_token: string, token_type: string, username: string }
};

// Register function
export const register = async (username: string, email: string, password: string, learning_language: string) => {
  const response = await apiClient.post('/auth/register', { username, email, password, learning_language });
  return response.data; // Expecting { username: string, email: string, learning_language: string, ... }
};