import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Brain, Send, Sparkles, AlertTriangle, Wrench, FileCode, Terminal,
  Lightbulb, GitBranch, Target, Shield, Zap, MessageSquare,
  ChevronRight, Rocket, BookOpen, Search,
} from 'lucide-react';
import { api } from '../utils/api';
import toast from 'react-hot-toast';

interface Message {
  id: string;
  role: 'user' | 'agent';
  content: string;
  type?: string;
  data?: any;
}

const agentModes = [
  { id: 'chat', icon: Sparkles, label: 'AI Chat', placeholder: 'Ask me anything about security, tools, hacking...', description: 'Chat with Gemini AI about anything' },
  { id: 'goal', icon: Target, label: 'Understand Goal', placeholder: 'Describe what you want to achieve...', description: 'AI understands your goal and recommends tools/workflows' },
  { id: 'workflow', icon: GitBranch, label: 'Generate Workflow', placeholder: 'Describe the pipeline you need...', description: 'Auto-generate multi-tool workflows with Gemini' },
  { id: 'recommend', icon: Lightbulb, label: 'Recommend Tools', placeholder: 'What task do you need to accomplish?', description: 'Get tool recommendations for any task' },
  { id: 'explain', icon: BookOpen, label: 'Explain Output', placeholder: 'Paste tool output here...', description: 'Explain tool output with Gemini AI' },
  { id: 'error', icon: AlertTriangle, label: 'Fix Error', placeholder: 'Paste error message here...', description: 'Analyze errors and get fixes with Gemini AI' },
  { id: 'analyze', icon: Search, label: 'Analyze Tool', placeholder: 'Enter tool executable name (e.g., nmap)...', description: 'Auto-analyze any CLI tool and generate GUI config' },
];

export default function AIAssistantPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'agent',
      content: "I'm the VIGIL LABS AI Agent. I can understand your goals, recommend tools, generate workflows, explain outputs, fix errors, and auto-configure tools. Choose a mode below or just tell me what you need.",
    },
  ]);
  const [input, setInput] = useState('');
  const [activeMode, setActiveMode] = useState<string>('chat');
  const [loading, setLoading] = useState(false);
  const [toolName, setToolName] = useState('');

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMsg: Message = { id: crypto.randomUUID(), role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    const currentInput = input;
    setInput('');
    setLoading(true);

    try {
      let response: any;
      let formattedContent = '';

      switch (activeMode) {
        case 'chat':
          response = await api.post('/api/system/ai/chat', { message: currentInput });
          formattedContent = response.data.response || 'No response.';
          break;
        case 'goal':
          response = await api.post('/api/system/ai/chat', {
            message: `My goal: ${currentInput}\n\nAs a security expert, tell me: which tools to use, a recommended approach, and safety notes.`,
          });
          formattedContent = response.data.response || 'No response.';
          break;
        case 'workflow':
          response = await api.post('/api/system/ai/generate-workflow-gemini', { goal: currentInput, available_tools: [] });
          formattedContent = response.data.response || 'No response.';
          break;
        case 'recommend':
          response = await api.post('/api/system/ai/chat', {
            message: `Recommend the best security tools for this task: ${currentInput}. List each tool with a one-line reason.`,
          });
          formattedContent = response.data.response || 'No response.';
          break;
        case 'explain':
          response = await api.post('/api/system/ai/analyze-output-gemini', { output: currentInput, tool_name: toolName || 'unknown', command: '' });
          formattedContent = response.data.response || 'No response.';
          break;
        case 'error':
          response = await api.post('/api/system/ai/analyze-error-gemini', { error: currentInput, tool_name: toolName || 'unknown', command: '' });
          formattedContent = response.data.response || 'No response.';
          break;
        case 'analyze':
          response = await api.post('/api/system/ai/auto-analyze-tool', { executable: currentInput.trim() });
          formattedContent = formatAnalyzeResponse(response.data);
          break;
        default:
          response = await api.post('/api/system/ai/chat', { message: currentInput });
          formattedContent = response.data.response || 'No response.';
      }

      const agentMsg: Message = { id: crypto.randomUUID(), role: 'agent', content: formattedContent, type: activeMode, data: response.data };
      setMessages(prev => [...prev, agentMsg]);
    } catch (err: any) {
      const detail = err?.response?.data?.error?.message || err?.response?.data?.detail || err?.message || 'request failed';
      toast.error(`AI error: ${detail}`);
      setMessages(prev => [...prev, { id: crypto.randomUUID(), role: 'agent', content: `Sorry, I hit an error: ${detail}\n\nCheck that GEMINI_API_KEY is set in backend/.env and AI_MODEL=gemini.` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col max-w-5xl mx-auto">
      {/* Mode Selector */}
      <div className="grid grid-cols-4 md:grid-cols-7 gap-2 mb-4">
        {agentModes.map(mode => (
          <button
            key={mode.id}
            onClick={() => setActiveMode(mode.id)}
            className={`glass-panel-hover p-2.5 text-center transition-all ${
              activeMode === mode.id ? 'border-vigil-primary bg-vigil-primary/5 shadow-glow-sm' : ''
            }`}
          >
            <mode.icon size={16} className={`mx-auto ${activeMode === mode.id ? 'text-vigil-primary' : 'text-vigil-text-dim'}`} />
            <p className="text-[10px] font-medium text-vigil-text mt-1.5 leading-tight">{mode.label}</p>
          </button>
        ))}
      </div>

      {/* Active Mode Description */}
      <div className="glass-panel px-4 py-2 mb-4 flex items-center gap-2">
        <Zap size={14} className="text-vigil-neon shrink-0" />
        <p className="text-xs text-vigil-text-muted">
          <span className="text-vigil-primary font-medium">{agentModes.find(m => m.id === activeMode)?.label}:</span>{' '}
          {agentModes.find(m => m.id === activeMode)?.description}
        </p>
      </div>

      {/* Chat Area */}
      <div className="flex-1 glass-panel overflow-hidden flex flex-col min-h-0">
        <div className="flex-1 overflow-auto p-4 space-y-4">
          {messages.map(msg => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[85%] rounded-xl px-4 py-3 ${
                msg.role === 'user'
                  ? 'bg-vigil-primary/10 border border-vigil-primary/20'
                  : 'bg-vigil-surface border border-vigil-border'
              }`}>
                {msg.role === 'agent' && (
                  <div className="flex items-center gap-1.5 mb-2">
                    <Brain size={12} className="text-vigil-neon" />
                    <span className="text-[10px] text-vigil-neon font-semibold tracking-wider uppercase">AI Agent</span>
                  </div>
                )}
                <div className="text-sm whitespace-pre-wrap leading-relaxed text-vigil-text">{msg.content}</div>
              </div>
            </motion.div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-vigil-surface border border-vigil-border rounded-xl px-4 py-3">
                <div className="flex items-center gap-2">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 rounded-full bg-vigil-neon animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 rounded-full bg-vigil-neon animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 rounded-full bg-vigil-neon animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                  <span className="text-xs text-vigil-text-dim">Thinking...</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-vigil-border">
          {/* Optional tool name for explain/error modes */}
          {(activeMode === 'explain' || activeMode === 'error') && (
            <div className="mb-2">
              <input
                type="text"
                value={toolName}
                onChange={e => setToolName(e.target.value)}
                placeholder="Tool name (optional, e.g., nmap)"
                className="input-field text-xs py-1.5"
              />
            </div>
          )}
          <div className="flex items-center gap-2">
            <div className="flex-1 relative">
              <input
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSend()}
                placeholder={agentModes.find(m => m.id === activeMode)?.placeholder || 'Ask the AI Agent...'}
                className="input-field pr-20"
              />
              <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[9px] text-vigil-neon bg-vigil-neon/10 px-1.5 py-0.5 rounded font-mono">
                {activeMode}
              </span>
            </div>
            <button
              onClick={handleSend}
              disabled={!input.trim() || loading}
              className="btn-primary p-2.5 shadow-glow-sm"
            >
              <Send size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── RESPONSE FORMATTERS ────────────────────────────────────────────────────

function formatGoalResponse(data: any): string {
  let text = '';
  if (data.recommendations?.length > 0) {
    text += '🎯 I understand your goal. Here\'s my analysis:\n\n';
    for (const rec of data.recommendations) {
      text += `▸ ${rec.description}\n`;
      text += `  Tools: ${rec.recommended_tools?.join(', ') || 'N/A'}\n`;
      if (rec.suggested_workflow) text += `  Workflow: ${rec.suggested_workflow}\n`;
      text += '\n';
    }
  }
  if (data.suggested_workflows?.length > 0) {
    text += '⚡ Suggested Workflows:\n';
    for (const wf of data.suggested_workflows) {
      text += `  • ${wf.name}: ${wf.tools?.join(' → ')}\n`;
    }
    text += '\n';
  }
  if (data.safety_notes?.length > 0) {
    text += '🛡️ Safety Notes:\n';
    for (const note of data.safety_notes) text += `  • ${note}\n`;
    text += '\n';
  }
  if (data.next_steps?.length > 0) {
    text += '➡️ Next Steps:\n';
    for (const step of data.next_steps) text += `  • ${step}\n`;
  }
  return text || 'I need more context to understand your goal. Could you be more specific?';
}

function formatWorkflowResponse(data: any): string {
  let text = `⚡ Generated Workflow: "${data.name || 'Custom'}"\n\n`;
  if (data.description) text += `${data.description}\n\n`;
  if (data.steps?.length > 0) {
    text += 'Pipeline Steps:\n';
    data.steps.forEach((step: any, i: number) => {
      text += `  ${i + 1}. ${step.tool_name} — ${step.purpose || ''}\n`;
    });
    text += `\nTotal tools: ${data.total_tools || data.steps.length}`;
    if (data.estimated_time) text += ` | Est. time: ${data.estimated_time}`;
    if (data.requires_confirmation) text += '\n\n⚠️ This workflow requires your confirmation before execution.';
  } else {
    text += 'No matching tools found for this workflow. Try installing tools from the Tool Store.';
  }
  return text;
}

function formatRecommendResponse(data: any): string {
  if (!data || data.length === 0) return 'No tool recommendations found for this task. Try a different description.';
  let text = '💡 Recommended Tools:\n\n';
  for (const tool of data.slice(0, 6)) {
    text += `▸ ${tool.name} (${tool.category})\n`;
    text += `  ${tool.description}\n`;
    text += `  Risk: ${tool.risk_level} | Install: ${tool.install_method}\n\n`;
  }
  return text;
}

function formatExplainResponse(data: any): string {
  let text = `📊 Output Analysis for ${data.tool}:\n\n`;
  text += `Summary: ${data.summary}\n\n`;
  if (data.key_findings?.length > 0) {
    text += 'Key Findings:\n';
    for (const f of data.key_findings.slice(0, 5)) text += `  • ${f}\n`;
    text += '\n';
  }
  if (data.risk_items?.length > 0) {
    text += '⚠️ Risk Items:\n';
    for (const r of data.risk_items) text += `  • ${r}\n`;
    text += '\n';
  }
  if (data.recommendations?.length > 0) {
    text += '💡 Recommendations:\n';
    for (const r of data.recommendations) text += `  • ${r}\n`;
  }
  return text;
}

function formatErrorResponse(data: any): string {
  let text = `🔧 Error Analysis (${data.error_type}):\n`;
  text += `Severity: ${data.severity}\n\n`;
  if (data.issues?.length > 0) {
    text += 'Issues:\n';
    for (const i of data.issues) text += `  ❌ ${i}\n`;
    text += '\n';
  }
  if (data.auto_fixes?.length > 0) {
    text += '⚡ Auto-Fix Options:\n';
    for (const f of data.auto_fixes) {
      text += `  ✅ ${f.description}`;
      if (f.command) text += ` → \`${f.command}\``;
      text += '\n';
    }
    text += '\n';
  }
  if (data.manual_fixes?.length > 0) {
    text += '🔨 Manual Fixes:\n';
    for (const f of data.manual_fixes) text += `  • ${f}\n`;
  }
  return text;
}

function formatAnalyzeResponse(data: any): string {
  if (!data.success) {
    let text = `❌ Could not analyze tool "${data.executable}"\n\n`;
    if (data.error) text += `Error: ${data.error}\n\n`;
    if (data.suggestions) {
      text += 'Suggestions:\n';
      for (const s of data.suggestions) text += `  • ${s}\n`;
    }
    return text;
  }
  let text = `✅ Successfully analyzed "${data.executable}"!\n\n`;
  if (data.description) text += `Description: ${data.description}\n\n`;
  text += `Command template: ${data.command_template}\n`;
  text += `Arguments found: ${data.arguments?.length || 0}\n\n`;
  if (data.arguments?.length > 0) {
    text += 'Detected Arguments:\n';
    for (const arg of data.arguments.slice(0, 10)) {
      text += `  • ${arg.label} (${arg.field_type}) ${arg.flag || ''}\n`;
      if (arg.description) text += `    ${arg.description}\n`;
    }
    if (data.arguments.length > 10) text += `  ... and ${data.arguments.length - 10} more\n`;
    text += '\n💡 You can use these to create a GUI form in the Tool Builder!';
  }
  return text;
}
