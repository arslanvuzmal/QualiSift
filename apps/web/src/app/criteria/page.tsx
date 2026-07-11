'use client';
import { useCriteria } from '@/lib/hooks';
import { CriteriaEditor } from '@/components/CriteriaEditor';

export default function CriteriaPage() {
  const { criteria, isLoading, mutate } = useCriteria();

  return (
    <div className="max-w-4xl mx-auto pb-24">
      <div className="mb-8">
        <h1 className="text-2xl font-bold tracking-tight text-slate-100">Scoring Criteria</h1>
        <p className="text-sm text-slate-400 mt-1">
          Tune how much each criterion contributes to a lead's composite score. Weights must sum to 100%.
        </p>
      </div>
      
      {isLoading ? (
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-32 bg-slate-900 animate-pulse rounded-xl border border-slate-800" />
          ))}
        </div>
      ) : (
        <CriteriaEditor criteria={criteria} onSaveSuccess={() => mutate()} />
      )}
    </div>
  );
}
