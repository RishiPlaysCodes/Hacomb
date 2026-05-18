import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';
import { cn } from '../../utils/cn';

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
}

export default function EmptyState({ icon: Icon, title, description, action, className }: EmptyStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className={cn('text-center py-16 glass-panel', className)}
    >
      <motion.div
        initial={{ y: 10 }}
        animate={{ y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="w-16 h-16 mx-auto rounded-2xl bg-vigil-primary/5 border border-vigil-border flex items-center justify-center mb-4">
          <Icon size={28} className="text-vigil-text-dim" />
        </div>
        <h3 className="text-lg font-semibold text-vigil-text">{title}</h3>
        {description && (
          <p className="text-sm text-vigil-text-muted mt-1.5 max-w-sm mx-auto">{description}</p>
        )}
        {action && (
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={action.onClick}
            className="btn-primary mt-5 text-sm"
          >
            {action.label}
          </motion.button>
        )}
      </motion.div>
    </motion.div>
  );
}
