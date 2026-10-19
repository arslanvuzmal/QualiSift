import React from 'react';

export function ScoreBadge({ score }: { score: number | null }) {
  if (score === null) {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border bg-slate-800 text-slate-400 border-slate-700">
        Unscored
      </span>
    );
  }

  if (score >= 75) {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border bg-rose-500/10 text-rose-400 border-rose-500/20 shadow-[0_0_10px_rgba(244,63,94,0.3)]">
        🔥 {score.toFixed(1)} - Hot
      </span>
    );
  }
  
  if (score >= 40) {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border bg-amber-500/10 text-amber-400 border-amber-500/20 shadow-[0_0_10px_rgba(251,191,36,0.2)]">
        🟡 {score.toFixed(1)} - Warm
      </span>
    );
  }

  return (
    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border bg-slate-800 text-slate-500 border-slate-700">
      ❌ {score.toFixed(1)} - Cold
    </span>
  );
}
