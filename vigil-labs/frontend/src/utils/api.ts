import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const stored = localStorage.getItem('vigil-auth');
  if (stored) {
    try {
      const { state } = JSON.parse(stored);
      if (state?.accessToken) {
        config.headers.Authorization = `Bearer ${state.accessToken}`;
      }
    } catch {}
  }
  return config;
});

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const stored = localStorage.getItem('vigil-auth');
      if (stored) {
        try {
          const { state } = JSON.parse(stored);
          if (state?.refreshToken) {
            const res = await axios.post(`${BASE_URL}/api/auth/refresh`, {
              refresh_token: state.refreshToken,
            });
            
            state.accessToken = res.data.access_token;
            state.refreshToken = res.data.refresh_token;
            localStorage.setItem('vigil-auth', JSON.stringify({ state }));
            
            originalRequest.headers.Authorization = `Bearer ${res.data.access_token}`;
            return api(originalRequest);
          }
        } catch {
          localStorage.removeItem('vigil-auth');
          window.location.href = '/login';
        }
      }
    }
    
    return Promise.reject(error);
  }
);

export const getWSUrl = (execution_id: string, token: string) => {
  const wsBase = BASE_URL.replace('http', 'ws');
  return `${wsBase}/ws/terminal/${execution_id}?token=${token}`;
};
