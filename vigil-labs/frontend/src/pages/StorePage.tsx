import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search, Download, Trash2, CheckCircle, XCircle, Loader,
  Star, Shield, ExternalLink, Filter, Grid, List, Package,
  ToggleLeft, ToggleRight, RefreshCw, Zap, AlertTriangle,
} from 'lucide-react';
import { api } from '../utils/api';
import toast from 'react-hot-toast';

interface StoreTool {
  id: string;
  name: string;
  slug: string;
  category: string;
  description: string;
  icon?: string;
  risk_level: string;
  supports_linux: boolean;
  supports_windows: boolean;
  install_method: string;
  github_url?: string;
  tags: string[];
  downloads: number;
  rating: number;
  is_featured: boolean;
  is_verified: boolean;
  executable_name?: string;
  dependencies: string[];
  install_status: string;
  is_enabled: boolean;
}

interface Category {
  name: string;
  icon: string;
  color: string;
  description: string;
}

export default function StorePage() {
  const [tools, setTools] = useState<StoreTool[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [installingIds, setInstallingIds] = useState<Set<string>>(new Set());
  const [showInstalled, setShowInstalled] = useState(false);

  useEffect(() => {
    loadStore();
    loadCategories();
  }, []);

  const loadStore = async () => {
    try {
      const res = await api.get('/api/store/catalog');
      setTools(res.data.tools || []);
    } catch {
      toast.error('Failed to load tool store');
    } finally {
      setLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const res = await api.get('/api/store/categories');
      setCategories(res.data);
    } catch {}
  };

  const installTool = async (toolId: string) => {
    setInstallingIds(prev => new Set([...prev, toolId]));
    try {
      const res = await api.post(`/api/store/install/${toolId}`);
      if (res.data.success) {
        toast.success(`${res.data.tool_name} installed successfully!`);
        setTools(tools.map(t => t.id === toolId ? { ...t, install_status: 'installed', is_enabled: true } : t));
      } else {
        toast.error(`Installation failed: ${res.data.details?.error || 'Unknown error'}`);
        setTools(tools.map(t => t.id === toolId ? { ...t, install_status: 'failed' } : t));
      }
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Installation failed');
    } finally {
      setInstallingIds(prev => { const s = new Set(prev); s.delete(toolId); return s; });
    }
  };

  const uninstallTool = async (toolId: string) => {
    if (!confirm('Are you sure you want to uninstall this tool?')) return;
    try {
      await api.post(`/api/store/uninstall/${toolId}`);
      toast.success('Tool uninstalled');
      setTools(tools.map(t => t.id === toolId ? { ...t, install_status: 'not_installed', is_enabled: false } : t));
    } catch {
      toast.error('Uninstall failed');
    }
  };

  const toggleTool = async (toolId: string) => {
    try {
      const res = await api.post(`/api/store/toggle/${toolId}`);
      setTools(tools.map(t => t.id === toolId ? { ...t, is_enabled: res.data.is_enabled } : t));
    } catch {
      toast.error('Toggle failed');
    }
  };

  const filteredTools = tools.filter(t => {
    const matchSearch = !search ||
      t.name.toLowerCase().includes(search.toLowerCase()) ||
      t.description?.toLowerCase().includes(search.toLowerCase()) ||
      t.tags?.some(tag => tag.toLowerCase().includes(search.toLowerCase()));
    const matchCategory = !selectedCategory || t.category === selectedCategory;
    const matchInstalled = !showInstalled || t.install_status === 'installed' || t.install_status === 'available';
    return matchSearch && matchCategory && matchInstalled;
  });

  const riskBadge = (level: string) => {
    const classes: Record<string, string> = {
      low: 'badge-success', medium: 'badge-warning',
      high: 'badge-danger', critical: 'bg-red-900/30 text-red-400 border border-red-500/30',
    };
    return classes[level] || 'badge-info';
  };

  const statusIndicator = (status: string, enabled: boolean) => {
    if (status === 'installed' || status === 'available') {
      return enabled
        ? <span className="badge-success text-[10px]"><CheckCircle size={10} className="mr-0.5" />Installed</span>
        : <span className="badge-warning text-[10px]">Disabled</span>;
    }
    if (status === 'installing') return <span className="badge-info text-[10px]"><Loader size={10} className="mr-0.5 animate-spin" />Installing</span>;
    if (status === 'failed') return <span className="badge-danger text-[10px]"><XCircle size={10} className="mr-0.5" />Failed</span>;
    return <span className="text-[10px] text-vigil-text-dim px-2 py-0.5 rounded-full bg-vigil-bg border border-vigil-border">Not Installed</span>;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-vigil-text flex items-center gap-2">
            <Package size={22} className="text-vigil-primary" /> Tool Store
          </h1>
          <p className="text-sm text-vigil-text-muted">
            {tools.length} tools available • {tools.filter(t => t.install_status === 'installed' || t.install_status === 'available').length} installed
          </p>
        </div>
        <button
          onClick={loadStore}
          className="btn-secondary flex items-center gap-2 text-sm"
        >
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      {/* Category Pills */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setSelectedCategory('')}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
            !selectedCategory
              ? 'bg-vigil-primary/10 text-vigil-primary border border-vigil-primary/30'
              : 'text-vigil-text-muted hover:text-vigil-text bg-vigil-surface border border-vigil-border hover:border-vigil-primary/20'
          }`}
        >
          All
        </button>
        {categories.map(cat => (
          <button
            key={cat.name}
            onClick={() => setSelectedCategory(selectedCategory === cat.name ? '' : cat.name)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              selectedCategory === cat.name
                ? 'bg-vigil-primary/10 text-vigil-primary border border-vigil-primary/30'
                : 'text-vigil-text-muted hover:text-vigil-text bg-vigil-surface border border-vigil-border hover:border-vigil-primary/20'
            }`}
          >
            {cat.name}
          </button>
        ))}
      </div>

      {/* Search & Filters */}
      <div className="glass-panel p-4 flex flex-col sm:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-vigil-text-dim" />
          <input
            type="text"
            placeholder="Search tools by name, description, or tags..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="input-field pl-10"
          />
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowInstalled(!showInstalled)}
            className={`px-3 py-2 rounded-lg text-xs font-medium transition-all border ${
              showInstalled
                ? 'bg-vigil-success/10 text-vigil-success border-vigil-success/30'
                : 'text-vigil-text-muted border-vigil-border hover:border-vigil-primary/30'
            }`}
          >
            Installed Only
          </button>
          <div className="flex items-center gap-1 bg-vigil-bg rounded-lg p-1 border border-vigil-border">
            <button onClick={() => setViewMode('grid')} className={`p-1.5 rounded-md ${viewMode === 'grid' ? 'bg-vigil-primary/10 text-vigil-primary' : 'text-vigil-text-dim'}`}>
              <Grid size={14} />
            </button>
            <button onClick={() => setViewMode('list')} className={`p-1.5 rounded-md ${viewMode === 'list' ? 'bg-vigil-primary/10 text-vigil-primary' : 'text-vigil-text-dim'}`}>
              <List size={14} />
            </button>
          </div>
        </div>
      </div>

      {/* Tools Grid */}
      {loading ? (
        <div className="text-center py-20">
          <div className="w-8 h-8 border-2 border-vigil-primary/30 border-t-vigil-primary rounded-full animate-spin mx-auto" />
          <p className="text-vigil-text-muted mt-3">Loading tool store...</p>
        </div>
      ) : filteredTools.length === 0 ? (
        <div className="text-center py-20 glass-panel">
          <Package size={48} className="mx-auto text-vigil-text-dim mb-4" />
          <h3 className="text-lg font-medium text-vigil-text">No tools found</h3>
          <p className="text-sm text-vigil-text-muted mt-1">Try a different search or category filter</p>
        </div>
      ) : (
        <motion.div
          className={viewMode === 'grid'
            ? 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4'
            : 'space-y-3'
          }
        >
          {filteredTools.map((tool, i) => (
            <motion.div
              key={tool.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.02 }}
              className="glass-panel-hover p-5 group relative"
            >
              {/* Featured badge */}
              {tool.is_featured && (
                <div className="absolute top-3 right-3">
                  <Star size={14} className="text-vigil-warning fill-vigil-warning" />
                </div>
              )}

              {/* Header */}
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-vigil-primary/10 flex items-center justify-center shrink-0">
                  <Shield size={18} className="text-vigil-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-vigil-text truncate">{tool.name}</h3>
                    {tool.is_verified && <CheckCircle size={12} className="text-vigil-secondary shrink-0" />}
                  </div>
                  <p className="text-xs text-vigil-text-dim">{tool.category}</p>
                </div>
              </div>

              {/* Description */}
              <p className="text-sm text-vigil-text-muted mt-3 line-clamp-2">{tool.description}</p>

              {/* Tags */}
              {tool.tags?.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-3">
                  {tool.tags.slice(0, 4).map(tag => (
                    <span key={tag} className="text-[10px] px-2 py-0.5 rounded-full bg-vigil-bg border border-vigil-border text-vigil-text-dim">
                      {tag}
                    </span>
                  ))}
                </div>
              )}

              {/* Metadata */}
              <div className="flex items-center gap-3 mt-3 pt-3 border-t border-vigil-border/50">
                <span className={`badge text-[10px] ${riskBadge(tool.risk_level)}`}>{tool.risk_level}</span>
                {statusIndicator(tool.install_status, tool.is_enabled)}
                <span className="text-[10px] text-vigil-text-dim ml-auto">{tool.install_method}</span>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 mt-3">
                {tool.install_status === 'installed' || tool.install_status === 'available' ? (
                  <>
                    <button
                      onClick={() => toggleTool(tool.id)}
                      className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-all border ${
                        tool.is_enabled
                          ? 'bg-vigil-success/10 text-vigil-success border-vigil-success/30 hover:bg-vigil-success/20'
                          : 'bg-vigil-surface text-vigil-text-muted border-vigil-border hover:border-vigil-primary/30'
                      }`}
                    >
                      {tool.is_enabled ? <ToggleRight size={14} /> : <ToggleLeft size={14} />}
                      {tool.is_enabled ? 'Enabled' : 'Disabled'}
                    </button>
                    <button
                      onClick={() => uninstallTool(tool.id)}
                      className="p-2 rounded-lg text-vigil-danger hover:bg-vigil-danger/10 border border-transparent hover:border-vigil-danger/30 transition-all"
                      title="Uninstall"
                    >
                      <Trash2 size={14} />
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => installTool(tool.id)}
                    disabled={installingIds.has(tool.id)}
                    className="flex-1 btn-primary flex items-center justify-center gap-1.5 py-2 text-xs"
                  >
                    {installingIds.has(tool.id) ? (
                      <><Loader size={12} className="animate-spin" /> Installing...</>
                    ) : (
                      <><Download size={12} /> Install</>
                    )}
                  </button>
                )}
                {tool.github_url && (
                  <a
                    href={tool.github_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 rounded-lg text-vigil-text-dim hover:text-vigil-text hover:bg-vigil-hover border border-transparent hover:border-vigil-border transition-all"
                    title="View Source"
                  >
                    <ExternalLink size={14} />
                  </a>
                )}
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}
    </div>
  );
}
