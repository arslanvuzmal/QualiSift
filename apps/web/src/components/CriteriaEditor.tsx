'use client';

import { useState, useEffect } from 'react';
import { updateCriteria } from '@/lib/api';
import type { CriteriaConfig } from '@/lib/types';
import { toast } from 'sonner';
import { Save, AlertTriangle, CheckCircle2 } from 'lucide-react';

export function CriteriaEditor({ criteria, onSaveSuccess }: { criteria: CriteriaConfig[], onSaveSuccess: () => void }) {
  const [weights, setWeights] = useState<Record<string, number>>({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const initialWeights: Record<string, number> = {};
    criteria.forEach((c) => {
      initialWeights[c.id] = c.weight;
    });
    setWeights(initialWeights);
  }, [criteria]);

  const totalWeight = Object.values(weights).reduce((sum, w) => sum + (w || 0), 0);
  // Tolerance matches the slider step (0.05) to avoid false negatives
  // when users set weights to valid slider positions that don't sum exactly to 1.0
  const isValid = Math.abs(totalWeight - 1.0) < 0.051;
  const percentage = Math.round(totalWeight * 100);

  const handleWeightChange = (id: string, value: number) => {
    setWeights((prev) => ({ ...prev, [id]: value }));
  };

  const handleSave = async () => {
    if (!isValid) return;
    setSaving(true);
    try {
      await Promise.all(
        criteria.map((c) => updateCriteria(c.id, { weight: weights[c.id] || 0 }))
      );
      toast.success('Criteria weights updated successfully.');
      onSaveSuccess();
    } catch {
      toast.error('Failed to save weights.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <div className="space-y-4">
        {criteria.map((criterion) => {
          const w = weights[criterion.id] || 0;
          return (
            <div key={criterion.id} className="enterprise-card p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-slate-100 capitalize">
                    {criterion.display_name.replace(/_/g, ' ')}
                  </h3>
                  <p className="text-sm text-slate-400 mt-1">{criterion.description}</p>
                </div>
                <div className="flex h-10 min-w-[4rem] items-center justify-center rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 font-bold shadow-[0_0_10px_rgba(99,102,241,0.1)]">
                  {Math.round(w * 100)}%
                </div>
              </div>
              
              <div className="pt-2">
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={w}
                  onChange={(e) => handleWeightChange(criterion.id, parseFloat(e.target.value))}
                  className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-slate-950"
                />
                <div className="flex justify-between text-xs font-medium text-slate-500 mt-2">
                  <span>0%</span>
                  <span>50%</span>
                  <span>100%</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Sticky Banner */}
      <div className="fixed bottom-0 left-0 right-0 z-50 lg:pl-64 border-t border-slate-800 bg-slate-950/90 backdrop-blur-md p-4 shadow-[0_-4px_15px_rgba(0,0,0,0.2)]">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            {!isValid ? (
              <>
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20">
                  <AlertTriangle className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-sm font-bold text-rose-400">Weights must equal 100%.</p>
                  <p className="text-xs font-medium text-rose-500 mt-0.5">Current: {percentage}%</p>
                </div>
              </>
            ) : (
              <>
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.1)]">
                  <CheckCircle2 className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-sm font-bold text-emerald-400">Weights are valid.</p>
                  <p className="text-xs font-medium text-emerald-500 mt-0.5">Current: 100%</p>
                </div>
              </>
            )}
          </div>
          
          <button
            onClick={handleSave}
            disabled={!isValid || saving}
            className={`btn-primary px-8 ${
              isValid ? 'bg-indigo-600 hover:bg-indigo-500' : 'bg-slate-800 text-slate-500 hover:bg-slate-800'
            }`}
          >
            {saving ? (
              <span className="flex items-center gap-2">
                <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Saving...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <Save className="h-4 w-4" /> Save Configuration
              </span>
            )}
          </button>
        </div>
      </div>
    </>
  );
}
