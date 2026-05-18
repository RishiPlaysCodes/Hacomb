import { useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Terminal,
  Bell,
  Search,
  User,
  LogOut,
  Moon,
} from 'lucide-react';
import { useAppStore } from '../../store/appStore';
import { useAuthStore } from '../../store/authStore';
import { useState } from 'react';

const pageTitles: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/tools': 'Tool Registry',
  '/builder': 'Custom Tool Builder',
  '/history': 'Execution History',
  '/ai': 'AI Assistant',
  '/settings': 'Settings',
};

export default function TopBar() {
  const location = useLocation();
  const { toggleTerminal, terminalOpen, activeExecutions } = useAppStore();
  const { user, logout } = useAuthStore();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const pageTitle = pageTitles[location.pathname] ||
    (location.pathname.startsWith('/execute') ? 'Tool Execution' : 'VIGIL LABS');

  return (
    <header className="h-14 flex items-center justify-between px-6 border-b border-vigil-border bg-vigil-surface/50 backdrop-blur-sm">
      {/* Left: Page Title */}
      <div className="flex items-center gap-4">
        <h2 className="text-lg font-semibold text-vigil-text">{pageTitle}</h2>
      </div>

      {/* Center: Search */}
      <div className="flex-1 max-w-md mx-8">
        <div className="relative">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-vigil-text-dim" />
          <input
            type="text"
            placeholder="Search tools, commands, history..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-vigil-bg border border-vigil-border rounded-lg
                       text-sm text-vigil-text placeholder-vigil-text-dim
                       focus:outline-none focus:border-vigil-primary/50 transition-colors"
          />
          <kbd className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] text-vigil-text-dim
                         bg-vigil-surface px-1.5 py-0.5 rounded border border-vigil-border">
            ⌘K
          </kbd>
        </div>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-2">
        {/* Terminal Toggle */}
        <button
          onClick={toggleTerminal}
          className={`p-2 rounded-lg transition-all ${
            terminalOpen
              ? 'bg-vigil-primary/10 text-vigil-primary border border-vigil-primary/20'
              : 'text-vigil-text-muted hover:text-vigil-text hover:bg-vigil-hover'
          }`}
          title="Toggle Terminal"
        >
          <Terminal size={18} />
          {activeExecutions.length > 0 && (
            <span className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-vigil-success rounded-full animate-pulse" />
          )}
        </button>

        {/* Notifications */}
        <button className="p-2 rounded-lg text-vigil-text-muted hover:text-vigil-text hover:bg-vigil-hover transition-all relative">
          <Bell size={18} />
        </button>

        {/* User Menu */}
        <div className="relative">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-vigil-hover transition-all"
          >
            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-vigil-primary to-vigil-accent flex items-center justify-center">
              <span className="text-xs font-bold text-white">
                {user?.username?.[0]?.toUpperCase() || 'V'}
              </span>
            </div>
            <span className="text-sm text-vigil-text-muted hidden lg:block">
              {user?.display_name || user?.username}
            </span>
          </button>

          {showUserMenu && (
            <motion.div
              initial={{ opacity: 0, y: 4, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 4, scale: 0.95 }}
              className="absolute right-0 top-full mt-2 w-48 glass-panel p-2 z-50"
            >
              <div className="px-3 py-2 border-b border-vigil-border mb-1">
                <p className="text-sm font-medium">{user?.username}</p>
                <p className="text-xs text-vigil-text-dim">{user?.role}</p>
              </div>
              <button
                onClick={() => { logout(); setShowUserMenu(false); }}
                className="w-full flex items-center gap-2 px-3 py-2 text-sm text-vigil-danger hover:bg-vigil-danger/10 rounded-lg transition-colors"
              >
                <LogOut size={14} />
                Logout
              </button>
            </motion.div>
          )}
        </div>
      </div>
    </header>
  );
}
