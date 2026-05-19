import { CheckCircle, XCircle, Loader, AlertTriangle, Clock, Pause } from 'lucide-react';
import { cn } from '../../utils/cn';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md';
  showIcon?: boolean;
}

const statusConfig: Record<string, { icon: any; className: string; label: string }> = {
  completed: { icon: CheckCircle, className: 'badge-success', label: 'Completed' },
  success: { icon: CheckCircle, className: 'badge-success', label: 'Success' },
  running: { icon: Loader, className: 'badge-info', label: 'Running' },
  installing: { icon: Loader, className: 'badge-info', label: 'Installing' },
  pending: { icon: Clock, className: 'bg-vigil-text-dim/10 text-vigil-text-dim border border-vigil-text-dim/20', label: 'Pending' },
  idle: { icon: Clock, className: 'bg-vigil-text-dim/10 text-vigil-text-dim border border-vigil-text-dim/20', label: 'Idle' },
  failed: { icon: XCircle, className: 'badge-danger', label: 'Failed' },
  error: { icon: XCircle, className: 'badge-danger', label: 'Error' },
  stopped: { icon: Pause, className: 'badge-warning', label: 'Stopped' },
  timeout: { icon: AlertTriangle, className: 'badge-warning', label: 'Timeout' },
  installed: { icon: CheckCircle, className: 'badge-success', label: 'Installed' },
  not_installed: { icon: XCircle, className: 'bg-vigil-text-dim/10 text-vigil-text-dim border border-vigil-text-dim/20', label: 'Not Installed' },
  disabled: { icon: Pause, className: 'badge-warning', label: 'Disabled' },
};

export default function StatusBadge({ status, size = 'sm', showIcon = true }: StatusBadgeProps) {
  const config = statusConfig[status] || statusConfig.pending;
  const Icon = config.icon;
  const textSize = size === 'sm' ? 'text-[10px]' : 'text-xs';
  const iconSize = size === 'sm' ? 10 : 12;

  return (
    <span className={cn('inline-flex items-center gap-1 px-2 py-0.5 rounded-full font-medium', textSize, config.className)}>
      {showIcon && <Icon size={iconSize} className={status === 'running' || status === 'installing' ? 'animate-spin' : ''} />}
      {config.label}
    </span>
  );
}
