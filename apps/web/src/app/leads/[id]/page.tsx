'use client';

import dynamic from 'next/dynamic';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { ArrowLeft, RefreshCw } from 'lucide-react';
import { useLead } from '@/lib/hooks';
import { ScoreBadge } from '@/components/ScoreBadge';
import { scoreLead } from '@/lib/api';
import { useState } from 'react';

// Recharts must render client-side only to avoid hydration mismatches.
const ScoreRadar = dynamic(
  () => import('@/components/ScoreRadar').then((m) => m.ScoreRadar),
  { ssr: false, loading: () => <div className="h-[300px]" /> }
);

export default function LeadDetailPage() {
  const params = useParams();
  const id = (params?.id as string) ?? null;
  const { lead, isLoading, mutate } = useLead(id);
  const [rescoring, setRescoring] = useState(false);

  const handleRescore = async () => {
    if (!id) return;
    setRescoring(true);
    try {
      await scoreLead(id);
      setTimeout(() => mutate(), 1500);
    } finally {
      setTimeout(() => setRescoring(false), 1500);
    }
  };

  if (isLoading) return <p className="text-slate-500">Loading lead…</p>;
  if (!lead) return <p className="text-slate-500">Lead not found.</p>;

  const composite = lead.composite_score;
  const enriched = (lead.enriched_data ?? {}) as Record<string, unknown>;

  return (
    <div className="max-w-4xl">
      <Link
        href="/"
        className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-900 mb-4"
      >
        <ArrowLeft className="h-4 w-4" /> Back to dashboard
      </Link>

      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{lead.company}</h1>
          <p className="text-slate-600">
            {lead.first_name} {lead.last_name} • {lead.job_title}
          </p>
          <p className="text-sm text-slate-500">{lead.email}</p>
        </div>
        <div className="flex items-center gap-3">
          {composite && <ScoreBadge score={Math.round(composite.composite_score)} size="lg" />}
          <button
            onClick={handleRescore}
            disabled={rescoring}
            className="flex items-center gap-2 px-3 py-2 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${rescoring ? 'animate-spin' : ''}`} />
            Re-score
          </button>
        </div>
      </div>

      {composite && (
        <div className="grid md:grid-cols-2 gap-4 mb-6">
          <div className="bg-white border rounded-lg p-4">
            <h3 className="text-sm font-semibold text-slate-700 mb-2">Why this lead matters</h3>
            <p className="text-sm text-slate-600">{composite.overall_summary}</p>
          </div>
          <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-indigo-800 mb-2">Suggested action</h3>
            <p className="text-sm text-indigo-900">{composite.suggested_action}</p>
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white border rounded-lg p-4">
          <h3 className="text-sm font-semibold text-slate-700 mb-2">Criteria radar</h3>
          {lead.scores && lead.scores.length > 0 ? (
            <ScoreRadar scores={lead.scores} />
          ) : (
            <p className="text-sm text-slate-500">Not scored yet.</p>
          )}
        </div>

        <div className="bg-white border rounded-lg p-4">
          <h3 className="text-sm font-semibold text-slate-700 mb-3">Enrichment</h3>
          <dl className="space-y-1 text-sm">
            {(['industry', 'employee_count', 'headquarters', 'founded_year'] as const).map(
              (k) =>
                enriched[k] != null && (
                  <div key={k} className="flex justify-between">
                    <dt className="text-slate-500 capitalize">{k.replace(/_/g, ' ')}</dt>
                    <dd className="text-slate-900">{String(enriched[k])}</dd>
                  </div>
                )
            )}
          </dl>
        </div>
      </div>

      <h3 className="text-lg font-semibold text-slate-900 mt-8 mb-3">Per-criterion scores</h3>
      <div className="space-y-3">
        {(lead.scores ?? []).map((s) => (
          <div key={s.id} className="bg-white border rounded-lg p-4">
            <div className="flex items-center justify-between mb-1">
              <span className="font-medium text-slate-900 capitalize">
                {s.criteria_name.replace(/_/g, ' ')}
              </span>
              <span className="text-sm text-slate-600">
                {s.score}/10 · {(s.confidence * 100).toFixed(0)}% confidence
              </span>
            </div>
            <p className="text-sm text-slate-600">{s.reasoning}</p>
            {s.cited_evidence && s.cited_evidence.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1.5">
                {s.cited_evidence.map((e, i) => (
                  <span
                    key={i}
                    className="inline-flex items-center px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-xs"
                  >
                    {e}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
