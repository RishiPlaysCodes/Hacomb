import { useState } from 'react';
import { X, Minimize2, Maximize2 } from 'lucide-react';
import { useAppStore } from '../../store/appStore';

export default function TerminalPanel() {
  const { toggleTerminal, setTerminalHeight, terminalHeight } = useAppStore();
  const [isMaximized, setIsMaximized] = useState(false);

  const handleMaximize = () => {
    if (isMaximized) {
      setTerminalHeight(300);
    } else {
      setTerminalHeight(600);
    }
    setIsMaximized(!isMaximized);
  };

  return (
    <div className="h-full flex flex-col bg-vigil-bg">
      {/* Terminal Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-vigil-surface border-b border-vigil-border">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-vigil-danger/70" />
            <div className="w-3 h-3 rounded-full bg-vigil-warning/70" />
            <div className="w-3 h-3 rounded-full bg-vigil-success/70" />
          </div>
          <span className="text-xs text-vigil-text-muted ml-2 font-mono">Terminal Output</span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={handleMaximize}
            className="p-1 rounded hover:bg-vigil-hover text-vigil-text-dim hover:text-vigil-text transition-colors"
          >
            {isMaximized ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
          </button>
          <button
            onClick={toggleTerminal}
            className="p-1 rounded hover:bg-vigil-hover text-vigil-text-dim hover:text-vigil-text transition-colors"
          >
            <X size={14} />
          </button>
        </div>
      </div>

      {/* Terminal Content */}
      <div className="flex-1 overflow-auto p-4 font-mono text-sm">
        <div className="text-vigil-text-dim">
          <p className="text-vigil-neon">╔══════════════════════════════════════╗</p>
          <p className="text-vigil-neon">║       VIGIL LABS Terminal v1.0       ║</p>
          <p className="text-vigil-neon">╚══════════════════════════════════════╝</p>
          <p className="mt-2 text-vigil-text-muted">Ready. Execute a tool to see live output here.</p>
          <p className="text-vigil-text-dim mt-1">
            <span className="text-vigil-primary">vigil@labs</span>
            <span className="text-vigil-text-muted">:</span>
            <span className="text-vigil-secondary">~</span>
            <span className="text-vigil-text-muted">$ </span>
            <span className="animate-pulse">▊</span>
          </p>
        </div>
      </div>
    </div>
  );
}
