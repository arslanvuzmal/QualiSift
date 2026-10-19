'use client';

import { useState } from 'react';
import Link from 'next/link';
import {
  MoreHorizontal,
  Mail,
  Upload,
  Users,
  Flame,
  ThermometerSun,
  Snowflake,
  Inbox,
} from 'lucide-react';
import { useLeads, useDigestHistory } from '@/lib/hooks';
import { createLead, generateDigest } from '@/lib/api';
import { parseCsv, toLead } from '@/lib/csv';
import type { Lead } from '@/lib/types';
import { toast } from 'sonner';
import { format } from 'date-fns';
import { DataTable, Column } from '@/components/DataTable';
import { ScoreBadge } from '@/components/ScoreBadge';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

export default function Dashboard() {
  const [page, setPage] = useState(1);
  const { leads, meta, isLoading, mutate } = useLeads(page, 20);
  const { digestRuns } = useDigestHistory();
  const [busy, setBusy] = useState(false);
  const [importing, setImporting] = useState(false);

  const scored = leads.filter((l) => l.composite_score);
  const hot = scored.filter((l) => (l.composite_score?.composite_score ?? 0) >= 75).length;
  const warm = scored.filter((l) => {
    const s = l.composite_score?.composite_score ?? 0;
    return s >= 40 && s < 75;
  }).length;
  const cold = scored.filter((l) => (l.composite_score?.composite_score ?? 0) < 40).length;

  // Each row becomes POST /leads; the API enriches and scores it in the background, and the
  // table picks it up on its 5-second refresh.
  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = '';
    if (!file) return;
    setImporting(true);
    try {
      const rows = parseCsv(await file.text()).filter((r) => r.email);
      let created = 0;
      for (const row of rows) {
        try {
          await createLead(toLead(row));
          created++;
        } catch {
          // A bad row (e.g. invalid email) should not stop the rest.
        }
      }
      await mutate();
      if (created === rows.length) toast.success(`Imported ${created} lead${created === 1 ? '' : 's'}; scoring has started.`);
      else toast.warning(`Imported ${created} of ${rows.length} rows; check the others for a valid email.`);
    } catch {
      toast.error('Could not read that file as CSV.');
    } finally {
      setImporting(false);
    }
  };

  const handleDigest = async () => {
    setBusy(true);
    try {
      await generateDigest();
      toast.success('Digest generated successfully.');
    } catch {
      toast.error('Failed to generate digest.');
    } finally {
      setBusy(false);
    }
  };

  const columns: Column<Lead>[] = [
    {
      header: 'Lead / Company',
      accessorKey: 'first_name',
      cell: (lead) => {
        const initials = ((lead.first_name?.[0] ?? '') + (lead.last_name?.[0] ?? '')).toUpperCase() || 'L';
        return (
          <div className="flex items-center gap-3">
            <span className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-800 border border-slate-700 text-xs font-semibold text-slate-300">
              {initials}
            </span>
            <div>
              <p className="font-semibold text-slate-100">
                {lead.first_name} {lead.last_name}
              </p>
              <p className="text-xs text-slate-500">{lead.company}</p>
            </div>
          </div>
        );
      },
    },
    {
      header: 'Job Title',
      accessorKey: 'job_title',
      cell: (lead) => <span className="text-slate-400">{lead.job_title || '—'}</span>,
    },
    {
      header: 'Composite Score',
      accessorKey: 'id',
      cell: (lead) => <ScoreBadge score={lead.composite_score?.composite_score ?? null} />,
    },
    {
      header: 'Status',
      accessorKey: 'status',
      cell: (lead) => (
        <span className="capitalize text-slate-400 font-medium">
          {lead.status}
        </span>
      ),
    },
    {
      header: 'Last Updated',
      accessorKey: 'updated_at',
      cell: (lead) => (
        <span className="text-slate-500">
          {lead.updated_at ? format(new Date(lead.updated_at), 'MMM d, yyyy') : '—'}
        </span>
      ),
    },
    {
      header: '',
      cell: (lead) => (
        <div className="flex justify-end">
          <Link
            href={`/leads/${lead.id}`}
            onClick={(e) => e.stopPropagation()}
            className="p-2 text-slate-500 hover:text-slate-300 rounded-lg hover:bg-slate-800 transition-colors"
          >
            <MoreHorizontal className="h-4 w-4" />
          </Link>
        </div>
      ),
    },
  ];

  // Prepare chart data
  const chartData = [...digestRuns].reverse().map(run => ({
    date: format(new Date(run.run_date), 'MMM d'),
    leads: run.total_leads,
    hot: run.hot_count,
    warm: run.warm_count,
    cold: run.cold_count
  }));

  const scoreDist = [
    { name: 'Cold (0-39)', value: cold, fill: '#64748b' },
    { name: 'Warm (40-74)', value: '#f59e0b', fill: '#f59e0b' },
    { name: 'Hot (75-100)', value: hot, fill: '#f43f5e' }
  ];

  // Correct the warm value mapping
  scoreDist[1].value = warm;

  return (
    <div className="space-y-8 max-w-[1400px] mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100">Pipeline Overview</h1>
          <p className="text-sm text-slate-500 mt-1">Your AI-qualified leads for today.</p>
        </div>
        <div className="flex items-center gap-3">
          <label className={`btn-secondary cursor-pointer ${importing ? 'opacity-60' : ''}`}>
            <Upload className="h-4 w-4 mr-2" />
            {importing ? 'Importing…' : 'Import CSV'}
            <input type="file" accept=".csv,text/csv" className="sr-only" disabled={importing} onChange={handleImport} />
          </label>
          <button
            onClick={handleDigest}
            disabled={busy}
            className="btn-primary"
          >
            <Mail className="h-4 w-4 mr-2" />
            {busy ? 'Generating…' : 'Generate Digest'}
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: 'Total Leads', value: meta.total || leads.length, icon: Users, color: 'text-indigo-400', bg: 'bg-indigo-500/10' },
          { label: 'Hot Leads', value: hot, icon: Flame, color: 'text-rose-400', bg: 'bg-rose-500/10' },
          { label: 'Warm Leads', value: warm, icon: ThermometerSun, color: 'text-amber-400', bg: 'bg-amber-500/10' },
          { label: 'Cold Leads', value: cold, icon: Snowflake, color: 'text-slate-400', bg: 'bg-slate-800' },
        ].map((stat, i) => (
          <div key={i} className="enterprise-card bg-slate-900/50 backdrop-blur p-6 border-slate-800">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-400">{stat.label}</span>
              <span className={`flex h-10 w-10 items-center justify-center rounded-lg ${stat.bg} ${stat.color} border border-white/5`}>
                <stat.icon className="h-5 w-5" />
              </span>
            </div>
            <div className="mt-4 flex items-baseline gap-2">
              <span className="text-3xl font-bold tracking-tight text-slate-100">
                {isLoading ? '—' : stat.value}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Analytics Charts */}
      {digestRuns.length > 0 && (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 enterprise-card bg-slate-900/50 backdrop-blur p-6 border-slate-800">
          <h3 className="text-sm font-semibold text-slate-400 mb-6">Leads Processed (Last 30 Days)</h3>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                <defs>
                  <linearGradient id="colorLeads" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="#1e293b" vertical={false} />
                <XAxis dataKey="date" stroke="#475569" tick={{fill: '#64748b', fontSize: 12}} tickLine={false} axisLine={false} />
                <YAxis stroke="#475569" tick={{fill: '#64748b', fontSize: 12}} tickLine={false} axisLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', color: '#f1f5f9' }}
                  itemStyle={{ color: '#818cf8' }}
                />
                <Line type="monotone" dataKey="leads" stroke="#6366f1" strokeWidth={3} dot={false} activeDot={{ r: 6, fill: '#818cf8', stroke: '#312e81', strokeWidth: 2 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="enterprise-card bg-slate-900/50 backdrop-blur p-6 border-slate-800">
          <h3 className="text-sm font-semibold text-slate-400 mb-6">Score Distribution</h3>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={scoreDist} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                <CartesianGrid stroke="#1e293b" vertical={false} />
                <XAxis dataKey="name" stroke="#475569" tick={{fill: '#64748b', fontSize: 12}} tickLine={false} axisLine={false} />
                <Tooltip 
                  cursor={{fill: '#1e293b'}}
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', color: '#f1f5f9' }}
                />
                <Bar dataKey="value" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      )}

      {/* Data Table Area */}
      <div className="enterprise-card overflow-hidden bg-slate-900 border-slate-800">
        {isLoading ? (
          <div className="p-8 space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-12 w-full animate-pulse bg-slate-800 rounded-lg" />
            ))}
          </div>
        ) : leads.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-24 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-slate-800 mb-4 border border-slate-700">
              <Inbox className="h-8 w-8 text-slate-500" />
            </div>
            <h3 className="text-lg font-medium text-slate-100">No leads found</h3>
            <p className="mt-1 text-sm text-slate-500">Send your first webhook to start qualifying leads.</p>
            <button className="mt-6 btn-primary">
              View API Docs
            </button>
          </div>
        ) : (
          <DataTable
            data={leads}
            columns={columns}
            keyExtractor={(l) => l.id.toString()}
            renderExpandedRow={(lead) => (
              <div className="p-6 bg-slate-950 border-t border-slate-800">
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">AI Summary</h4>
                    <p className="text-sm text-slate-300 leading-relaxed">
                      {lead.composite_score?.overall_summary || 'No AI summary available for this lead yet.'}
                    </p>
                  </div>
                  <div>
                    <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Suggested Action</h4>
                    <div className="rounded-lg bg-amber-500/10 border border-amber-500/20 p-3 shadow-[0_0_10px_rgba(251,191,36,0.1)]">
                      <p className="text-sm font-medium text-amber-400">
                        {lead.composite_score?.suggested_action || 'Nurture via email campaign.'}
                      </p>
                    </div>
                    <div className="mt-3 flex gap-2">
                      <Link href={`/leads/${lead.id}`} className="text-sm font-medium text-indigo-400 hover:text-indigo-300">
                        View full details &rarr;
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            )}
          />
        )}
        
        {/* Pagination footer */}
        {meta.total_pages > 1 && (
          <div className="border-t border-slate-800 px-6 py-4 flex items-center justify-between bg-slate-900">
            <span className="text-sm text-slate-500">
              Showing page {meta.page} of {meta.total_pages}
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="btn-secondary px-3 py-1.5"
              >
                Previous
              </button>
              <button
                onClick={() => setPage((p) => Math.min(meta.total_pages, p + 1))}
                disabled={page >= meta.total_pages}
                className="btn-secondary px-3 py-1.5"
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
