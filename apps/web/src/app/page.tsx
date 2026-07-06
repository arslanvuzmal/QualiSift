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
} from 'lucide-react';
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

  // score-band distribution for the chart
  const bands = [
    { label: '0–40', color: '#64748b', count: scored.filter((l) => scoreOf(l) < 40).length },
    { label: '40–55', color: '#d97706', count: scored.filter((l) => scoreOf(l) >= 40 && scoreOf(l) < 55).length },
    { label: '55–70', color: '#d97706', count: scored.filter((l) => scoreOf(l) >= 55 && scoreOf(l) < 70).length },
    { label: '70–85', color: '#2563eb', count: scored.filter((l) => scoreOf(l) >= 70 && scoreOf(l) < 85).length },
    { label: '85–100', color: '#dc2626', count: scored.filter((l) => scoreOf(l) >= 85).length },
  ];
  const maxBand = Math.max(1, ...bands.map((b) => b.count));

  const metrics = [
    { key: 'total', label: 'Total Leads', value: meta.total || leads.length, meta: `${scored.length} scored`, cls: 'm-primary', Icon: Users },
    { key: 'hot', label: 'Hot Leads', value: hot, meta: 'score ≥ 75', cls: 'm-danger', Icon: Flame },
    { key: 'warm', label: 'Warm Leads', value: warm, meta: 'score 40–74', cls: 'm-warning', Icon: ThermometerSun },
    { key: 'cold', label: 'Cold Leads', value: cold, meta: 'score < 40', cls: 'm-neutral', Icon: Snowflake },
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
    <div className="space-y-5">
      {/* Page heading */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <span className="flex h-11 w-11 items-center justify-center rounded-lg bg-gradient-to-br from-[#2563eb] to-[#0f766e] text-white">
            <Gauge className="h-5 w-5" />
          </span>
          <div>
            <p className="text-[11px] font-bold uppercase tracking-wide admin-muted">Overview</p>
            <h1 className="text-2xl font-bold" style={{ color: 'var(--admin-text)' }}>Dashboard</h1>
            <p className="admin-muted text-sm">Monitor lead quality, scoring, and pipeline segments in one place.</p>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => mutate()}
            className="inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium hover:bg-admin-soft"
            style={{ borderColor: 'var(--admin-border)', color: 'var(--admin-text)' }}
          >
            <RefreshCw className="h-4 w-4" /> Refresh
          </button>
          <button
            onClick={handleDigest}
            disabled={busy}
            className="inline-flex items-center gap-2 rounded-lg bg-admin-primary px-3 py-2 text-sm font-semibold text-white hover:bg-admin-primaryDark disabled:opacity-50"
          >
            <Mail className="h-4 w-4" /> {busy ? 'Generating…' : 'Generate Digest'}
          </button>
        </div>
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {metrics.map(({ key, label, value, meta: m, cls, Icon }) => (
          <article key={key} className={`metric-card ${cls}`}>
            <div className="flex items-start justify-between">
              <span className="text-[0.78rem] font-extrabold uppercase admin-muted">{label}</span>
              <span className="metric-icon"><Icon className="h-[18px] w-[18px]" /></span>
            </div>
            <div className="mt-4 text-[2.1rem] font-extrabold leading-none" style={{ color: 'var(--admin-text)' }}>
              {isLoading ? '—' : value}
            </div>
            <div className="mt-3 text-sm font-semibold admin-muted">{m}</div>
          </article>
        ))}
      </div>

      {/* Chart + activity */}
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <div className="panel xl:col-span-2">
          <div className="mb-5 flex items-start justify-between">
            <div>
              <h2 className="flex items-center gap-2 text-base font-semibold" style={{ color: 'var(--admin-text)' }}>
                <BarChart3 className="h-[18px] w-[18px] text-admin-primary" /> Score Distribution
              </h2>
              <p className="admin-muted text-sm">How scored leads spread across quality bands.</p>
            </div>
            <span className="text-sm font-semibold admin-muted">avg {avg}</span>
          </div>
          <div
            className="grid items-end gap-4 rounded-lg px-2 pt-4"
            style={{ height: 260, gridTemplateColumns: `repeat(${bands.length}, minmax(0,1fr))`, background: 'linear-gradient(180deg, var(--admin-soft) 0%, var(--admin-surface) 100%)' }}
          >
            {bands.map((b) => (
              <div key={b.label} className="grid h-full grid-rows-[1fr_auto] items-end gap-2 text-center">
                <div className="flex items-end justify-center">
                  <div
                    className="w-full max-w-[46px] rounded-t-md transition-all"
                    style={{ height: `${(b.count / maxBand) * 190 + 6}px`, background: b.color, opacity: b.count ? 1 : 0.25 }}
                    title={`${b.count} leads`}
                  />
                </div>
                <small className="admin-muted">{b.label}<br /><span className="font-semibold">{b.count}</span></small>
              </div>
            ))}
          </div>
        </div>

        <div className="panel">
          <div className="mb-5">
            <h2 className="flex items-center gap-2 text-base font-semibold" style={{ color: 'var(--admin-text)' }}>
              <Activity className="h-[18px] w-[18px] text-admin-success" /> Pipeline Segments
            </h2>
            <p className="admin-muted text-sm">Live breakdown of qualified leads.</p>
          </div>
          <ul className="space-y-4">
            {[
              { dot: '#dc2626', label: 'Hot', desc: 'Ready to engage now', count: hot },
              { dot: '#d97706', label: 'Warm', desc: 'Nurture and follow up', count: warm },
              { dot: '#64748b', label: 'Cold', desc: 'Low priority for now', count: cold },
            ].map((s) => (
              <li key={s.label} className="flex items-center gap-3">
                <span className="mt-1 h-2.5 w-2.5 shrink-0 rounded-full" style={{ background: s.dot }} />
                <div className="flex-1">
                  <p className="text-sm font-semibold" style={{ color: 'var(--admin-text)' }}>{s.label}</p>
                  <p className="admin-muted text-xs">{s.desc}</p>
                </div>
                <span className="text-lg font-bold" style={{ color: 'var(--admin-text)' }}>{s.count}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Leads table */}
      <div className="panel">
        <div className="mb-4 flex items-start justify-between">
          <div>
            <h2 className="flex items-center gap-2 text-base font-semibold" style={{ color: 'var(--admin-text)' }}>
              <Users className="h-[18px] w-[18px] text-admin-primary" /> Recent Leads
            </h2>
            <p className="admin-muted text-sm">Latest scored leads across the workspace.</p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[720px] border-collapse text-sm">
            <thead>
              <tr className="border-b text-left" style={{ borderColor: 'var(--admin-border)' }}>
                {['Lead', 'Company', 'Score', 'Segment', 'Status', ''].map((h) => (
                  <th key={h} className="px-3 py-3 text-[11px] font-bold uppercase tracking-wide admin-muted">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr><td colSpan={6} className="px-3 py-8 text-center admin-muted">Loading leads…</td></tr>
              ) : leads.length === 0 ? (
                <tr><td colSpan={6} className="px-3 py-8 text-center admin-muted">No leads yet.</td></tr>
              ) : (
                leads.map((lead) => {
                  const score = scoreOf(lead);
                  const seg = segment(score);
                  return (
                    <tr key={lead.id} className="border-b last:border-0" style={{ borderColor: 'var(--admin-border)' }}>
                      <td className="px-3 py-3">
                        <Link href={`/leads/${lead.id}`} className="flex items-center gap-3 group">
                          <span className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-[#2563eb] to-[#0f766e] text-[11px] font-bold text-white">
                            {initials(lead)}
                          </span>
                          <span className="leading-tight">
                            <span className="block font-semibold group-hover:text-admin-primary" style={{ color: 'var(--admin-text)' }}>
                              {lead.first_name} {lead.last_name}
                            </span>
                            <span className="block text-xs admin-muted">{lead.email}</span>
                          </span>
                        </Link>
                      </td>
                      <td className="px-3 py-3">
                        <p className="font-medium" style={{ color: 'var(--admin-text)' }}>{lead.company}</p>
                        <p className="text-xs admin-muted">{lead.job_title}</p>
                      </td>
                      <td className="px-3 py-3 font-bold" style={{ color: 'var(--admin-text)' }}>
                        {lead.composite_score ? Math.round(score) : '—'}
                      </td>
                      <td className="px-3 py-3">
                        <span className={`badge-admin ${seg === 'hot' ? 'badge-hot' : seg === 'warm' ? 'badge-warm' : 'badge-cold'}`}>
                          {seg.charAt(0).toUpperCase() + seg.slice(1)}
                        </span>
                      </td>
                      <td className="px-3 py-3">
                        <span className={`badge-admin ${lead.status === 'scored' ? 'badge-ok' : lead.status === 'disqualified' ? 'badge-hot' : 'badge-neutral'}`}>
                          {lead.status}
                        </span>
                      </td>
                      <td className="px-3 py-3 text-right">
                        <Link
                          href={`/leads/${lead.id}`}
                          className="rounded-md border px-2.5 py-1 text-xs font-medium hover:bg-admin-soft"
                          style={{ borderColor: 'var(--admin-border)', color: 'var(--admin-text)' }}
                        >
                          View
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
          <div className="mt-4 flex items-center justify-between text-sm">
            <span className="admin-muted">Page {meta.page} of {meta.total_pages}</span>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="rounded-md border px-3 py-1 disabled:opacity-50"
                style={{ borderColor: 'var(--admin-border)', color: 'var(--admin-text)' }}
              >
                Previous
              </button>
              <button
                onClick={() => setPage((p) => Math.min(meta.total_pages, p + 1))}
                disabled={page >= meta.total_pages}
                className="rounded-md border px-3 py-1 disabled:opacity-50"
                style={{ borderColor: 'var(--admin-border)', color: 'var(--admin-text)' }}
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
