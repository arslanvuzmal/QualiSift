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
    <div className="bg-white border rounded-lg p-6">
      <h3 className="text-lg font-semibold text-slate-900 mb-4">
        Scoring Criteria Weights
      </h3>

      <div className="space-y-4">
        {criteria.map((criterion) => (
          <div key={criterion.id}>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-slate-700">
                {criterion.display_name}
              </label>
              <span className="text-sm text-slate-600">
                {(weights[criterion.id] || 0).toFixed(2)}
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={weights[criterion.id] || 0}
              onChange={(e) =>
                handleWeightChange(criterion.id, parseFloat(e.target.value))
              }
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
            />
            <p className="text-xs text-slate-500 mt-1">{criterion.description}</p>
          </div>
        ))}
      </div>

      <div
        className={cn(
          'mt-6 p-4 rounded-lg',
          isValid ? 'bg-emerald-50 border border-emerald-200' : 'bg-amber-50 border border-amber-200'
        )}
      >
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">
            Total Weight: {totalWeight.toFixed(2)}
          </span>
          <span
            className={cn(
              'text-sm font-semibold',
              isValid ? 'text-emerald-800' : 'text-amber-800'
            )}
          >
            {isValid ? '✓ Valid' : '⚠ Must equal 1.0'}
          </span>
        </div>
      </div>

      <button
        onClick={handleSave}
        disabled={!isValid}
        className={cn(
          'mt-4 w-full py-2 px-4 rounded-lg font-medium transition-colors',
          isValid
            ? 'bg-indigo-600 text-white hover:bg-indigo-700'
            : 'bg-slate-200 text-slate-500 cursor-not-allowed'
        )}
      >
        Save Weights
      </button>
    </div>
  );
}
