import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Search, Filter, Grid, List, Plus, Star, StarOff,
  Play, Edit, Trash2, Shield, AlertTriangle, CheckCircle, XCircle,
} from 'lucide-react';
import { api } from '../utils/api';
import toast from 'react-hot-toast';

interface Tool {
  id: string;
  name: string;
  description: string;
  category_name?: string;
  risk_level: string;
  is_installed: boolean;
  is_favorite: boolean;
  use_count: number;
  tags: string[];
  icon?: string;
  supports_linux: boolean;
  supports_windows: boolean;
}

export default function ToolsPage() {
  const navigate = useNavigate();
  const [tools, setTools] = useState<Tool[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [search, setSearch] = useState('');
  const [filterCategory, setFilterCategory] = useState('');
  const [categories, setCategories] = useState<any[]>([]);

  useEffect(() => {
    loadTools();
    loadCategories();
  }, []);

  const loadTools = async () => {
    try {
      const res = await api.get('/api/tools/');
      setTools(res.data);
    } catch {} finally {
      setLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const res = await api.get('/api/tools/categories/all');
      setCategories(res.data);
    } catch {}
  };

  const toggleFavorite = async (toolId: string) => {
    try {
      const res = await api.post(`/api/tools/${toolId}/favorite`);
      setTools(tools.map(t => t.id === toolId ? { ...t, is_favorite: res.data.is_favorite } : t));
    } catch {
      toast.error('Failed to update favorite');
    }
  };

  const deleteTool = async (toolId: string) => {
    if (!confirm('Are you sure you want to delete this tool?')) return;
    try {
      await api.delete(`/api/tools/${toolId}`);
      setTools(tools.filter(t => t.id !== toolId));
      toast.success('Tool deleted');
    } catch {
      toast.error('Failed to delete tool');
    }
  };

  const filteredTools = tools.filter(t => {
    const matchesSearch = !search || 
      t.name.toLowerCase().includes(search.toLowerCase()) ||
      t.description?.toLowerCase().includes(search.toLowerCase()) ||
      t.tags?.some(tag => tag.toLowerCase().includes(search.toLowerCase()));
    const matchesCategory = !filterCategory || t.category_name === filterCategory;
    return matchesSearch && matchesCategory;
  });

  const riskColors: Record<string, string> = {
    low: 'badge-success',
    medium: 'badge-warning',
    high: 'badge-danger',
    critical: 'bg-red-900/30 text-red-400 border border-red-500/30',
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-vigil-text">Tool Registry</h1>
          <p className="text-sm text-vigil-text-muted">{tools.length} tools registered</p>
        </div>
        <button onClick={() => navigate('/builder')} className="btn-primary flex items-center gap-2">
          <Plus size={16} /> Add Tool
        </button>
      </div>

      {/* Filters Bar */}
      <div className="glass-panel p-4 flex flex-col sm:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-vigil-text-dim" />
          <input
            type="text"
            placeholder="Search tools..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input-field pl-10"
          />
        </div>
        <select
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
          className="input-field w-full sm:w-48"
        >
          <option value="">All Categories</option>
          {categories.map(c => (
            <option key={c.id} value={c.name}>{c.name}</option>
          ))}
        </select>
        <div className="flex items-center gap-1 bg-vigil-bg rounded-lg p-1 border border-vigil-border">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-2 rounded-md ${viewMode === 'grid' ? 'bg-vigil-primary/10 text-vigil-primary' : 'text-vigil-text-dim'}`}
          >
            <Grid size={16} />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 rounded-md ${viewMode === 'list' ? 'bg-vigil-primary/10 text-vigil-primary' : 'text-vigil-text-dim'}`}
          >
            <List size={16} />
          </button>
        </div>
      </div>

      {/* Tools Grid/List */}
      {loading ? (
        <div className="text-center py-20">
          <div className="w-8 h-8 border-2 border-vigil-primary/30 border-t-vigil-primary rounded-full animate-spin mx-auto" />
          <p className="text-vigil-text-muted mt-3">Loading tools...</p>
        </div>
      ) : filteredTools.length === 0 ? (
        <div className="text-center py-20 glass-panel">
          <Shield size={48} className="mx-auto text-vigil-text-dim mb-4" />
          <h3 className="text-lg font-medium text-vigil-text">No tools found</h3>
          <p className="text-sm text-vigil-text-muted mt-1">
            {search ? 'Try a different search' : 'Add your first tool to get started'}
          </p>
          <button onClick={() => navigate('/builder')} className="btn-primary mt-4">
            Add Tool
          </button>
        </div>
      ) : (
        <motion.div
          className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4' : 'space-y-3'}
        >
          {filteredTools.map((tool, i) => (
            <motion.div
              key={tool.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.03 }}
              className="glass-panel-hover p-5 group"
            >
              {/* Tool Header */}
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-vigil-primary/10 flex items-center justify-center">
                    <Shield size={18} className="text-vigil-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-vigil-text group-hover:text-vigil-primary transition-colors">
                      {tool.name}
                    </h3>
                    {tool.category_name && (
                      <p className="text-xs text-vigil-text-dim">{tool.category_name}</p>
                    )}
                  </div>
                </div>
                <button
                  onClick={(e) => { e.stopPropagation(); toggleFavorite(tool.id); }}
                  className="text-vigil-text-dim hover:text-vigil-warning transition-colors"
                >
                  {tool.is_favorite ? <Star size={16} className="text-vigil-warning fill-vigil-warning" /> : <StarOff size={16} />}
                </button>
              </div>

              {/* Description */}
              <p className="text-sm text-vigil-text-muted mt-3 line-clamp-2">
                {tool.description || 'No description'}
              </p>

              {/* Tags */}
              {tool.tags?.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-3">
                  {tool.tags.slice(0, 3).map(tag => (
                    <span key={tag} className="text-[10px] px-2 py-0.5 rounded-full bg-vigil-bg border border-vigil-border text-vigil-text-dim">
                      {tag}
                    </span>
                  ))}
                </div>
              )}

              {/* Footer */}
              <div className="flex items-center justify-between mt-4 pt-3 border-t border-vigil-border/50">
                <div className="flex items-center gap-2">
                  <span className={`badge text-[10px] ${riskColors[tool.risk_level] || 'badge-info'}`}>
                    {tool.risk_level}
                  </span>
                  {tool.is_installed ? (
                    <CheckCircle size={14} className="text-vigil-success" />
                  ) : (
                    <XCircle size={14} className="text-vigil-danger" />
                  )}
                </div>
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={() => navigate(`/execute/${tool.id}`)}
                    className="p-1.5 rounded-md hover:bg-vigil-success/10 text-vigil-success transition-colors"
                    title="Run"
                  >
                    <Play size={14} />
                  </button>
                  <button
                    onClick={() => navigate(`/builder/${tool.id}`)}
                    className="p-1.5 rounded-md hover:bg-vigil-primary/10 text-vigil-primary transition-colors"
                    title="Edit"
                  >
                    <Edit size={14} />
                  </button>
                  <button
                    onClick={() => deleteTool(tool.id)}
                    className="p-1.5 rounded-md hover:bg-vigil-danger/10 text-vigil-danger transition-colors"
                    title="Delete"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}
    </div>
  );
}
