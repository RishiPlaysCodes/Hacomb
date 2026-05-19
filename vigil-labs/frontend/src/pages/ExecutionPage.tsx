import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Play, Square, Terminal, Shield, Clock, Save, Copy,
  CheckCircle, XCircle, AlertTriangle, Loader, Eye, EyeOff,
} from 'lucide-react';
import { api, getWSUrl } from '../utils/api';
import { useAuthStore } from '../store/authStore';
import { useAppStore } from '../store/appStore';
import toast from 'react-hot-toast';

interface ToolArg {
  name: string;
  label: string;
  description?: string;
  field_type: string;
  flag?: string;
  placeholder?: string;
  default_value?: string;
  tooltip?: string;
  example?: string;
  is_required: boolean;
  options: { value: string; label: string }[];
  width: string;
  is_advanced: boolean;
  group?: string;
}

export default function ExecutionPage() {
  const { toolId } = useParams();
  const navigate = useNavigate();
  const { accessToken } = useAuthStore();
  const { addExecution, removeExecution } = useAppStore();
  
  const [tool, setTool] = useState<any>(null);
  const [formValues, setFormValues] = useState<Record<string, any>>({});
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [executionId, setExecutionId] = useState<string | null>(null);
  const [output, setOutput] = useState<string[]>([]);
  const [status, setStatus] = useState<string>('idle');
  const [command, setCommand] = useState('');
  const outputRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (toolId) loadTool(toolId);
    return () => { wsRef.current?.close(); };
  }, [toolId]);

  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [output]);

  const loadTool = async (id: string) => {
    try {
      const res = await api.get(`/api/tools/${id}`);
      setTool(res.data);
      // Set defaults
      const defaults: Record<string, any> = {};
      res.data.arguments?.forEach((arg: ToolArg) => {
        if (arg.default_value) defaults[arg.name] = arg.default_value;
        if (arg.field_type === 'checkbox' || arg.field_type === 'toggle') {
          defaults[arg.name] = defaults[arg.name] === 'true' || false;
        }
      });
      setFormValues(defaults);
    } catch {
      toast.error('Failed to load tool');
      navigate('/tools');
    }
  };

  const handleExecute = async () => {
    if (!tool) return;
    
    // Validate required fields
    const missing = tool.arguments
      ?.filter((a: ToolArg) => a.is_required && !formValues[a.name])
      .map((a: ToolArg) => a.label);
    
    if (missing?.length > 0) {
      toast.error(`Missing required fields: ${missing.join(', ')}`);
      return;
    }

    setExecuting(true);
    setOutput([]);
    setStatus('running');

    try {
      const res = await api.post('/api/executions/run', {
        tool_id: tool.id,
        arguments: formValues,
      });
      
      setExecutionId(res.data.id);
      setCommand(res.data.command);
      addExecution(res.data.id);
      
      // Connect WebSocket for live output
      connectWebSocket(res.data.id);
      
      toast.success('Execution started!');
    } catch (err: any) {
      setExecuting(false);
      setStatus('failed');
      const detail = err.response?.data?.detail;
      if (typeof detail === 'object') {
        toast.error(detail.message || 'Execution failed');
        setOutput([`Error: ${detail.message}`, ...(detail.errors || [])]);
      } else {
        toast.error(detail || 'Execution failed');
      }
    }
  };

  const connectWebSocket = (execId: string) => {
    if (!accessToken) return;
    const url = getWSUrl(execId, accessToken);
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === 'output') {
        setOutput(prev => [...prev, msg.data]);
      } else if (msg.type === 'status') {
        setStatus(msg.status);
        setExecuting(false);
        removeExecution(execId);
        if (msg.status === 'completed') {
          toast.success('Execution completed!');
        } else if (msg.status === 'failed') {
          toast.error(`Execution failed (exit code: ${msg.exit_code})`);
        }
      }
    };

    ws.onerror = () => {
      setOutput(prev => [...prev, '[WebSocket connection error]']);
    };

    ws.onclose = () => {
      if (status === 'running') {
        setStatus('disconnected');
      }
    };
  };

  const handleStop = async () => {
    if (!executionId) return;
    try {
      await api.post('/api/executions/stop', { execution_id: executionId });
      setStatus('stopped');
      setExecuting(false);
      removeExecution(executionId);
      toast.success('Process stopped');
    } catch {
      toast.error('Failed to stop process');
    }
  };

  const copyCommand = () => {
    navigator.clipboard.writeText(command);
    toast.success('Command copied!');
  };

  const renderField = (arg: ToolArg) => {
    const value = formValues[arg.name] ?? '';
    const onChange = (val: any) => setFormValues({ ...formValues, [arg.name]: val });

    const widthClass = arg.width === 'half' ? 'md:col-span-1' : arg.width === 'third' ? 'md:col-span-1' : 'md:col-span-2';

    const fieldContent = () => {
      switch (arg.field_type) {
        case 'textarea':
          return <textarea value={value} onChange={e => onChange(e.target.value)} placeholder={arg.placeholder} rows={3} className="input-field resize-none text-sm" />;
        
        case 'number':
        case 'port':
          return <input type="number" value={value} onChange={e => onChange(e.target.value)} placeholder={arg.placeholder || (arg.field_type === 'port' ? '1-65535' : '')} className="input-field text-sm" />;
        
        case 'select':
          return (
            <select value={value} onChange={e => onChange(e.target.value)} className="input-field text-sm">
              <option value="">Select...</option>
              {arg.options?.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
            </select>
          );
        
        case 'checkbox':
        case 'toggle':
          return (
            <label className="flex items-center gap-2 cursor-pointer mt-2">
              <div className={`relative w-10 h-5 rounded-full transition-colors ${value ? 'bg-vigil-primary' : 'bg-vigil-border'}`}>
                <div className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform ${value ? 'translate-x-5' : 'translate-x-0.5'}`} />
              </div>
              <span className="text-sm text-vigil-text">{value ? 'Enabled' : 'Disabled'}</span>
            </label>
          );
        
        case 'file':
        case 'wordlist':
        case 'folder':
          return <input type="text" value={value} onChange={e => onChange(e.target.value)} placeholder={arg.placeholder || `Enter ${arg.field_type} path...`} className="input-field text-sm font-mono" />;
        
        case 'password':
          return (
            <div className="relative">
              <input type="password" value={value} onChange={e => onChange(e.target.value)} placeholder={arg.placeholder || '••••••'} className="input-field text-sm" />
            </div>
          );
        
        case 'ip':
        case 'ip_range':
          return <input type="text" value={value} onChange={e => onChange(e.target.value)} placeholder={arg.placeholder || '192.168.1.1'} className="input-field text-sm font-mono" />;
        
        case 'domain':
          return <input type="text" value={value} onChange={e => onChange(e.target.value)} placeholder={arg.placeholder || 'example.com'} className="input-field text-sm font-mono" />;
        
        case 'port_range':
          return <input type="text" value={value} onChange={e => onChange(e.target.value)} placeholder={arg.placeholder || '1-1000'} className="input-field text-sm font-mono" />;
        
        case 'url':
          return <input type="url" value={value} onChange={e => onChange(e.target.value)} placeholder={arg.placeholder || 'https://'} className="input-field text-sm" />;
        
        default:
          return <input type="text" value={value} onChange={e => onChange(e.target.value)} placeholder={arg.placeholder} className="input-field text-sm" />;
      }
    };

    return (
      <div key={arg.name} className={widthClass}>
        <label className="text-sm font-medium text-vigil-text-muted block mb-1.5">
          {arg.label}
          {arg.is_required && <span className="text-vigil-danger ml-1">*</span>}
          {arg.flag && <span className="text-vigil-text-dim font-mono ml-2 text-xs">{arg.flag}</span>}
        </label>
        {fieldContent()}
        {arg.tooltip && <p className="text-[11px] text-vigil-text-dim mt-1">{arg.tooltip}</p>}
        {arg.example && <p className="text-[11px] text-vigil-text-dim mt-0.5">Example: {arg.example}</p>}
      </div>
    );
  };

  if (!tool) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="w-8 h-8 border-2 border-vigil-primary/30 border-t-vigil-primary rounded-full animate-spin" />
      </div>
    );
  }

  const basicArgs = tool.arguments?.filter((a: ToolArg) => !a.is_advanced) || [];
  const advancedArgs = tool.arguments?.filter((a: ToolArg) => a.is_advanced) || [];

  return (
    <div className="space-y-6">
      {/* Tool Header */}
      <div className="glass-panel p-5 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-vigil-primary to-vigil-accent flex items-center justify-center shadow-glow-sm">
            <Shield size={24} className="text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-vigil-text">{tool.name}</h1>
            <p className="text-sm text-vigil-text-muted">{tool.description || 'No description'}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {status === 'running' ? (
            <button onClick={handleStop} className="btn-danger flex items-center gap-2">
              <Square size={14} /> Stop
            </button>
          ) : (
            <button onClick={handleExecute} disabled={executing} className="btn-primary flex items-center gap-2">
              {executing ? <Loader size={14} className="animate-spin" /> : <Play size={14} />}
              Execute
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Form Panel */}
        <div className="lg:col-span-2 space-y-4">
          <div className="glass-panel p-5">
            <h3 className="text-sm font-semibold text-vigil-text-muted uppercase tracking-wider mb-4">
              Configuration
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {basicArgs.map(renderField)}
            </div>

            {advancedArgs.length > 0 && (
              <>
                <button
                  onClick={() => setShowAdvanced(!showAdvanced)}
                  className="flex items-center gap-2 mt-4 text-sm text-vigil-primary hover:text-vigil-primary-light transition-colors"
                >
                  {showAdvanced ? <EyeOff size={14} /> : <Eye size={14} />}
                  {showAdvanced ? 'Hide' : 'Show'} Advanced Options ({advancedArgs.length})
                </button>
                {showAdvanced && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 pt-4 border-t border-vigil-border"
                  >
                    {advancedArgs.map(renderField)}
                  </motion.div>
                )}
              </>
            )}
          </div>
        </div>

        {/* Terminal Output */}
        <div className="lg:col-span-3">
          <div className="glass-panel overflow-hidden h-[600px] flex flex-col">
            {/* Terminal Header */}
            <div className="flex items-center justify-between px-4 py-2.5 bg-vigil-surface border-b border-vigil-border">
              <div className="flex items-center gap-2">
                <div className="flex gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-vigil-danger/70" />
                  <div className="w-2.5 h-2.5 rounded-full bg-vigil-warning/70" />
                  <div className="w-2.5 h-2.5 rounded-full bg-vigil-success/70" />
                </div>
                <span className="text-xs font-mono text-vigil-text-dim ml-2">
                  {tool.name} — Output
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className={`badge text-[10px] ${
                  status === 'running' ? 'badge-info' :
                  status === 'completed' ? 'badge-success' :
                  status === 'failed' ? 'badge-danger' :
                  status === 'stopped' ? 'badge-warning' : ''
                }`}>
                  {status}
                </span>
                {command && (
                  <button onClick={copyCommand} className="p-1 rounded hover:bg-vigil-hover text-vigil-text-dim" title="Copy command">
                    <Copy size={12} />
                  </button>
                )}
              </div>
            </div>

            {/* Command Display */}
            {command && (
              <div className="px-4 py-2 bg-vigil-bg/80 border-b border-vigil-border/50 font-mono text-xs">
                <span className="text-vigil-success">$ </span>
                <span className="text-vigil-text">{command}</span>
              </div>
            )}

            {/* Output */}
            <div ref={outputRef} className="flex-1 overflow-auto p-4 font-mono text-sm bg-vigil-bg">
              {output.length === 0 ? (
                <div className="text-vigil-text-dim">
                  <p>Waiting for execution...</p>
                  <p className="mt-2 text-vigil-text-dim">
                    <span className="text-vigil-primary">vigil</span>@<span className="text-vigil-secondary">{tool.name}</span>
                    <span className="text-vigil-text-muted">:~$ </span>
                    <span className="animate-pulse">▊</span>
                  </p>
                </div>
              ) : (
                output.map((line, i) => (
                  <div key={i} className="text-vigil-text whitespace-pre-wrap leading-relaxed">
                    {line}
                  </div>
                ))
              )}
              {status === 'running' && (
                <div className="text-vigil-primary animate-pulse mt-1">▊</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
