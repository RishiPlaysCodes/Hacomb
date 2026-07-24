/**
 * VIGIL LABS - API Client
 * Production-grade Axios instance with:
 * - Automatic token injection
 * - Token refresh on 401
 * - Request/response interceptors
 * - Proper error handling
 * - Request timeout
 */
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const REQUEST_TIMEOUT = 30000; // 30 seconds

// ─── API Instance ────────────────────────────────────────────────────────────

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: REQUEST_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ─── Request Interceptor ─────────────────────────────────────────────────────

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const stored = localStorage.getItem('vigil-auth');
    if (stored) {
      try {
        const { state } = JSON.parse(stored);
        if (state?.accessToken) {
          config.headers.Authorization = `Bearer ${state.accessToken}`;
        }
      } catch {
        // Invalid stored data, will be cleaned up on 401
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ─── Response Interceptor with Token Refresh ─────────────────────────────────

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value: unknown) => void;
  reject: (reason: unknown) => void;
}> = [];

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Handle 401 - attempt token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Queue this request while refresh is in progress
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const stored = localStorage.getItem('vigil-auth');
      if (stored) {
        try {
          const { state } = JSON.parse(stored);
          if (state?.refreshToken) {
            const res = await axios.post(`${BASE_URL}/api/auth/refresh`, {
              refresh_token: state.refreshToken,
            });

            const newAccessToken = res.data.access_token;
            const newRefreshToken = res.data.refresh_token;

            // Update stored tokens
            state.accessToken = newAccessToken;
            state.refreshToken = newRefreshToken;
            localStorage.setItem('vigil-auth', JSON.stringify({ state }));

            // Process queued requests
            processQueue(null, newAccessToken);

            // Retry original request
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
            return api(originalRequest);
          }
        } catch (refreshError) {
          processQueue(refreshError, null);
          // Refresh failed - clear auth and redirect to login
          localStorage.removeItem('vigil-auth');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        } finally {
          isRefreshing = false;
        }
      }
    }

    // Handle 429 - rate limited
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after'];
      console.warn(`Rate limited. Retry after ${retryAfter || 60}s`);
    }

    return Promise.reject(error);
  }
);

// ─── WebSocket URL Helper ────────────────────────────────────────────────────

export const getWSUrl = (executionId: string, token: string): string => {
  const wsBase = BASE_URL.replace('http', 'ws');
  return `${wsBase}/ws/terminal/${executionId}?token=${encodeURIComponent(token)}`;
};

// ─── Error Extraction Helper ─────────────────────────────────────────────────

export interface ApiErrorResponse {
  error?: {
    code?: string;
    message?: string;
    details?: {
      errors?: string[];
    };
  };
  detail?: string | { message?: string; errors?: string[] };
}

/**
 * Extract a user-friendly error message from an API error response.
 */
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as ApiErrorResponse | undefined;

    // New structured error format
    if (data?.error?.message) {
      return data.error.message;
    }

    // Legacy format
    if (data?.detail) {
      if (typeof data.detail === 'string') {
        return data.detail;
      }
      if (typeof data.detail === 'object' && data.detail.message) {
        return data.detail.message;
      }
    }

    // Fallback to status text
    if (error.response?.statusText) {
      return error.response.statusText;
    }

    // Network error
    if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
      return 'Cannot connect to server. Please check that the backend is running.';
    }

    if (error.code === 'ECONNABORTED') {
      return 'Request timed out. Please try again.';
    }
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'An unexpected error occurred';
}
