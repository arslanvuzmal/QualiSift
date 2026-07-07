'use client';

import dynamic from 'next/dynamic';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import {
  ArrowLeft,
  RefreshCw,
  Building2,
  User,
  Mail,
  Calendar,
  Globe,
  Briefcase,
  ExternalLink,
  Target,
  Sparkles,
  Info,
} from 'lucide-react';
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

  if (isLoading)
    return (
      <div className="flex h-64 items-center justify-center">
        <RefreshCw className="h-10 w-10 animate-spin text-white opacity-20" />
      </div>
    );
  if (!lead) return <div className="panel text-center py-20 font-black uppercase tracking-[0.2em] text-slate-500">Lead not found.</div>;

  const composite = lead.composite_score;
  const enriched = (lead.enriched_data ?? {}) as Record<string, unknown>;

  return (
    <div className="max-w-5xl space-y-8">
      <div className="flex items-center justify-between">
        <Link
          href="/"
          className="group inline-flex items-center gap-3 text-xs font-black uppercase tracking-widest text-slate-500 hover:text-white transition-all"
        >
          <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-white/10 bg-white/5 group-hover:border-white/30 group-hover:-translate-x-1 transition-all">
            <ArrowLeft className="h-4 w-4" />
          </div>
          Dashboard
        </Link>
        <div className="flex items-center gap-3">
          <span className={`badge-admin px-4 py-1.5 font-black uppercase tracking-tighter ${lead.status === 'scored' ? 'badge-ok' : 'badge-neutral'}`}>
            {lead.status}
          </span>
          <span className="text-[10px] font-black uppercase tracking-widest text-slate-600 bg-white/5 px-2 py-1 rounded border border-white/5">ID: {id?.slice(0, 8)}</span>
        </div>
      </div>

      {/* Header Card */}
      <div className="panel border-t-2 border-t-white overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-8">
          <div className="flex items-center gap-6">
            <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-[#444] to-[#000] text-3xl font-black text-white shadow-2xl border border-white/10">
              {lead.company?.[0] || 'L'}
            </div>
            <div>
              <h1 className="text-4xl font-black tracking-tighter text-white">
                {lead.company}
              </h1>
              <div className="mt-2 flex flex-wrap items-center gap-x-6 gap-y-2 text-xs font-bold uppercase tracking-wide text-slate-500">
                <span className="flex items-center gap-2">
                  <User className="h-3.5 w-3.5" /> {lead.first_name} {lead.last_name}
                </span>
                <span className="flex items-center gap-2">
                  <Briefcase className="h-3.5 w-3.5" /> {lead.job_title}
                </span>
                <span className="flex items-center gap-2 lowercase tracking-normal">
                  <Mail className="h-3.5 w-3.5" /> {lead.email}
                </span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-6">
            {composite && (
              <div className="text-center md:text-right">
                <div className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-600 mb-2">
                  Composite Score
                </div>
                <div className="relative inline-block">
                  <div className="absolute inset-0 blur-lg bg-white/10 rounded-full" />
                  <ScoreBadge score={Math.round(composite.composite_score)} size="lg" className="relative z-10 scale-110" />
                </div>
              </div>
            )}
            <button
              onClick={handleRescore}
              disabled={rescoring}
              className="flex h-12 items-center gap-3 rounded-xl bg-white px-6 text-sm font-black uppercase tracking-widest text-black shadow-xl transition-all hover:bg-slate-200 disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 ${rescoring ? 'animate-spin' : ''}`} />
              {rescoring ? 'Processing' : 'Re-score'}
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Analysis */}
        <div className="lg:col-span-2 space-y-8">
          {composite && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="panel bg-white/5 border-white/5">
                <div className="flex items-center gap-3 mb-4">
                  <Target className="h-5 w-5 text-white" />
                  <h3 className="text-xs font-black uppercase tracking-[0.2em] text-white">
                    Lead Analysis
                  </h3>
                </div>
                <p className="text-sm font-medium leading-relaxed text-slate-300">
                  {composite.overall_summary}
                </p>
              </div>
              <div className="panel border-white/20 bg-white text-black">
                <div className="flex items-center gap-3 mb-4">
                  <Sparkles className="h-5 w-5" />
                  <h3 className="text-xs font-black uppercase tracking-[0.2em]">Strategy</h3>
                </div>
                <p className="text-sm font-black leading-relaxed">{composite.suggested_action}</p>
              </div>
            </div>
          )}

          <div className="panel">
            <h3 className="flex items-center gap-3 text-xl font-black mb-8 text-white">
              <Info className="h-6 w-6 text-slate-500" />
              Scoring Breakdown
            </h3>
            <div className="space-y-6">
              {(lead.scores ?? []).map((s) => (
                <div
                  key={s.id}
                  className="rounded-2xl border border-white/5 bg-white/[0.02] p-6 transition-all hover:bg-white/[0.04] hover:border-white/10"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-4">
                      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white text-black font-black text-sm shadow-xl">
                        {s.score}
                      </div>
                      <span className="font-black text-white uppercase tracking-tight text-lg">
                        {s.criteria_name.replace(/_/g, ' ')}
                      </span>
                    </div>
                    <span className="text-[10px] font-black uppercase tracking-widest text-slate-500 bg-white/5 px-3 py-1 rounded-full border border-white/5">
                      {(s.confidence * 100).toFixed(0)}% confidence
                    </span>
                  </div>
                  <p className="text-sm font-medium text-slate-400 leading-relaxed mb-4">{s.reasoning}</p>
                  {s.cited_evidence && s.cited_evidence.length > 0 && (
                    <div className="flex flex-wrap gap-2 pt-4 border-t border-white/5">
                      {s.cited_evidence.map((e, i) => (
                        <span
                          key={i}
                          className="inline-flex items-center px-3 py-1 rounded-lg bg-white/5 border border-white/10 text-[10px] font-black uppercase tracking-widest text-slate-400"
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
        </div>

        {/* Right Column: Visualization & Details */}
        <div className="space-y-8">
          <div className="panel">
            <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 mb-6">Visual Metrics</h3>
            {lead.scores && lead.scores.length > 0 ? (
              <div className="h-[280px]">
                <ScoreRadar scores={lead.scores} />
              </div>
            ) : (
              <div className="py-20 text-center text-[10px] font-black uppercase tracking-widest text-slate-700">No Metrics</div>
            )}
          </div>

          <div className="panel">
            <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 mb-6">Firmographics</h3>
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-x-4 gap-y-6">
                {[
                  { label: 'Industry', value: enriched.industry, icon: Building2 },
                  { label: 'Staff', value: enriched.employee_count, icon: User },
                  { label: 'Base', value: enriched.headquarters, icon: Globe },
                  { label: 'Year', value: enriched.founded_year, icon: Calendar },
                ].map(
                  (item) =>
                    item.value != null && (
                      <div key={item.label} className="space-y-2">
                        <div className="flex items-center gap-2 text-[9px] font-black uppercase tracking-widest text-slate-600">
                          <item.icon className="h-3 w-3" /> {item.label}
                        </div>
                        <div className="text-sm font-black text-white truncate uppercase tracking-tight">{String(item.value)}</div>
                      </div>
                    )
                )}
              </div>
              {lead.company_domain && (
                <div className="pt-6 border-t border-white/5">
                  <a
                    href={`https://${lead.company_domain}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-center gap-3 w-full h-11 bg-white/5 border border-white/10 rounded-xl text-xs font-black uppercase tracking-[0.2em] text-slate-400 hover:bg-white hover:text-black hover:border-white transition-all shadow-sm"
                  >
                    Site <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
