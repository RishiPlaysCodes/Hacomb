import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { api, getErrorMessage } from '../utils/api';

interface User {
  id: string;
  username: string;
  email?: string;
  display_name?: string;
  role: string;
  is_active: boolean;
  last_login?: string;
  created_at: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  lastActivity: number;
  
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string, email?: string) => Promise<void>;
  logout: () => void;
  refreshAuth: () => Promise<void>;
  updateActivity: () => void;
  checkInactivity: () => boolean;
}

const INACTIVITY_TIMEOUT = 30 * 60 * 1000; // 30 minutes

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      lastActivity: Date.now(),

      login: async (username: string, password: string) => {
        set({ isLoading: true });
        try {
          const res = await api.post('/api/auth/login', { username, password });
          const { access_token, refresh_token, user } = res.data;
          set({
            user,
            accessToken: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
            isLoading: false,
            lastActivity: Date.now(),
          });
        } catch (error: any) {
          set({ isLoading: false });
          throw new Error(getErrorMessage(error));
        }
      },

      register: async (username: string, password: string, email?: string) => {
        set({ isLoading: true });
        try {
          const res = await api.post('/api/auth/register', { username, password, email });
          const { access_token, refresh_token, user } = res.data;
          set({
            user,
            accessToken: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
            isLoading: false,
            lastActivity: Date.now(),
          });
        } catch (error: any) {
          set({ isLoading: false });
          throw new Error(getErrorMessage(error));
        }
      },

      logout: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        });
      },

      refreshAuth: async () => {
        const { refreshToken } = get();
        if (!refreshToken) return;
        try {
          const res = await api.post('/api/auth/refresh', { refresh_token: refreshToken });
          set({
            accessToken: res.data.access_token,
            refreshToken: res.data.refresh_token,
            lastActivity: Date.now(),
          });
        } catch {
          get().logout();
        }
      },

      updateActivity: () => set({ lastActivity: Date.now() }),

      checkInactivity: () => {
        const { lastActivity, isAuthenticated } = get();
        if (!isAuthenticated) return false;
        if (Date.now() - lastActivity > INACTIVITY_TIMEOUT) {
          get().logout();
          return true;
        }
        return false;
      },
    }),
    {
      name: 'vigil-auth',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
        lastActivity: state.lastActivity,
      }),
    }
  )
);
