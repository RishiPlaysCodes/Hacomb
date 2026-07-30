import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Save, Plus, Trash2, ChevronDown, ChevronUp, GripVertical,
  Terminal, Shield, Tag, Cpu, FileCode, Settings, AlertTriangle,
  Eye, Code, TestTube,
} from 'lucide-react';
import { api } from '../utils/api';
import toast from 'react-hot-toast';

const FIELD_TYPES = [
  { value: 'text', label: 'Text Input' },
  { value: 'textarea', label: 'Text Area' },
  { value: 'number', label: 'Number' },
  { value: 'select', label: 'Dropdown Select' },
  { value: 'checkbox', label: 'Checkbox' },
  { value: 'toggle', label: 'Toggle Switch' },
  { value: 'file', label: 'File Picker' },
  { value: 'folder', label: 'Folder Picker' },
  { value: 'ip', label: 'IP Address' },
  { value: 'domain', label: 'Domain/Hostname' },
  { value: 'port', label: 'Port Number' },
  { value: 'port_range', label: 'Port Range' },
  { value: 'interface', label: 'Network Interface' },
  { value: 'password', label: 'Password/Secret' },
  { value: 'url', label: 'URL' },
  { value: 'wordlist', label: 'Wordlist File' },
  { value: 'payload', label: 'Payload' },
  { value: 'ip_range', label: 'IP Range/CIDR' },
];

const RISK_LEVELS = ['low', 'medium', 'high', 'critical'];

const defaultArg = {
  name: '', label: '', description: '', field_type: 'text', flag: '',
  placeholder: '', default_value: '', tooltip: '', example: '',
  is_required: false, validation_regex: '', options: [],
  order: 0, group: '', width: 'full', is_advanced: false, depends_on: '',
};

export default function ToolBuilderPage() {
  const navigate = useNavigate();
  const { toolId } = useParams();
  const [isEditing, setIsEditing] = useState(false);
  const [activeSection, setActiveSection] = useState('basic');
  const [saving, setSaving] = useState(false);
  const [categories, setCategories] = useState<any[]>([]);
  
  const [form, setForm] = useState({
    name: '', description: '', category_id: '', executable_path: '',
    command_template: '{executable} {args}',
    supports_linux: true, supports_windows: false, supports_macos: false,
    icon: '', tags: [] as string[], notes: '', risk_level: 'low',
    version: '', author: '', output_format: 'text',
    report_path: '', execution_timeout: 300, working_directory: '',
    run_as_root: false, environment_variables: {} as Record<string, string>,
    dependencies: [] as string[],
    pre_execution_checks: [] as any[], post_execution_actions: [] as any[],
    arguments: [] as any[],
  });

  const [newTag, setNewTag] = useState('');
  const [newDep, setNewDep] = useState('');
  const [newEnvKey, setNewEnvKey] = useState('');
  const [newEnvVal, setNewEnvVal] = useState('');
  const [analyzing, setAnalyzing] = useState(false);

  // One-click: run `<executable> --help` and auto-generate the GUI form
  const autoAnalyze = async () => {
    if (!form.executable_path) {
      toast.error('Enter the executable path/command first');
      return;
    }
    setAnalyzing(true);
    try {
      const res = await api.post('/api/system/ai/auto-analyze-tool', {
        executable: form.executable_path,
      });
      if (!res.data.success) {
        toast.error(res.data.error || 'Could not read tool help output');
        return;
      }
      const detected = (res.data.arguments || []).map((a: any, i: number) => ({
        ...defaultArg,
        ...a,
        order: i,
      }));
      setForm(prev => ({
        ...prev,
        description: prev.description || res.data.description || '',
        command_template: res.data.command_template || prev.command_template,
        arguments: detected.length ? detected : prev.arguments,
      }));
      toast.success(`Detected ${detected.length} argument(s)! Review and save.`);
      setActiveSection('arguments');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Auto-analyze failed');
    } finally {
      setAnalyzing(false);
    }
  };

  useEffect(() => {
    loadCategories();
    if (toolId) {
      loadTool(toolId);
    }
  }, [toolId]);

  const loadCategories = async () => {
    try {
      const res = await api.get('/api/tools/categories/all');
      setCategories(res.data);
    } catch {}
  };

  const loadTool = async (id: string) => {
    try {
      const res = await api.get(`/api/tools/${id}`);
      setForm(res.data);
      setIsEditing(true);
    } catch {
      toast.error('Failed to load tool');
    }
  };

  const handleSave = async () => {
    if (!form.name || !form.executable_path || !form.command_template) {
      toast.error('Please fill in required fields (Name, Executable, Command Template)');
      return;
    }
    setSaving(true);
    try {
      if (isEditing && toolId) {
        await api.put(`/api/tools/${toolId}`, form);
        toast.success('Tool updated successfully!');
      } else {
        await api.post('/api/tools/', form);
        toast.success('Tool created successfully!');
      }
      navigate('/tools');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to save tool');
    } finally {
      setSaving(false);
    }
  };

  const addArgument = () => {
    setForm({
      ...form,
      arguments: [...form.arguments, { ...defaultArg, order: form.arguments.length }],
    });
  };

  const removeArgument = (index: number) => {
    setForm({ ...form, arguments: form.arguments.filter((_, i) => i !== index) });
  };

  const updateArgument = (index: number, field: string, value: any) => {
    const args = [...form.arguments];
    args[index] = { ...args[index], [field]: value };
    if (field === 'label' && !args[index].name) {
      args[index].name = value.toLowerCase().replace(/[^a-z0-9]/g, '_');
    }
    setForm({ ...form, arguments: args });
  };

  const sections = [
    { id: 'basic', label: 'Basic Info', icon: Shield },
    { id: 'execution', label: 'Execution', icon: Terminal },
    { id: 'arguments', label: 'Arguments', icon: Code },
    { id: 'advanced', label: 'Advanced', icon: Settings },
  ];

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-vigil-text">
            {isEditing ? 'Edit Tool' : 'Custom Tool Builder'}
          </h1>
          <p className="text-sm text-vigil-text-muted">
            {isEditing ? 'Update tool configuration' : 'Register any CLI tool with a visual interface'}
          </p>
        </div>
        <button onClick={handleSave} disabled={saving} className="btn-primary flex items-center gap-2">
          {saving ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Save size={16} />}
          {isEditing ? 'Update Tool' : 'Save Tool'}
        </button>
      </div>

      {/* Section Tabs */}
      <div className="glass-panel p-1 flex gap-1">
        {sections.map(s => (
          <button
            key={s.id}
            onClick={() => setActiveSection(s.id)}
            className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
              activeSection === s.id
                ? 'bg-vigil-primary/10 text-vigil-primary border border-vigil-primary/20'
                : 'text-vigil-text-muted hover:text-vigil-text hover:bg-vigil-hover'
            }`}
          >
            <s.icon size={16} />
            {s.label}
          </button>
        ))}
      </div>

      {/* Section Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeSection}
          initial={{ opacity: 0, x: 10 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -10 }}
          className="glass-panel p-6"
        >
          {/* BASIC INFO */}
          {activeSection === 'basic' && (
            <div className="space-y-5">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-vigil-text-muted block mb-1.5">
                    Tool Name <span className="text-vigil-danger">*</span>
                  </label>
                  <input
                    type="text"
                    value={form.name}
                    onChange={e => setForm({ ...form, name: e.target.value })}
                    placeholder="e.g., Nmap, Hydra, Custom Script"
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-vigil-text-muted block mb-1.5">Category</label>
                  <select
                    value={form.category_id}
                    onChange={e => setForm({ ...form, category_id: e.target.value })}
                    className="input-field"
                  >
                    <option value="">Select category</option>
                    {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-vigil-text-muted block mb-1.5">Description</label>
                <textarea
                  value={form.description}
                  onChange={e => setForm({ ...form, description: e.target.value })}
                  placeholder="What does this tool do?"
                  rows={3}
                  className="input-field resize-none"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-vigil-text-muted block mb-1.5">Risk Level</label>
                  <select
                    value={form.risk_level}
                    onChange={e => setForm({ ...form, risk_level: e.target.value })}
                    className="input-field"
                  >
                    {RISK_LEVELS.map(r => <option key={r} value={r}>{r.charAt(0).toUpperCase() + r.slice(1)}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium text-vigil-text-muted block mb-1.5">Version</label>
                  <input
                    type="text"
                    value={form.version}
                    onChange={e => setForm({ ...form, version: e.target.value })}
                    placeholder="e.g., 7.94"
                    className="input-field"
                  />
                </div>
              </div>

              {/* OS Support */}
              <div>
                <label className="text-sm font-medium text-vigil-text-muted block mb-2">Platform Support</label>
                <div className="flex gap-4">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={form.supports_linux}
                      onChange={e => setForm({ ...form, supports_linux: e.target.checked })}
                      className="w-4 h-4 rounded border-vigil-border bg-vigil-bg text-vigil-primary focus:ring-vigil-primary"
                    />
                    <span className="text-sm text-vigil-text">Linux / Kali</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={form.supports_windows}
                      onChange={e => setForm({ ...form, supports_windows: e.target.checked })}
                      className="w-4 h-4 rounded border-vigil-border bg-vigil-bg text-vigil-primary focus:ring-vigil-primary"
                    />
                    <span className="text-sm text-vigil-text">Windows</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={form.supports_macos}
                      onChange={e => setForm({ ...form, supports_macos: e.target.checked })}
                      className="w-4 h-4 rounded border-vigil-border bg-vigil-bg text-vigil-primary focus:ring-vigil-primary"
                    />
                    <span className="text-sm text-vigil-text">macOS</span>
                  </label>
                </div>
                <p className="text-xs text-vigil-text-dim mt-1.5">
                  Tip: Android (Termux) uses Linux support. Mark only the OSes where this tool actually runs so users see accurate "not supported" info.
                </p>
              </div>

              {/* Tags */}
              <div>
                <label className="text-sm font-medium text-vigil-text-muted block mb-1.5">Tags</label>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={newTag}
                    onChange={e => setNewTag(e.target.value)}
                    onKeyDown={e => {
                      if (e.key === 'Enter' && newTag.trim()) {
                        setForm({ ...form, tags: [...form.tags, newTag.trim()] });
                        setNewTag('');
                      }
                    }}
                    placeholder="Add tag and press Enter"
                    className="input-field"
                  />
                </div>
                <div className="flex flex-wrap gap-2 mt-2">
                  {form.tags.map((tag, i) => (
                    <span key={i} className="badge badge-info flex items-center gap-1">
                      {tag}
                      <button onClick={() => setForm({ ...form, tags: form.tags.filter((_, idx) => idx !== i) })}>
                        <Trash2 size={10} />
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* EXECUTION */}
          {activeSection === 'execution' && (
            <div className="space-y-5">
              <div>
                <label className="text-sm font-medium text-vigil-text-muted block mb-1.5">
                  Executable Path <span className="text-vigil-danger">*</span>
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={form.executable_path}
                    onChange={e => setForm({ ...form, executable_path: e.target.value })}
                    placeholder="e.g., nmap, /usr/bin/python3, ./my_script.sh"
                    className="input-field font-mono flex-1"
                  />
                  <button
                    type="button"
                    onClick={autoAnalyze}
                    disabled={analyzing}
                    className="btn-secondary flex items-center gap-2 text-sm whitespace-nowrap shrink-0"
                    title="Run --help and auto-generate the form fields"
                  >
                    {analyzing
                      ? <div className="w-4 h-4 border-2 border-vigil-primary/30 border-t-vigil-primary rounded-full animate-spin" />
                      : <TestTube size={14} />}
                    Auto-detect
                  </button>
                </div>
                <p className="text-xs text-vigil-text-dim mt-1">
                  Full path or command name if in PATH. Click <span className="text-vigil-primary">Auto-detect</span> to read the tool's <code>--help</code> and build the form for you.
                </p>
              </div>

              <div>
                <label className="text-sm font-medium text-vigil-text-muted block mb-1.5">
                  Command Template <span className="text-vigil-danger">*</span>
                </label>
                <input
                  type="text"
                  value={form.command_template}
                  onChange={e => setForm({ ...form, command_template: e.target.value })}
                  placeholder="{executable} {args}"
                  className="input-field font-mono"
                />
                <p className="text-xs text-vigil-text-dim mt-1">
                  Use {'{executable}'} for tool path and {'{args}'} for arguments. Or use {'{{arg_name}}'} for specific arg placement.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-vigil-text-muted block mb-1.5">Timeout (seconds)</label>
                  <input
                    type="number"
                    value={form.execution_timeout}
                    onChange={e => setForm({ ...form, execution_timeout: parseInt(e.target.value) || 300 })}
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-vigil-text-muted block mb-1.5">Output Format</label>
                  <select
                    value={form.output_format}
                    onChange={e => setForm({ ...form, output_format: e.target.value })}
                    className="input-field"
                  >
                    <option value="text">Plain Text</option>
                    <option value="json">JSON</option>
                    <option value="xml">XML</option>
                    <option value="html">HTML</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-vigil-text-muted block mb-1.5">Working Directory</label>
                <input
                  type="text"
                  value={form.working_directory}
                  onChange={e => setForm({ ...form, working_directory: e.target.value })}
                  placeholder="Leave empty for default"
                  className="input-field"
                />
              </div>

              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.run_as_root}
                  onChange={e => setForm({ ...form, run_as_root: e.target.checked })}
                  className="w-4 h-4 rounded border-vigil-border bg-vigil-bg text-vigil-primary"
                />
                <span className="text-sm text-vigil-text">Requires root/admin privileges</span>
              </label>

              {/* Dependencies */}
              <div>
                <label className="text-sm font-medium text-vigil-text-muted block mb-1.5">Dependencies</label>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={newDep}
                    onChange={e => setNewDep(e.target.value)}
                    onKeyDown={e => {
                      if (e.key === 'Enter' && newDep.trim()) {
                        setForm({ ...form, dependencies: [...form.dependencies, newDep.trim()] });
                        setNewDep('');
                      }
                    }}
                    placeholder="Add dependency name"
                    className="input-field"
                  />
                </div>
                <div className="flex flex-wrap gap-2 mt-2">
                  {form.dependencies.map((dep, i) => (
                    <span key={i} className="badge badge-warning flex items-center gap-1">
                      {dep}
                      <button onClick={() => setForm({ ...form, dependencies: form.dependencies.filter((_, idx) => idx !== i) })}>
                        <Trash2 size={10} />
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* ARGUMENTS */}
          {activeSection === 'arguments' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <p className="text-sm text-vigil-text-muted">
                  Define the arguments your tool accepts. These will become GUI form fields.
                </p>
                <button onClick={addArgument} className="btn-primary flex items-center gap-2 text-sm">
                  <Plus size={14} /> Add Argument
                </button>
              </div>

              {form.arguments.length === 0 ? (
                <div className="text-center py-12 bg-vigil-bg/50 rounded-lg border border-dashed border-vigil-border">
                  <Code size={32} className="mx-auto text-vigil-text-dim mb-3" />
                  <p className="text-vigil-text-muted">No arguments defined yet</p>
                  <p className="text-xs text-vigil-text-dim mt-1">Click "Add Argument" to define tool parameters</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {form.arguments.map((arg, index) => (
                    <motion.div
                      key={index}
                      layout
                      className="glass-panel p-4 border-l-2 border-l-vigil-primary/50"
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <GripVertical size={14} className="text-vigil-text-dim cursor-grab" />
                          <span className="text-sm font-medium text-vigil-text">
                            Arg #{index + 1}: {arg.label || 'Unnamed'}
                          </span>
                          {arg.is_required && <span className="text-[10px] text-vigil-danger">Required</span>}
                        </div>
                        <button
                          onClick={() => removeArgument(index)}
                          className="p-1 rounded hover:bg-vigil-danger/10 text-vigil-danger"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                        <div>
                          <label className="text-xs text-vigil-text-dim block mb-1">Label</label>
                          <input
                            type="text"
                            value={arg.label}
                            onChange={e => updateArgument(index, 'label', e.target.value)}
                            placeholder="e.g., Target IP"
                            className="input-field text-sm"
                          />
                        </div>
                        <div>
                          <label className="text-xs text-vigil-text-dim block mb-1">Field Type</label>
                          <select
                            value={arg.field_type}
                            onChange={e => updateArgument(index, 'field_type', e.target.value)}
                            className="input-field text-sm"
                          >
                            {FIELD_TYPES.map(ft => (
                              <option key={ft.value} value={ft.value}>{ft.label}</option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <label className="text-xs text-vigil-text-dim block mb-1">CLI Flag</label>
                          <input
                            type="text"
                            value={arg.flag}
                            onChange={e => updateArgument(index, 'flag', e.target.value)}
                            placeholder="e.g., -p, --port"
                            className="input-field text-sm font-mono"
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-3">
                        <div>
                          <label className="text-xs text-vigil-text-dim block mb-1">Placeholder</label>
                          <input
                            type="text"
                            value={arg.placeholder}
                            onChange={e => updateArgument(index, 'placeholder', e.target.value)}
                            placeholder="Placeholder text"
                            className="input-field text-sm"
                          />
                        </div>
                        <div>
                          <label className="text-xs text-vigil-text-dim block mb-1">Default Value</label>
                          <input
                            type="text"
                            value={arg.default_value}
                            onChange={e => updateArgument(index, 'default_value', e.target.value)}
                            placeholder="Default"
                            className="input-field text-sm"
                          />
                        </div>
                        <div>
                          <label className="text-xs text-vigil-text-dim block mb-1">Width</label>
                          <select
                            value={arg.width}
                            onChange={e => updateArgument(index, 'width', e.target.value)}
                            className="input-field text-sm"
                          >
                            <option value="full">Full Width</option>
                            <option value="half">Half Width</option>
                            <option value="third">Third Width</option>
                          </select>
                        </div>
                      </div>

                      <div className="flex items-center gap-4 mt-3">
                        <label className="flex items-center gap-1.5 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={arg.is_required}
                            onChange={e => updateArgument(index, 'is_required', e.target.checked)}
                            className="w-3.5 h-3.5 rounded border-vigil-border bg-vigil-bg text-vigil-primary"
                          />
                          <span className="text-xs text-vigil-text-muted">Required</span>
                        </label>
                        <label className="flex items-center gap-1.5 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={arg.is_advanced}
                            onChange={e => updateArgument(index, 'is_advanced', e.target.checked)}
                            className="w-3.5 h-3.5 rounded border-vigil-border bg-vigil-bg text-vigil-primary"
                          />
                          <span className="text-xs text-vigil-text-muted">Advanced</span>
                        </label>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* ADVANCED */}
          {activeSection === 'advanced' && (
            <div className="space-y-5">
              <div>
                <label className="text-sm font-medium text-vigil-text-muted block mb-1.5">Notes</label>
                <textarea
                  value={form.notes}
                  onChange={e => setForm({ ...form, notes: e.target.value })}
                  placeholder="Internal notes, usage instructions, warnings..."
                  rows={3}
                  className="input-field resize-none"
                />
              </div>

              <div>
                <label className="text-sm font-medium text-vigil-text-muted block mb-1.5">Report Output Path</label>
                <input
                  type="text"
                  value={form.report_path}
                  onChange={e => setForm({ ...form, report_path: e.target.value })}
                  placeholder="e.g., /reports/{{tool_name}}_{{timestamp}}.txt"
                  className="input-field font-mono"
                />
              </div>

              {/* Environment Variables */}
              <div>
                <label className="text-sm font-medium text-vigil-text-muted block mb-1.5">Environment Variables</label>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={newEnvKey}
                    onChange={e => setNewEnvKey(e.target.value)}
                    placeholder="KEY"
                    className="input-field font-mono"
                  />
                  <span className="text-vigil-text-dim">=</span>
                  <input
                    type="text"
                    value={newEnvVal}
                    onChange={e => setNewEnvVal(e.target.value)}
                    placeholder="value"
                    className="input-field font-mono"
                    onKeyDown={e => {
                      if (e.key === 'Enter' && newEnvKey.trim()) {
                        setForm({
                          ...form,
                          environment_variables: { ...form.environment_variables, [newEnvKey]: newEnvVal },
                        });
                        setNewEnvKey('');
                        setNewEnvVal('');
                      }
                    }}
                  />
                </div>
                <div className="space-y-1 mt-2">
                  {Object.entries(form.environment_variables).map(([key, val]) => (
                    <div key={key} className="flex items-center justify-between px-3 py-1.5 bg-vigil-bg rounded text-xs font-mono">
                      <span><span className="text-vigil-primary">{key}</span>=<span className="text-vigil-secondary">{val}</span></span>
                      <button
                        onClick={() => {
                          const { [key]: _, ...rest } = form.environment_variables;
                          setForm({ ...form, environment_variables: rest });
                        }}
                        className="text-vigil-danger hover:text-vigil-danger/80"
                      >
                        <Trash2 size={12} />
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-vigil-text-muted block mb-1.5">Author</label>
                <input
                  type="text"
                  value={form.author}
                  onChange={e => setForm({ ...form, author: e.target.value })}
                  placeholder="Tool author or your name"
                  className="input-field"
                />
              </div>
            </div>
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
