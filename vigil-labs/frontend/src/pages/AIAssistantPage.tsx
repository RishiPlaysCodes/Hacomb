import { useState } from 'react';
import { motion } from 'framer-motion';
import { Brain, Send, Sparkles, AlertTriangle, Wrench, FileCode, Terminal, Lightbulb } from 'lucide-react';
import { api } from '../utils/api';
import toast from 'react-hot-toast';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  type?: string;
  data?: any;
}

const quickActions = [
  { icon: Terminal, label: 'Analyze Help Output', action: 'analyze-help', placeholder: 'Paste the --help output of a tool here...' },
  { icon: AlertTriangle, label: 'Analyze Error', action: 'analyze-error', placeholder: 'Paste the error output here...' },
  { icon: Wrench, label: 'Suggest Configuration', action: 'suggest-config', placeholder: 'Enter tool name to get safe default configs...' },
  { icon: FileCode, label: 'Explain Command', action: 'explain-command', placeholder: 'Enter a command to get an explanation...' },
];

export default function AIAssistantPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hello! I'm the VIGIL LABS AI Assistant. I can help you understand tools, analyze errors, generate configurations, explain commands, and build tool templates. How can I help you today?",
    },
  ]);
  const [input, setInput] = useState('');
  const [activeAction, setActiveAction] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input,
    };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      let response: any;
      const action = activeAction || 'explain-command';

      switch (action) {
        case 'analyze-help':
          response = await api.post('/api/system/ai/analyze-help', {
            help_output: input,
            tool_name: 'unknown',
          });
          break;
        case 'analyze-error':
          response = await api.post('/api/system/ai/analyze-error', {
            error_output: input,
            tool_name: 'unknown',
          });
          break;
        case 'suggest-config':
          response = await api.post('/api/system/ai/suggest-config', {
            tool_name: input,
            context: {},
          });
          break;
        case 'explain-command':
          response = await api.post('/api/system/ai/explain-command', {
            command: input,
          });
          break;
        default:
          response = await api.post('/api/system/ai/explain-command', { command: input });
      }

      const aiMsg: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: formatResponse(action, response.data),
        type: action,
        data: response.data,
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (err) {
      toast.error('AI request failed');
      setMessages(prev => [...prev, {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
      }]);
    } finally {
      setLoading(false);
    }
  };

  const formatResponse = (action: string, data: any): string => {
    switch (action) {
      case 'analyze-help':
        const argCount = data.arguments?.length || 0;
        return `Found ${argCount} arguments in the help output. I can convert these into GUI form fields for your tool builder.\n\nArguments detected:\n${
          data.arguments?.map((a: any) => `• ${a.label} (${a.field_type}) - Flag: ${a.flag || 'none'}`).join('\n') || 'None found'
        }`;
      
      case 'analyze-error':
        return `Error Analysis:\n${
          data.analysis?.map((a: any) => `\n⚠️ ${a.issue}\n   Fix: ${a.fix}\n   Severity: ${a.severity}`).join('\n') || 'No specific issues identified.'
        }`;
      
      case 'suggest-config':
        return `Configuration Suggestions for "${data.tool}":\n\n${
          data.suggestions?.recommendation || 'No specific recommendations.'
        }\n\nSafety Notes:\n${
          data.safety_notes?.map((n: string) => `• ${n}`).join('\n') || ''
        }`;
      
      case 'explain-command':
        return `Command Explanation:\n\n${data.explanation || 'Unable to analyze this command.'}`;
      
      default:
        return JSON.stringify(data, null, 2);
    }
  };

  return (
    <div className="h-full flex flex-col max-w-4xl mx-auto">
      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        {quickActions.map((action) => (
          <button
            key={action.action}
            onClick={() => {
              setActiveAction(action.action === activeAction ? null : action.action);
              setInput('');
            }}
            className={`glass-panel-hover p-3 text-left ${
              activeAction === action.action ? 'border-vigil-primary bg-vigil-primary/5' : ''
            }`}
          >
            <action.icon size={16} className={activeAction === action.action ? 'text-vigil-primary' : 'text-vigil-text-dim'} />
            <p className="text-xs font-medium text-vigil-text mt-1.5">{action.label}</p>
          </button>
        ))}
      </div>

      {/* Chat Area */}
      <div className="flex-1 glass-panel overflow-hidden flex flex-col">
        <div className="flex-1 overflow-auto p-4 space-y-4">
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[80%] rounded-xl px-4 py-3 ${
                msg.role === 'user'
                  ? 'bg-vigil-primary/10 border border-vigil-primary/20 text-vigil-text'
                  : 'bg-vigil-surface border border-vigil-border text-vigil-text'
              }`}>
                {msg.role === 'assistant' && (
                  <div className="flex items-center gap-1.5 mb-1.5">
                    <Brain size={12} className="text-vigil-neon" />
                    <span className="text-[10px] text-vigil-neon font-medium">AI Assistant</span>
                  </div>
                )}
                <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>
              </div>
            </motion.div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-vigil-surface border border-vigil-border rounded-xl px-4 py-3">
                <div className="flex items-center gap-2">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 rounded-full bg-vigil-primary animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 rounded-full bg-vigil-primary animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 rounded-full bg-vigil-primary animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                  <span className="text-xs text-vigil-text-dim">Analyzing...</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="p-4 border-t border-vigil-border">
          <div className="flex items-center gap-2">
            <div className="flex-1 relative">
              <input
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSend()}
                placeholder={
                  quickActions.find(a => a.action === activeAction)?.placeholder ||
                  'Ask about tools, commands, errors, or configurations...'
                }
                className="input-field pr-10"
              />
              {activeAction && (
                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] text-vigil-primary bg-vigil-primary/10 px-1.5 py-0.5 rounded">
                  {activeAction}
                </span>
              )}
            </div>
            <button
              onClick={handleSend}
              disabled={!input.trim() || loading}
              className="btn-primary p-2.5"
            >
              <Send size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
