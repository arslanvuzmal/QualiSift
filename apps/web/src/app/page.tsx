'use client';

import { useState } from 'react';
import Link from 'next/link';
import {
  RefreshCw,
  Mail,
  Users,
  Flame,
  ThermometerSun,
  Snowflake,
  Gauge,
  BarChart3,
  Activity,
  ArrowRight,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  PieChart,
  Pie,
} from 'recharts';
import { useLeads } from '@/lib/hooks';
import { generateDigest } from '@/lib/api';
import type { Lead } from '@/lib/types';

function scoreOf(l: Lead) {
  return l.composite_score?.composite_score ?? 0;
}
function segment(score: number): 'hot' | 'warm' | 'cold' {
  if (score >= 75) return 'hot';
  if (score >= 40) return 'warm';
  return 'cold';
}
function initials(l: Lead) {
  const a = (l.first_name?.[0] ?? '').toUpperCase();
  const b = (l.last_name?.[0] ?? l.company?.[0] ?? '').toUpperCase();
  return (a + b) || 'L';
}

export default function Dashboard() {
  const [page, setPage] = useState(1);
  const { leads, meta, isLoading, mutate } = useLeads(page, 20);
  const [busy, setBusy] = useState(false);

  const scored = leads.filter((l) => l.composite_score);
  const hot = scored.filter((l) => scoreOf(l) >= 75).length;
  const warm = scored.filter((l) => scoreOf(l) >= 40 && scoreOf(l) < 75).length;
  const cold = scored.filter((l) => scoreOf(l) < 40).length;
  const avg = scored.length ? Math.round(scored.reduce((s, l) => s + scoreOf(l), 0) / scored.length) : 0;

  // score-band distribution for the chart - 3D Dark Grey palette
  const bands = [
    { name: '0–40', count: scored.filter((l) => scoreOf(l) < 40).length, color: '#333333' },
    { name: '40–55', count: scored.filter((l) => scoreOf(l) >= 40 && scoreOf(l) < 55).length, color: '#555555' },
    { name: '55–70', count: scored.filter((l) => scoreOf(l) >= 55 && scoreOf(l) < 70).length, color: '#777777' },
    { name: '70–85', count: scored.filter((l) => scoreOf(l) >= 70 && scoreOf(l) < 85).length, color: '#999999' },
    { name: '85–100', count: scored.filter((l) => scoreOf(l) >= 85).length, color: '#ffffff' },
  ];

  const pieData = [
    { name: 'Hot', value: hot, color: '#ffffff' },
    { name: 'Warm', value: warm, color: '#888888' },
    { name: 'Cold', value: cold, color: '#444444' },
  ].filter(d => d.value > 0);

  const metrics = [
    { key: 'total', label: 'Total Leads', value: meta.total || leads.length, meta: `${scored.length} scored`, cls: 'm-primary', Icon: Users, trend: '+12% from last week' },
    { key: 'hot', label: 'Hot Leads', value: hot, meta: 'score ≥ 75', cls: 'm-danger', Icon: Flame, trend: '+5% vs avg' },
    { key: 'warm', label: 'Warm Leads', value: warm, meta: 'score 40–74', cls: 'm-warning', Icon: ThermometerSun, trend: 'Stable' },
    { key: 'cold', label: 'Cold Leads', value: cold, meta: 'score < 40', cls: 'm-neutral', Icon: Snowflake, trend: '-2% vs avg' },
  ];

  const handleDigest = async () => {
    setBusy(true);
    try {
      await generateDigest();
      alert('Digest generated.');
    } catch {
      alert('Failed to generate digest.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page heading */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex items-start gap-4">
          <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-[#333] to-[#000] text-white shadow-[0_0_15px_rgba(255,255,255,0.1)] border border-white/10">
            <Gauge className="h-6 w-6" />
          </span>
          <div>
            <p className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">Overview</p>
            <h1 className="text-3xl font-black tracking-tighter" style={{ color: 'var(--admin-text)' }}>Dashboard</h1>
            <p className="admin-muted text-sm font-medium">Monitor lead quality and pipeline segments in 3D depth.</p>
          </div>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => mutate()}
            className="inline-flex h-11 items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 text-sm font-bold text-white hover:bg-white/10 transition-all shadow-sm"
          >
            <RefreshCw className="h-4 w-4" /> Refresh
          </button>
          <button
            onClick={handleDigest}
            disabled={busy}
            className="inline-flex h-11 items-center gap-2 rounded-xl bg-white px-5 text-sm font-black text-black hover:bg-slate-200 disabled:opacity-50 transition-all shadow-[0_0_20px_rgba(255,255,255,0.2)]"
          >
            <Mail className="h-4 w-4" /> {busy ? 'Generating…' : 'Generate Digest'}
          </button>
        </div>
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {metrics.map(({ key, label, value, meta: m, cls, Icon, trend }) => (
          <article key={key} className={`metric-card group ${cls}`}>
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[0.72rem] font-bold uppercase tracking-widest admin-muted">{label}</span>
                <div className="mt-1 text-3xl font-black tracking-tighter text-white">
                  {isLoading ? '—' : value}
                </div>
              </div>
              <span className="metric-icon transition-transform group-hover:scale-110 group-hover:rotate-3"><Icon className="h-5 w-5" /></span>
            </div>
            <div className="mt-4 flex items-center justify-between">
              <div className="text-[11px] font-bold admin-muted">{m}</div>
              <div className="text-[10px] font-black text-emerald-500 opacity-0 transition-opacity group-hover:opacity-100">{trend}</div>
            </div>
            <div className="absolute bottom-0 left-0 h-1 w-0 bg-white opacity-20 transition-all group-hover:w-full" />
          </article>
        ))}
      </div>

      {/* Chart + activity */}
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <div className="panel xl:col-span-2">
          <div className="mb-6 flex items-start justify-between">
            <div>
              <h2 className="flex items-center gap-2 text-lg font-black tracking-tight text-white">
                <BarChart3 className="h-5 w-5 text-slate-400" /> Score Distribution
              </h2>
              <p className="admin-muted text-xs font-bold uppercase tracking-wider">Quality Banding</p>
            </div>
            <div className="text-right">
              <span className="block text-2xl font-black text-white">{avg}</span>
              <span className="block text-[10px] font-black uppercase tracking-tighter admin-muted">Avg Score</span>
            </div>
          </div>
          <div className="h-[280px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={bands} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                <XAxis
                  dataKey="name"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: 'var(--admin-muted)', fontSize: 10, fontWeight: 800 }}
                  dy={10}
                />
                <YAxis hide domain={[0, 'dataMax + 2']} />
                <Tooltip
                  cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      return (
                        <div className="rounded-xl border border-white/10 bg-black/90 backdrop-blur-md p-3 shadow-2xl">
                          <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">{payload[0].payload.name}</p>
                          <p className="text-sm font-black text-white">{payload[0].value} leads</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar dataKey="count" radius={[6, 6, 0, 0]} barSize={44}>
                  {bands.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="panel">
          <div className="mb-6">
            <h2 className="flex items-center gap-2 text-lg font-black tracking-tight text-white">
              <Activity className="h-5 w-5 text-emerald-500" /> Segments
            </h2>
            <p className="admin-muted text-xs font-bold uppercase tracking-wider">Lead Breakdown</p>
          </div>

          <div className="flex h-[150px] items-center justify-center">
            {pieData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={70}
                    paddingAngle={8}
                    dataKey="value"
                    stroke="none"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        return (
                          <div className="rounded-xl border border-white/10 bg-black/90 backdrop-blur-md p-2 shadow-2xl text-[10px] font-black uppercase tracking-widest text-white">
                            {payload[0].name}: {payload[0].value}
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-xs font-bold uppercase tracking-widest admin-muted">No data</div>
            )}
          </div>

          <ul className="mt-4 space-y-3">
            {[
              { dot: '#ffffff', label: 'Hot', desc: 'Engage Now', count: hot },
              { dot: '#888888', label: 'Warm', desc: 'Nurture', count: warm },
              { dot: '#444444', label: 'Cold', desc: 'Backlog', count: cold },
            ].map((s) => (
              <li key={s.label} className="flex items-center justify-between rounded-xl bg-white/5 p-3 transition-all hover:bg-white/10 hover:translate-x-1">
                <div className="flex items-center gap-3">
                  <span className="h-2 w-2 rounded-full shadow-[0_0_8px_rgba(255,255,255,0.5)]" style={{ background: s.dot }} />
                  <div>
                    <p className="text-xs font-black text-white uppercase tracking-tight">{s.label}</p>
                    <p className="text-[9px] font-bold uppercase tracking-widest text-slate-500">{s.desc}</p>
                  </div>
                </div>
                <span className="text-sm font-black text-white">{s.count}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Leads table */}
      <div className="panel overflow-hidden">
        <div className="mb-6 flex items-start justify-between">
          <div>
            <h2 className="flex items-center gap-2 text-lg font-black tracking-tight text-white">
              <Users className="h-5 w-5 text-slate-400" /> Recent Leads
            </h2>
            <p className="admin-muted text-xs font-bold uppercase tracking-wider">Latest Scoring Results</p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[720px] border-collapse text-sm">
            <thead>
              <tr className="text-left border-b border-white/5">
                {['Lead', 'Company', 'Score', 'Segment', 'Status', ''].map((h) => (
                  <th key={h} className="px-4 py-4 text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {isLoading ? (
                <tr><td colSpan={6} className="px-4 py-16 text-center admin-muted font-bold uppercase tracking-widest">Loading...</td></tr>
              ) : leads.length === 0 ? (
                <tr><td colSpan={6} className="px-4 py-16 text-center admin-muted font-bold uppercase tracking-widest">Empty</td></tr>
              ) : (
                leads.map((lead) => {
                  const score = scoreOf(lead);
                  const seg = segment(score);
                  return (
                    <tr key={lead.id} className="group transition-colors hover:bg-white/[0.02]">
                      <td className="px-4 py-5">
                        <Link href={`/leads/${lead.id}`} className="flex items-center gap-4">
                          <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-[#444] to-[#000] text-[10px] font-black text-white shadow-xl border border-white/10 transition-transform group-hover:scale-110">
                            {initials(lead)}
                          </span>
                          <div className="min-w-0 flex-1">
                            <span className="block truncate text-sm font-black tracking-tight text-white group-hover:text-white transition-colors">
                              {lead.first_name} {lead.last_name}
                            </span>
                            <span className="block truncate text-[11px] font-bold text-slate-500">{lead.email}</span>
                          </div>
                        </Link>
                      </td>
                      <td className="px-4 py-5">
                        <p className="truncate text-sm font-black text-slate-200">{lead.company}</p>
                        <p className="truncate text-[10px] font-bold uppercase tracking-wider text-slate-500">{lead.job_title}</p>
                      </td>
                      <td className="px-4 py-5">
                        <span className="text-lg font-black text-white">
                          {lead.composite_score ? Math.round(score) : '—'}
                        </span>
                        <span className="ml-1 text-[10px] font-black text-slate-600">/100</span>
                      </td>
                      <td className="px-4 py-5">
                        <span className={`badge-admin uppercase tracking-tighter ${seg === 'hot' ? 'badge-hot' : seg === 'warm' ? 'badge-warm' : 'badge-cold'}`}>
                          {seg}
                        </span>
                      </td>
                      <td className="px-4 py-5">
                        <span className={`badge-admin uppercase tracking-tighter ${lead.status === 'scored' ? 'badge-ok' : lead.status === 'disqualified' ? 'badge-hot' : 'badge-neutral'}`}>
                          {lead.status}
                        </span>
                      </td>
                      <td className="px-4 py-5 text-right">
                        <Link
                          href={`/leads/${lead.id}`}
                          className="inline-flex h-9 w-9 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-slate-400 transition-all hover:border-white/40 hover:text-white hover:shadow-[0_0_15px_rgba(255,255,255,0.1)]"
                        >
                          <ArrowRight className="h-4 w-4" />
                        </Link>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {meta.total_pages > 1 && (
          <div className="mt-6 flex items-center justify-between px-4 pb-4">
            <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">Page {meta.page} of {meta.total_pages}</span>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="rounded-lg border border-white/10 px-4 py-2 text-xs font-black uppercase tracking-widest text-white disabled:opacity-30"
              >
                Prev
              </button>
              <button
                onClick={() => setPage((p) => Math.min(meta.total_pages, p + 1))}
                disabled={page >= meta.total_pages}
                className="rounded-lg border border-white/10 px-4 py-2 text-xs font-black uppercase tracking-widest text-white disabled:opacity-30"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
