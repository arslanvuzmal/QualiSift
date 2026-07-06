'use client';

import { cn } from '@/lib/utils';

interface ScoreBadgeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function ScoreBadge({ score, size = 'md', className }: ScoreBadgeProps) {
  const getColorClasses = (score: number) => {
    if (score >= 75) {
      return {
        bg: 'bg-rose-100',
        text: 'text-rose-800',
        border: 'border-rose-200',
      };
    }
    if (score >= 40) {
      return {
        bg: 'bg-amber-100',
        text: 'text-amber-800',
        border: 'border-amber-200',
      };
    }
    return {
      bg: 'bg-slate-100',
      text: 'text-slate-800',
      border: 'border-slate-200',
    };
  };

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-1.5 text-base',
  };

  const colors = getColorClasses(score);

  return (
    <span
      className={cn(
        'inline-flex items-center font-semibold rounded-full border',
        colors.bg,
        colors.text,
        colors.border,
        sizeClasses[size],
        className
      )}
    >
      {score}/100
    </span>
  );
}
