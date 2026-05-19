import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  GitBranch, Plus, Play, Trash2, Edit, Clock, CheckCircle,
  ArrowRight, Zap, Save, ChevronDown,
} from 'lucide-react';
import { api } from '../utils/api';
import toast from 'react-hot-toast';

interface Workflow {
  id: string;
  name: string;
  description: string;
  steps: WorkflowStep[];
  status: string;
  last_run?: string;
  run_count: number;
  is_favorite: boolean;
  created_at: string;
}

interface WorkflowStep {
  id: string;
  tool_id: string;
  tool_name: string;
  order: number;
  arguments: Record<string, any>;
  pipe_output: boolean;
  condition?: string;
}

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [showBuilder, setShowBuilder] = useState(false);
  const [builderName, setBuilderName] = useState('');
  const [builderDesc, setBuilderDesc] = useState('');
  const [builderSteps, setBuilderSteps] = useState<any[]>([]);
  const [tools, setTools] = useState<any[]>([]);

  useEffect(() => {
    loadWorkflows();
    loadTools();
  }, []);

  const loadWorkflows = async () => {
    try {
      const res = await api.get('/api/workflows/');
      setWorkflows(res.data || []);
    } catch {} finally {
      setLoading(false);
    }
  };

  const loadTools = async () => {
    try {
      const res = await api.get('/api/tools/');
      setTools(res.data || []);
    } catch {}
  };

  const addStep = () => {
    setBuilderSteps([...builderSteps, { tool_id: '', tool_name: '', order: builderSteps.length, arguments: {}, pipe_output: true }]);
  };

  const removeStep = (index: number) => {
    setBuilderSteps(builderSteps.filter((_, i) => i !== index));
  };

  const updateStep = (index: number, field: string, value: any) => {
    const steps = [...builderSteps];
    steps[index] = { ...steps[index], [field]: value };
    if (field === 'tool_id') {
      const tool = tools.find(t => t.id === value);
      if (tool) steps[index].tool_name = tool.name;
    }
    setBuilderSteps(steps);
  };

  const saveWorkflow = async () => {
    if (!builderName || builderSteps.length < 2) {
      toast.error('Workflow needs a name and at least 2 steps');
      return;
    }
    try {
      await api.post('/api/workflows/', {
        name: builderName,
        description: builderDesc,
        steps: builderSteps,
      });
      toast.success('Workflow saved!');
      setShowBuilder(false);
      setBuilderName('');
      setBuilderDesc('');
      setBuilderSteps([]);
      loadWorkflows();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to save workflow');
    }
  };

  const runWorkflow = async (id: string) => {
    try {
      await api.post(`/api/workflows/${id}/run`);
      toast.success('Workflow started!');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to start workflow');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-vigil-text flex items-center gap-2">
            <GitBranch size={22} className="text-vigil-warning" /> Workflows
          </h1>
          <p className="text-sm text-vigil-text-muted">
            Chain multiple tools together into automated pipelines
          </p>
        </div>
        <button
          onClick={() => setShowBuilder(!showBuilder)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={16} /> Create Workflow
        </button>
      </div>

      {/* Workflow Builder */}
      {showBuilder && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="glass-panel p-6"
        >
          <h3 className="text-lg font-semibold text-vigil-text mb-4">New Workflow</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="text-sm font-medium text-vigil-text-muted block mb-1.5">Workflow Name</label>
              <input
                type="text"
                value={builderName}
                onChange={e => setBuilderName(e.target.value)}
                placeholder="e.g., Full Web Recon Pipeline"
                className="input-field"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-vigil-text-muted block mb-1.5">Description</label>
              <input
                type="text"
                value={builderDesc}
                onChange={e => setBuilderDesc(e.target.value)}
                placeholder="What does this workflow do?"
                className="input-field"
              />
            </div>
          </div>

          {/* Steps */}
          <div className="space-y-3 mb-4">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-vigil-text-muted">Pipeline Steps</label>
              <button onClick={addStep} className="text-xs text-vigil-primary hover:text-vigil-primary-light flex items-center gap-1">
                <Plus size={12} /> Add Step
              </button>
            </div>
            
            {builderSteps.length === 0 ? (
              <div className="text-center py-8 bg-vigil-bg/50 rounded-lg border border-dashed border-vigil-border">
                <GitBranch size={24} className="mx-auto text-vigil-text-dim mb-2" />
                <p className="text-sm text-vigil-text-muted">Add steps to build your pipeline</p>
              </div>
            ) : (
              <div className="space-y-2">
                {builderSteps.map((step, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <span className="text-xs text-vigil-text-dim w-6 text-center font-mono">{index + 1}</span>
                    <select
                      value={step.tool_id}
                      onChange={e => updateStep(index, 'tool_id', e.target.value)}
                      className="input-field flex-1 text-sm"
                    >
                      <option value="">Select Tool...</option>
                      {tools.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                    </select>
                    {index < builderSteps.length - 1 && (
                      <ArrowRight size={14} className="text-vigil-primary shrink-0" />
                    )}
                    <label className="flex items-center gap-1.5 shrink-0">
                      <input
                        type="checkbox"
                        checked={step.pipe_output}
                        onChange={e => updateStep(index, 'pipe_output', e.target.checked)}
                        className="w-3.5 h-3.5 rounded border-vigil-border bg-vigil-bg text-vigil-primary"
                      />
                      <span className="text-[10px] text-vigil-text-dim">Pipe</span>
                    </label>
                    <button onClick={() => removeStep(index)} className="p-1 text-vigil-danger hover:bg-vigil-danger/10 rounded">
                      <Trash2 size={14} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="flex items-center gap-2 pt-3 border-t border-vigil-border">
            <button onClick={saveWorkflow} className="btn-primary flex items-center gap-2 text-sm">
              <Save size={14} /> Save Workflow
            </button>
            <button onClick={() => setShowBuilder(false)} className="btn-secondary text-sm">Cancel</button>
          </div>
        </motion.div>
      )}

      {/* Existing Workflows */}
      {loading ? (
        <div className="text-center py-16">
          <div className="w-8 h-8 border-2 border-vigil-primary/30 border-t-vigil-primary rounded-full animate-spin mx-auto" />
        </div>
      ) : workflows.length === 0 && !showBuilder ? (
        <div className="text-center py-20 glass-panel">
          <GitBranch size={48} className="mx-auto text-vigil-text-dim mb-4" />
          <h3 className="text-lg font-medium text-vigil-text">No workflows yet</h3>
          <p className="text-sm text-vigil-text-muted mt-1">
            Create your first workflow to chain tools together
          </p>
          <button onClick={() => setShowBuilder(true)} className="btn-primary mt-4">
            Create Workflow
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {workflows.map((wf, i) => (
            <motion.div
              key={wf.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="glass-panel-hover p-5"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-vigil-text">{wf.name}</h3>
                  <p className="text-xs text-vigil-text-muted mt-0.5">{wf.description}</p>
                </div>
                <div className="flex items-center gap-1">
                  <button onClick={() => runWorkflow(wf.id)} className="p-1.5 rounded hover:bg-vigil-success/10 text-vigil-success" title="Run">
                    <Play size={14} />
                  </button>
                  <button className="p-1.5 rounded hover:bg-vigil-danger/10 text-vigil-danger" title="Delete">
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>

              {/* Steps visualization */}
              <div className="flex items-center gap-1.5 mt-3 overflow-x-auto">
                {wf.steps?.map((step, si) => (
                  <div key={si} className="flex items-center gap-1.5 shrink-0">
                    <span className="px-2 py-1 text-[10px] font-medium bg-vigil-bg border border-vigil-border rounded-md text-vigil-text">
                      {step.tool_name}
                    </span>
                    {si < wf.steps.length - 1 && <ArrowRight size={10} className="text-vigil-primary" />}
                  </div>
                ))}
              </div>

              <div className="flex items-center gap-3 mt-3 pt-3 border-t border-vigil-border/50">
                <span className="text-[10px] text-vigil-text-dim flex items-center gap-1">
                  <Zap size={10} /> {wf.run_count} runs
                </span>
                {wf.last_run && (
                  <span className="text-[10px] text-vigil-text-dim flex items-center gap-1">
                    <Clock size={10} /> {new Date(wf.last_run).toLocaleDateString()}
                  </span>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
