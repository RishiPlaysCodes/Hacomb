import { useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  LayoutDashboard,
  Wrench,
  PlusCircle,
  History,
  Brain,
  Settings,
  ChevronLeft,
  ChevronRight,
  Shield,
  Terminal,
  Zap,
} from 'lucide-react';
import { useAppStore } from '../../store/appStore';
import { cn } from '../../utils/cn';

const navItems = [
  { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard', color: 'text-vigil-primary' },
  { path: '/tools', icon: Wrench, label: 'Tool Registry', color: 'text-vigil-secondary' },
  { path: '/builder', icon: PlusCircle, label: 'Tool Builder', color: 'text-vigil-accent' },
  { path: '/history', icon: History, label: 'History', color: 'text-vigil-warning' },
  { path: '/ai', icon: Brain, label: 'AI Assistant', color: 'text-vigil-neon' },
  { path: '/settings', icon: Settings, label: 'Settings', color: 'text-vigil-text-muted' },
];

export default function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { sidebarCollapsed, toggleSidebar, activeExecutions } = useAppStore();

  return (
    <motion.aside
      animate={{ width: sidebarCollapsed ? 72 : 240 }}
      transition={{ duration: 0.2, ease: 'easeInOut' }}
      className="h-full flex flex-col bg-vigil-surface border-r border-vigil-border relative z-20"
    >
      {/* Logo */}
      <div className="flex items-center h-16 px-4 border-b border-vigil-border">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-vigil-primary to-vigil-accent flex items-center justify-center shadow-glow-sm">
            <Shield size={20} className="text-white" />
          </div>
          {!sidebarCollapsed && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <h1 className="text-lg font-bold text-gradient">VIGIL</h1>
              <p className="text-[10px] text-vigil-text-dim -mt-1 tracking-wider">LABS</p>
            </motion.div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path ||
            (item.path !== '/' && location.pathname.startsWith(item.path));
          
          return (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className={cn(
                'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group relative',
                isActive
                  ? 'bg-vigil-primary/10 text-vigil-primary border border-vigil-primary/20'
                  : 'text-vigil-text-muted hover:text-vigil-text hover:bg-vigil-hover'
              )}
            >
              {isActive && (
                <motion.div
                  layoutId="sidebar-indicator"
                  className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-6 bg-vigil-primary rounded-r-full"
                />
              )}
              <item.icon
                size={20}
                className={cn(
                  'shrink-0 transition-colors',
                  isActive ? item.color : 'group-hover:text-vigil-text'
                )}
              />
              {!sidebarCollapsed && (
                <span className="text-sm font-medium truncate">{item.label}</span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Active processes indicator */}
      {activeExecutions.length > 0 && (
        <div className="mx-3 mb-3">
          <div className={cn(
            'flex items-center gap-2 px-3 py-2 rounded-lg bg-vigil-success/10 border border-vigil-success/20',
            sidebarCollapsed && 'justify-center'
          )}>
            <Zap size={16} className="text-vigil-success animate-pulse" />
            {!sidebarCollapsed && (
              <span className="text-xs text-vigil-success font-medium">
                {activeExecutions.length} Running
              </span>
            )}
          </div>
        </div>
      )}

      {/* Collapse Toggle */}
      <div className="border-t border-vigil-border p-3">
        <button
          onClick={toggleSidebar}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg
                     text-vigil-text-dim hover:text-vigil-text hover:bg-vigil-hover transition-all"
        >
          {sidebarCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
          {!sidebarCollapsed && <span className="text-xs">Collapse</span>}
        </button>
      </div>
    </motion.aside>
  );
}
