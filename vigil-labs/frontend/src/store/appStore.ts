import { create } from 'zustand';

interface AppState {
  sidebarCollapsed: boolean;
  terminalOpen: boolean;
  terminalHeight: number;
  activeExecutions: string[];
  notifications: Notification[];
  
  toggleSidebar: () => void;
  toggleTerminal: () => void;
  setTerminalHeight: (height: number) => void;
  addExecution: (id: string) => void;
  removeExecution: (id: string) => void;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  dismissNotification: (id: string) => void;
}

interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: number;
}

export const useAppStore = create<AppState>((set) => ({
  sidebarCollapsed: false,
  terminalOpen: false,
  terminalHeight: 300,
  activeExecutions: [],
  notifications: [],

  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
  toggleTerminal: () => set((s) => ({ terminalOpen: !s.terminalOpen })),
  setTerminalHeight: (height) => set({ terminalHeight: height }),
  
  addExecution: (id) => set((s) => ({
    activeExecutions: [...s.activeExecutions, id],
  })),
  removeExecution: (id) => set((s) => ({
    activeExecutions: s.activeExecutions.filter((e) => e !== id),
  })),
  
  addNotification: (notification) => set((s) => ({
    notifications: [
      ...s.notifications,
      { ...notification, id: crypto.randomUUID(), timestamp: Date.now() },
    ],
  })),
  dismissNotification: (id) => set((s) => ({
    notifications: s.notifications.filter((n) => n.id !== id),
  })),
}));
