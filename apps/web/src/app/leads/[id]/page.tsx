'use client';

import { useState } from 'react';
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
import { 
  ArrowLeft, RefreshCw, Mail, Building, Globe, 
  Code, Send, MessageSquare, Trash2, Clock 
} from 'lucide-react';
import { useLead } from '@/lib/hooks';
import { scoreLead } from '@/lib/api';
import { toast } from 'sonner';
import { format } from 'date-fns';

const ScoreRadar = dynamic(
  () => import('@/components/ScoreRadar').then((m) => m.ScoreRadar),
  { ssr: false, loading: () => <div className="h-64 w-full animate-pulse bg-slate-800 rounded-lg" /> }
);

export default function LeadDetailPage() {
  const params = useParams();
  const id = (params?.id as string) ?? null;
  const { lead, isLoading, mutate } = useLead(id);
  const [rescoring, setRescoring] = useState(false);
  const [showPayload, setShowPayload] = useState(false);
  const [expandedCriteria, setExpandedCriteria] = useState<Record<string, boolean>>({});

  const handleRescore = async () => {
    if (!id) return;
    setRescoring(true);
    toast.info('Rescoring lead...');
    try {
      await scoreLead(id);
      setTimeout(() => {
        mutate();
        toast.success('Lead rescored successfully!');
      }, 1500);
    } catch {
      toast.error('Failed to rescore lead.');
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
  const toggleCriteria = (id: string) => {
    setExpandedCriteria(prev => ({ ...prev, [id]: !prev[id] }));
  };

  if (isLoading) {
    return (
      <div className="flex justify-center py-20">
        <div className="animate-spin h-8 w-8 border-4 border-indigo-600 border-t-transparent rounded-full" />
      </div>
    );
  }
  
  if (!lead) {
    return (
      <div className="text-center py-20">
        <h2 className="text-xl font-bold text-slate-100">Lead not found</h2>
        <Link href="/" className="mt-4 text-indigo-400 hover:underline inline-block">Return to dashboard</Link>
      </div>
    );
  }

  const composite = lead.composite_score;
  const enriched = (lead.enriched_data ?? {}) as Record<string, unknown>;
  const radarData = (lead.scores ?? []).map(s => ({
    subject: s.criteria_name.replace(/_/g, ' ').toUpperCase(),
    score: s.score,
    fullMark: 10
  }));

  const compositeVal = composite?.composite_score ?? 0;
  // Circular progress stroke calculation
  const radius = 36;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (compositeVal / 100) * circumference;

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
    <div className="max-w-[1400px] mx-auto">
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-400 hover:text-slate-100 mb-6 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" /> Back to pipeline
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* LEFT COLUMN: Context (30%) - approx col-span-3 or 4 */}
        <div className="lg:col-span-3 space-y-6">
          <div className="enterprise-card bg-slate-900 border-slate-800 p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-slate-800 text-lg font-bold text-slate-300">
                {((lead.first_name?.[0] ?? '') + (lead.last_name?.[0] ?? '')).toUpperCase() || 'L'}
              </div>
              <div className="overflow-hidden">
                <h2 className="text-lg font-bold text-slate-100 truncate">{lead.first_name} {lead.last_name}</h2>
                <p className="text-sm font-medium text-slate-400 truncate">{lead.job_title}</p>
              </div>
            </div>
            
            <div className="space-y-3 pt-4 border-t border-slate-800">
              <div className="flex items-center gap-3 text-sm text-slate-400">
                <Building className="h-4 w-4 text-slate-500 shrink-0" />
                <span className="font-medium text-slate-300 truncate">{lead.company}</span>
              </div>
              <div className="flex items-center gap-3 text-sm text-slate-400">
                <Mail className="h-4 w-4 text-slate-500 shrink-0" />
                <a href={`mailto:${lead.email}`} className="text-indigo-400 hover:text-indigo-300 hover:underline truncate">{lead.email}</a>
              </div>
            </div>
          </div>

          <div className="enterprise-card bg-slate-900 border-slate-800 p-6">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-4">Firmographics</h3>
            <div className="space-y-4">
              {(['industry', 'employee_count', 'headquarters', 'founded_year'] as const).map((k) => (
                enriched[k] != null && (
                  <div key={k}>
                    <p className="text-xs text-slate-500 capitalize">{k.replace(/_/g, ' ')}</p>
                    <p className="text-sm font-medium text-slate-300 mt-0.5">{String(enriched[k])}</p>
                  </div>
                )
              ))}
            </div>
          </div>

          <div className="enterprise-card overflow-hidden bg-slate-900 border-slate-800">
            <button 
              onClick={() => setShowPayload(!showPayload)}
              className="w-full flex items-center justify-between p-4 bg-slate-800/50 text-sm font-medium text-slate-300 hover:bg-slate-800 transition-colors"
            >
              <span className="flex items-center gap-2"><Code className="h-4 w-4 text-slate-400" /> Raw Payload</span>
              <span className="text-lg text-slate-500">{showPayload ? '-' : '+'}</span>
            </button>
            {showPayload && (
              <div className="p-4 bg-slate-950 text-slate-300 text-xs font-mono overflow-x-auto max-h-96">
                <pre>{JSON.stringify(lead.raw_payload || {}, null, 2)}</pre>
              </div>
            )}
          </div>
        </div>

        {/* MIDDLE COLUMN: AI Insights (45%) - approx col-span-6 */}
        <div className="lg:col-span-6 space-y-6">
          <div className="enterprise-card bg-slate-900 border-slate-800 p-8">
            <div className="flex items-start justify-between mb-8">
              <div className="flex items-center gap-6">
                <div className="relative flex items-center justify-center shrink-0">
                  <svg className="transform -rotate-90 w-24 h-24">
                    <circle cx="48" cy="48" r={radius} stroke="currentColor" strokeWidth="8" fill="transparent" className="text-slate-800" />
                    <circle 
                      cx="48" cy="48" r={radius} stroke="currentColor" strokeWidth="8" fill="transparent"
                      strokeDasharray={circumference} strokeDashoffset={strokeDashoffset}
                      className={compositeVal >= 75 ? 'text-rose-500' : compositeVal >= 40 ? 'text-amber-500' : 'text-slate-400'}
                      style={{ transition: 'stroke-dashoffset 1s ease-out' }}
                    />
                  </svg>
                  <div className="absolute flex flex-col items-center justify-center">
                    <span className="text-2xl font-bold text-slate-100">{Math.round(compositeVal)}</span>
                  </div>
                </div>
                <div>
                  <h2 className="text-xl font-bold text-slate-100 mb-1">Composite Score</h2>
                  <p className="text-sm text-slate-400">{composite?.overall_summary || 'No AI summary available yet.'}</p>
                </div>
              </div>
              <button
                onClick={handleRescore}
                disabled={rescoring}
                className="btn-secondary shrink-0"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${rescoring ? 'animate-spin' : ''}`} />
                Re-score Lead
              </button>
            </div>

            {radarData.length > 0 && (
              <div className="mb-8 border-b border-slate-800 pb-8">
                <ScoreRadar data={radarData} />
              </div>
            ) : (
              <div className="py-20 text-center text-[10px] font-black uppercase tracking-widest text-slate-700">No Metrics</div>
            )}

            <div>
              <h3 className="text-base font-bold text-slate-100 mb-4">Criteria Breakdown</h3>
              <div className="space-y-4">
                {(lead.scores ?? []).map((s) => (
                  <div key={s.id} className="border border-slate-800 rounded-lg overflow-hidden">
                    <button 
                      onClick={() => toggleCriteria(s.id.toString())}
                      className="w-full flex items-center justify-between p-4 bg-slate-900 hover:bg-slate-800/50 transition-colors"
                    >
                      <div className="flex-1 text-left">
                        <div className="flex justify-between mb-2">
                          <span className="font-semibold text-slate-300 capitalize text-sm">{s.criteria_name.replace(/_/g, ' ')}</span>
                          <span className="text-sm font-bold text-slate-400">{s.score}/10</span>
                        </div>
                        <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-indigo-500 rounded-full shadow-[0_0_8px_rgba(99,102,241,0.5)]" 
                            style={{ width: `${(s.score / 10) * 100}%` }}
                          />
                        </div>
                      </div>
                    </button>
                    {expandedCriteria[s.id.toString()] && (
                      <div className="p-4 bg-slate-800/30 border-t border-slate-800">
                        <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">AI Reasoning</h4>
                        <p className="text-sm text-slate-300 leading-relaxed mb-4">{s.reasoning}</p>
                        
                        {s.cited_evidence && s.cited_evidence.length > 0 && (
                          <div>
                            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">Cited Evidence</h4>
                            <div className="space-y-2">
                              {s.cited_evidence.map((evidence, i) => (
                                <div key={i} className="px-3 py-2 bg-slate-900 border border-slate-700 rounded-md text-xs text-slate-400 font-mono">
                                  {evidence}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: Actions & Timeline (25%) - approx col-span-3 */}
        <div className="lg:col-span-3 space-y-6">
          <div className="enterprise-card bg-slate-900 border-amber-500/20 shadow-[0_0_15px_rgba(251,191,36,0.05)] p-6">
            <h3 className="text-xs font-bold uppercase tracking-wider text-amber-500 mb-3">Suggested Action</h3>
            <p className="text-sm font-medium text-amber-100 leading-relaxed">
              {composite?.suggested_action || 'Review details and decide on next steps manually.'}
            </p>
          </div>

          <div className="enterprise-card bg-slate-900 border-slate-800 p-6 space-y-3">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-4">Quick Actions</h3>
            <button className="w-full btn-primary bg-indigo-600 hover:bg-indigo-500">
              <Send className="h-4 w-4 mr-2" /> Draft Email
            </button>
            <button className="w-full btn-secondary">
              <MessageSquare className="h-4 w-4 mr-2 text-slate-400" /> Log to CRM
            </button>
            <button className="w-full btn-secondary text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 hover:border-rose-500/20">
              <Trash2 className="h-4 w-4 mr-2" /> Mark as Bad Lead
            </button>
          </div>

          <div className="enterprise-card bg-slate-900 border-slate-800 p-6">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-6">Activity Timeline</h3>
            <div className="relative border-l border-slate-700 ml-3 space-y-6 pb-2">
              
              <div className="relative pl-6">
                <span className="absolute -left-1.5 top-1 h-3 w-3 rounded-full bg-slate-600 ring-4 ring-slate-900" />
                <p className="text-sm font-medium text-slate-300">Lead Ingested</p>
                <p className="text-xs text-slate-500 mt-1 flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {format(new Date(lead.created_at || Date.now()), 'MMM d, h:mm a')}
                </p>
              </div>

              {lead.enriched_data && (
                <div className="relative pl-6">
                  <span className="absolute -left-1.5 top-1 h-3 w-3 rounded-full bg-indigo-500 ring-4 ring-slate-900" />
                  <p className="text-sm font-medium text-slate-300">Data Enriched</p>
                  <p className="text-xs text-slate-500 mt-1 flex items-center gap-1">
                    <Globe className="h-3 w-3" />
                    Via API
                  </p>
                </div>
              )}

              {lead.scores && lead.scores.length > 0 && (
                <div className="relative pl-6">
                  <span className="absolute -left-1.5 top-1 h-3 w-3 rounded-full bg-emerald-500 ring-4 ring-slate-900 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                  <p className="text-sm font-medium text-slate-300">AI Scoring Complete</p>
                  <p className="text-xs text-slate-500 mt-1 flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {format(new Date(lead.updated_at || Date.now()), 'MMM d, h:mm a')}
                  </p>
                </div>
              )}

            </div>
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
    </div>
  );
}
