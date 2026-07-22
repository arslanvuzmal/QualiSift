import React from 'react';

export function ScoreBadge({ score }: { score: number | null }) {
  if (score === null) {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border bg-slate-800 text-slate-400 border-slate-700">
        Unscored
      </span>
    );
  }

interface ScoreBadgeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function ScoreBadge({ score, size = 'md', className }: ScoreBadgeProps) {
  const getColorClasses = (score: number) => {
    if (score >= 75) {
      return {
        bg: 'bg-white',
        text: 'text-black',
        border: 'border-white',
        shadow: 'shadow-[0_0_15px_rgba(255,255,255,0.4)]',
      };
    }
    if (score >= 40) {
      return {
        bg: 'bg-[#888]',
        text: 'text-white',
        border: 'border-[#aaa]',
        shadow: 'shadow-lg',
      };
    }
    return {
      bg: 'bg-[#333]',
      text: 'text-slate-400',
      border: 'border-[#444]',
      shadow: 'shadow-sm',
    };
  };

  const sizeClasses = {
    sm: 'px-2.5 py-0.5 text-[10px] tracking-widest',
    md: 'px-4 py-1 text-xs tracking-[0.2em]',
    lg: 'px-6 py-2 text-sm tracking-[0.3em]',
  };

  const colors = getColorClasses(score);

  return (
    <span
      className={cn(
        'inline-flex items-center font-black uppercase rounded-full border transition-all',
        colors.bg,
        colors.text,
        colors.border,
        colors.shadow,
        sizeClasses[size],
        className
      )}
    >
      {score}/100
  if (score >= 75) {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border bg-rose-500/10 text-rose-400 border-rose-500/20 shadow-[0_0_10px_rgba(244,63,94,0.3)]">
        🔥 {score.toFixed(0)} - Hot
      </span>
    );
  }
  
  if (score >= 40) {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border bg-amber-500/10 text-amber-400 border-amber-500/20 shadow-[0_0_10px_rgba(251,191,36,0.2)]">
        🟡 {score.toFixed(0)} - Warm
      </span>
    );
  }

  return (
    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border bg-slate-800 text-slate-500 border-slate-700">
      ❌ {score.toFixed(0)} - Cold
    </span>
  );
}
