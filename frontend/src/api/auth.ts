import { apiClient } from './client';

interface LoginResponse {
  access_token: string;
  token_type: string;
}

interface UserResponse {
  id: number;
  username: string;
  email: string;
  learning_language: string;
  is_active: boolean;
  created_at: string;
  last_login: string | null;
  openai_thread_id: string | null;
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  try {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    const response = await apiClient.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  } catch (error) {
    throw new Error('Invalid username or password');
  }
}

export async function signup(
  email: string,
  username: string,
  password: string,
  learning_language: string
): Promise<void> {
  try {
    await apiClient.post('/auth/register', {
      email,
      username,
      password,
      learning_language,
    });
  } catch (error) {
    throw new Error('Failed to sign up');
  }
}

export async function validateToken(token: string): Promise<UserResponse> {
  try {
    const response = await apiClient.get('/auth/validate', {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error) {
    throw new Error('Failed to validate token');
  }
}