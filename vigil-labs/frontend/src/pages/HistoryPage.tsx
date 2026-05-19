import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Clock, Terminal, Search, Filter, Download, Trash2,
  CheckCircle, XCircle, AlertTriangle, Play, Loader,
} from 'lucide-react';
import { api } from '../utils/api';
import toast from 'react-hot-toast';

export default function HistoryPage() {
  const [executions, setExecutions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedExec, setSelectedExec] = useState<any>(null);

  useEffect(() => {
    loadHistory();
  }, [page, statusFilter]);

  const loadHistory = async () => {
    try {
      const params = new URLSearchParams({ page: page.toString(), per_page: '20' });
      if (statusFilter) params.set('status', statusFilter);
      if (search) params.set('search', search);
      
      const res = await api.get(`/api/executions/history?${params}`);
      setExecutions(res.data.executions);
      setTotal(res.data.total);
    } catch {} finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setPage(1);
    loadHistory();
  };

  const exportExecution = async (id: string, format: string) => {
    try {
      const res = await api.get(`/api/executions/${id}/export?format=${format}`);
      const blob = new Blob([typeof res.data === 'string' ? res.data : JSON.stringify(res.data, null, 2)], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report_${id}.${format}`;
      a.click();
      toast.success(`Exported as ${format.toUpperCase()}`);
    } catch {
      toast.error('Export failed');
    }
  };

  const deleteExecution = async (id: string) => {
    try {
      await api.delete(`/api/executions/${id}`);
      setExecutions(executions.filter(e => e.id !== id));
      toast.success('Deleted');
    } catch {
      toast.error('Failed to delete');
    }
  };

  const statusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle size={14} className="text-vigil-success" />;
      case 'failed': return <XCircle size={14} className="text-vigil-danger" />;
      case 'running': return <Loader size={14} className="text-vigil-secondary animate-spin" />;
      case 'stopped': return <AlertTriangle size={14} className="text-vigil-warning" />;
      default: return <Clock size={14} className="text-vigil-text-dim" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-vigil-text">Execution History</h1>
          <p className="text-sm text-vigil-text-muted">{total} total executions</p>
        </div>
      </div>

      {/* Filters */}
      <div className="glass-panel p-4 flex flex-col sm:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-vigil-text-dim" />
          <input
            type="text"
            placeholder="Search commands..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
            className="input-field pl-10"
          />
        </div>
        <select
          value={statusFilter}
          onChange={e => { setStatusFilter(e.target.value); setPage(1); }}
          className="input-field w-full sm:w-40"
        >
          <option value="">All Status</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
          <option value="running">Running</option>
          <option value="stopped">Stopped</option>
          <option value="timeout">Timeout</option>
        </select>
      </div>

      {/* Executions List */}
      {loading ? (
        <div className="text-center py-16">
          <div className="w-8 h-8 border-2 border-vigil-primary/30 border-t-vigil-primary rounded-full animate-spin mx-auto" />
        </div>
      ) : executions.length === 0 ? (
        <div className="text-center py-16 glass-panel">
          <Clock size={48} className="mx-auto text-vigil-text-dim mb-4" />
          <h3 className="text-lg font-medium text-vigil-text">No executions found</h3>
          <p className="text-sm text-vigil-text-muted">Run tools to see history here</p>
        </div>
      ) : (
        <div className="space-y-2">
          {executions.map((exec, i) => (
            <motion.div
              key={exec.id}
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.03 }}
              onClick={() => setSelectedExec(selectedExec?.id === exec.id ? null : exec)}
              className="glass-panel-hover p-4 cursor-pointer"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {statusIcon(exec.status)}
                  <div>
                    <p className="text-sm font-mono text-vigil-text truncate max-w-[500px]">{exec.command}</p>
                    <div className="flex items-center gap-3 mt-1">
                      <span className="text-xs text-vigil-text-dim">
                        {new Date(exec.created_at).toLocaleString()}
                      </span>
                      {exec.duration_seconds && (
                        <span className="text-xs text-vigil-text-dim">
                          Duration: {exec.duration_seconds.toFixed(1)}s
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={e => { e.stopPropagation(); exportExecution(exec.id, 'json'); }}
                    className="p-1.5 rounded hover:bg-vigil-hover text-vigil-text-dim"
                    title="Export JSON"
                  >
                    <Download size={14} />
                  </button>
                  <button
                    onClick={e => { e.stopPropagation(); deleteExecution(exec.id); }}
                    className="p-1.5 rounded hover:bg-vigil-danger/10 text-vigil-danger"
                    title="Delete"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>

              {/* Expanded Details */}
              {selectedExec?.id === exec.id && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  className="mt-3 pt-3 border-t border-vigil-border"
                >
                  {exec.stdout && (
                    <div className="mb-2">
                      <p className="text-xs text-vigil-text-dim mb-1">Output:</p>
                      <pre className="text-xs text-vigil-text bg-vigil-bg p-3 rounded-lg max-h-40 overflow-auto font-mono">
                        {exec.stdout}
                      </pre>
                    </div>
                  )}
                  {exec.stderr && (
                    <div>
                      <p className="text-xs text-vigil-danger mb-1">Errors:</p>
                      <pre className="text-xs text-vigil-danger/80 bg-vigil-danger/5 p-3 rounded-lg max-h-40 overflow-auto font-mono">
                        {exec.stderr}
                      </pre>
                    </div>
                  )}
                  <div className="flex gap-2 mt-3">
                    <button onClick={() => exportExecution(exec.id, 'txt')} className="btn-secondary text-xs py-1.5 px-3">Export TXT</button>
                    <button onClick={() => exportExecution(exec.id, 'html')} className="btn-secondary text-xs py-1.5 px-3">Export HTML</button>
                    <button onClick={() => exportExecution(exec.id, 'json')} className="btn-secondary text-xs py-1.5 px-3">Export JSON</button>
                  </div>
                </motion.div>
              )}
            </motion.div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {total > 20 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1}
            className="btn-secondary text-sm py-1.5"
          >
            Previous
          </button>
          <span className="text-sm text-vigil-text-muted">
            Page {page} of {Math.ceil(total / 20)}
          </span>
          <button
            onClick={() => setPage(page + 1)}
            disabled={page >= Math.ceil(total / 20)}
            className="btn-secondary text-sm py-1.5"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
