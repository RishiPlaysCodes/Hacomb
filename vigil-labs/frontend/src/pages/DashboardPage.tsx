import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  Wrench, Activity, Clock, Shield, Terminal, Cpu, HardDrive,
  MemoryStick, TrendingUp, Play, Star, AlertTriangle, Package,
  GitBranch, Brain, Zap,
} from 'lucide-react';
import { api } from '../utils/api';

interface SystemInfo {
  platform: string;
  cpu_count: number;
  memory_total_gb: number;
  memory_available_gb: number;
  disk_usage_percent: number;
}

export default function DashboardPage() {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    total_tools: 0,
    total_executions: 0,
    running_processes: 0,
    favorites: 0,
  });
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [recentExecutions, setRecentExecutions] = useState<any[]>([]);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const [sysRes, histRes, toolsRes] = await Promise.allSettled([
        api.get('/api/system/stats'),
        api.get('/api/executions/history?per_page=5'),
        api.get('/api/tools/'),
      ]);

      if (sysRes.status === 'fulfilled') {
        setSystemInfo(sysRes.value.data.system);
        setStats(prev => ({ ...prev, running_processes: sysRes.value.data.running_processes }));
      }
      if (histRes.status === 'fulfilled') {
        setRecentExecutions(histRes.value.data.executions || []);
        setStats(prev => ({ ...prev, total_executions: histRes.value.data.total }));
      }
      if (toolsRes.status === 'fulfilled') {
        const tools = toolsRes.value.data;
        setStats(prev => ({
          ...prev,
          total_tools: tools.length,
          favorites: tools.filter((t: any) => t.is_favorite).length,
        }));
      }
    } catch {}
  };

  const statCards = [
    { label: 'Registered Tools', value: stats.total_tools, icon: Wrench, color: 'from-vigil-primary to-indigo-600' },
    { label: 'Total Executions', value: stats.total_executions, icon: Activity, color: 'from-vigil-secondary to-cyan-600' },
    { label: 'Running Now', value: stats.running_processes, icon: Play, color: 'from-vigil-success to-emerald-600' },
    { label: 'Favorites', value: stats.favorites, icon: Star, color: 'from-vigil-warning to-amber-600' },
  ];

  const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.08 } },
  };
  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 },
  };

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-panel p-6 relative overflow-hidden"
      >
        <div className="absolute inset-0 bg-gradient-to-r from-vigil-primary/5 to-vigil-accent/5" />
        <div className="relative z-10">
          <h1 className="text-2xl font-bold text-vigil-text">
            Welcome to <span className="text-gradient">VIGIL LABS</span>
          </h1>
          <p className="text-vigil-text-muted mt-1">
            Your unified CLI tool management platform. Build labs, run tools, automate workflows.
          </p>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        {statCards.map((stat) => (
          <motion.div key={stat.label} variants={item} className="glass-panel-hover p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-vigil-text">{stat.value}</p>
                <p className="text-sm text-vigil-text-muted mt-0.5">{stat.label}</p>
              </div>
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${stat.color} flex items-center justify-center shadow-lg`}>
                <stat.icon size={22} className="text-white" />
              </div>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* System Monitor */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-panel p-5"
        >
          <h3 className="text-sm font-semibold text-vigil-text-muted uppercase tracking-wider mb-4 flex items-center gap-2">
            <Cpu size={14} /> System Status
          </h3>
          {systemInfo ? (
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-vigil-text-muted">Platform</span>
                  <span className="text-vigil-text font-medium">{systemInfo.platform}</span>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-vigil-text-muted">CPU Cores</span>
                  <span className="text-vigil-text font-medium">{systemInfo.cpu_count}</span>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1.5">
                  <span className="text-vigil-text-muted">Memory</span>
                  <span className="text-vigil-text font-medium">
                    {systemInfo.memory_available_gb}GB / {systemInfo.memory_total_gb}GB
                  </span>
                </div>
                <div className="w-full h-2 bg-vigil-bg rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-vigil-primary to-vigil-secondary rounded-full transition-all"
                    style={{ width: `${((systemInfo.memory_total_gb - systemInfo.memory_available_gb) / systemInfo.memory_total_gb * 100)}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1.5">
                  <span className="text-vigil-text-muted">Disk Usage</span>
                  <span className="text-vigil-text font-medium">{systemInfo.disk_usage_percent}%</span>
                </div>
                <div className="w-full h-2 bg-vigil-bg rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${
                      systemInfo.disk_usage_percent > 80 ? 'bg-vigil-danger' : 'bg-gradient-to-r from-vigil-success to-vigil-secondary'
                    }`}
                    style={{ width: `${systemInfo.disk_usage_percent}%` }}
                  />
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center text-vigil-text-dim py-8">Loading system info...</div>
          )}
        </motion.div>

        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="lg:col-span-2 glass-panel p-5"
        >
          <h3 className="text-sm font-semibold text-vigil-text-muted uppercase tracking-wider mb-4 flex items-center gap-2">
            <Clock size={14} /> Recent Executions
          </h3>
          {recentExecutions.length > 0 ? (
            <div className="space-y-2">
              {recentExecutions.map((exec: any) => (
                <div
                  key={exec.id}
                  className="flex items-center justify-between p-3 rounded-lg bg-vigil-bg/50 hover:bg-vigil-hover transition-colors cursor-pointer"
                >
                  <div className="flex items-center gap-3">
                    <Terminal size={16} className="text-vigil-text-dim" />
                    <div>
                      <p className="text-sm text-vigil-text font-mono truncate max-w-[300px]">
                        {exec.command}
                      </p>
                      <p className="text-xs text-vigil-text-dim">
                        {new Date(exec.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <span className={`badge ${
                    exec.status === 'completed' ? 'badge-success' :
                    exec.status === 'failed' ? 'badge-danger' :
                    exec.status === 'running' ? 'badge-info' : 'badge-warning'
                  }`}>
                    {exec.status}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <Terminal size={40} className="mx-auto text-vigil-text-dim mb-3" />
              <p className="text-vigil-text-muted">No executions yet</p>
              <p className="text-sm text-vigil-text-dim mt-1">Run your first tool to see activity here</p>
              <button
                onClick={() => navigate('/tools')}
                className="btn-primary mt-4 text-sm"
              >
                Browse Tools
              </button>
            </div>
          )}
        </motion.div>
      </div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <button
          onClick={() => navigate('/store')}
          className="glass-panel-hover p-5 text-left group"
        >
          <div className="w-10 h-10 rounded-lg bg-vigil-neon/10 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
            <Package size={20} className="text-vigil-neon" />
          </div>
          <h4 className="font-medium text-vigil-text">Tool Store</h4>
          <p className="text-xs text-vigil-text-dim mt-1">Browse and install tools from the marketplace</p>
        </button>

        <button
          onClick={() => navigate('/builder')}
          className="glass-panel-hover p-5 text-left group"
        >
          <div className="w-10 h-10 rounded-lg bg-vigil-accent/10 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
            <Wrench size={20} className="text-vigil-accent" />
          </div>
          <h4 className="font-medium text-vigil-text">AI Tool Builder</h4>
          <p className="text-xs text-vigil-text-dim mt-1">Create custom tools with AI assistance</p>
        </button>

        <button
          onClick={() => navigate('/workflows')}
          className="glass-panel-hover p-5 text-left group"
        >
          <div className="w-10 h-10 rounded-lg bg-vigil-warning/10 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
            <GitBranch size={20} className="text-vigil-warning" />
          </div>
          <h4 className="font-medium text-vigil-text">Workflows</h4>
          <p className="text-xs text-vigil-text-dim mt-1">Chain tools into automated pipelines</p>
        </button>

        <button
          onClick={() => navigate('/ai')}
          className="glass-panel-hover p-5 text-left group"
        >
          <div className="w-10 h-10 rounded-lg bg-vigil-secondary/10 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
            <Brain size={20} className="text-vigil-secondary" />
          </div>
          <h4 className="font-medium text-vigil-text">AI Agent</h4>
          <p className="text-xs text-vigil-text-dim mt-1">Get intelligent help and automation</p>
        </button>
      </motion.div>
    </div>
  );
}
