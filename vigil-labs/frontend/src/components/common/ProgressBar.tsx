import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';

interface ProgressBarProps {
  value: number;
  max?: number;
  variant?: 'primary' | 'success' | 'warning' | 'danger';
  size?: 'sm' | 'md';
  showLabel?: boolean;
  animated?: boolean;
  className?: string;
}

export default function ProgressBar({
  value,
  max = 100,
  variant = 'primary',
  size = 'sm',
  showLabel = false,
  animated = true,
  className,
}: ProgressBarProps) {
  const percent = Math.min((value / max) * 100, 100);
  
  const colors = {
    primary: 'from-vigil-primary to-vigil-secondary',
    success: 'from-vigil-success to-emerald-400',
    warning: 'from-vigil-warning to-amber-400',
    danger: 'from-vigil-danger to-red-400',
  };
  
  const heights = { sm: 'h-1.5', md: 'h-2.5' };

  return (
    <div className={cn('w-full', className)}>
      {showLabel && (
        <div className="flex justify-between text-xs text-vigil-text-muted mb-1">
          <span>{value}/{max}</span>
          <span>{percent.toFixed(0)}%</span>
        </div>
      )}
      <div className={cn('w-full bg-vigil-bg rounded-full overflow-hidden', heights[size])}>
        <motion.div
          initial={animated ? { width: 0 } : undefined}
          animate={{ width: `${percent}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className={cn('h-full rounded-full bg-gradient-to-r', colors[variant])}
        />
      </div>
    </div>
  );
}
