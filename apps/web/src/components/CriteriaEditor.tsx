'use client';

import { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';
import type { CriteriaConfig } from '@/lib/types';

interface CriteriaEditorProps {
  criteria: CriteriaConfig[];
  onSave?: (criteria: CriteriaConfig[]) => void;
}

export function CriteriaEditor({ criteria, onSave }: CriteriaEditorProps) {
  const [weights, setWeights] = useState<Record<string, number>>({});

  useEffect(() => {
    const initialWeights: Record<string, number> = {};
    criteria.forEach((c) => {
      initialWeights[c.id] = c.weight;
    });
    setWeights(initialWeights);
  }, [criteria]);

  const totalWeight = Object.values(weights).reduce((sum, w) => sum + (w || 0), 0);
  const isValid = Math.abs(totalWeight - 1.0) < 0.01;

  const handleWeightChange = (id: string, value: number) => {
    setWeights((prev) => ({ ...prev, [id]: value }));
  };

  const handleSave = () => {
    if (!isValid || !onSave) return;

    const updatedCriteria = criteria.map((c) => ({
      ...c,
      weight: weights[c.id] || 0,
    }));

    onSave(updatedCriteria);
  };

  return (
    <div className="panel space-y-8">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-black text-white tracking-tight uppercase">
          Criteria Weights
        </h3>
        <div className="text-right">
          <div className="text-[10px] font-black uppercase tracking-widest text-slate-500 mb-1">Status</div>
          <span className={cn(
            'px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-tighter transition-all',
            isValid ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.2)]' : 'bg-red-500/10 text-red-500 border border-red-500/20'
          )}>
            {isValid ? 'Ready to Sync' : 'Invalid Balance'}
          </span>
        </div>
      </div>

      <div className="space-y-8">
        {criteria.map((criterion) => (
          <div key={criterion.id} className="group">
            <div className="flex items-center justify-between mb-4">
              <div>
                <label className="text-xs font-black uppercase tracking-widest text-white block mb-1">
                  {criterion.display_name}
                </label>
                <p className="text-[10px] font-bold text-slate-500 uppercase tracking-tighter group-hover:text-slate-400 transition-colors">
                  {criterion.description}
                </p>
              </div>
              <span className="flex h-10 w-16 items-center justify-center rounded-xl bg-white/5 border border-white/10 text-sm font-black text-white shadow-inner">
                {Math.round((weights[criterion.id] || 0) * 100)}%
              </span>
            </div>
            <div className="relative h-1.5 w-full bg-white/5 rounded-full overflow-hidden border border-white/5">
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={weights[criterion.id] || 0}
                onChange={(e) =>
                  handleWeightChange(criterion.id, parseFloat(e.target.value))
                }
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
              />
              <div
                className="absolute inset-y-0 left-0 bg-white shadow-[0_0_10px_rgba(255,255,255,0.5)] transition-all duration-300"
                style={{ width: `${(weights[criterion.id] || 0) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="pt-6 border-t border-white/5">
        <div className="flex items-center justify-between mb-6">
          <span className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">
            Current Total Sum
          </span>
          <span className={cn(
            "text-xl font-black tracking-tighter",
            isValid ? "text-white" : "text-red-500"
          )}>
            {(totalWeight * 100).toFixed(0)}%
          </span>
        </div>

        <button
          onClick={handleSave}
          disabled={!isValid}
          className={cn(
            'w-full py-4 rounded-xl font-black uppercase tracking-[0.2em] transition-all text-xs shadow-2xl',
            isValid
              ? 'bg-white text-black hover:bg-slate-200'
              : 'bg-white/5 text-slate-600 border border-white/5 cursor-not-allowed'
          )}
        >
          {isValid ? 'Apply New Logic' : 'Sum Must Equal 100%'}
        </button>
      </div>
    </div>
  );
}
