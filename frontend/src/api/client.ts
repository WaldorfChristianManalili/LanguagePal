import axios, { AxiosInstance } from 'axios';

// Create an Axios instance with base configuration
export const apiClient: AxiosInstance = axios.create({
  baseURL: 'http://localhost:8000', // Adjust to your backend URL (e.g., from .env or config)
  headers: {
    'Content-Type': 'application/json',
  },
});

// Optional: Add response interceptor to handle 401 errors globally
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to home on unauthorized
      localStorage.removeItem('token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);