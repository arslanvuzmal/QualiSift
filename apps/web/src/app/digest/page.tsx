'use client';

import { useState } from 'react';
import { Mail, RefreshCw, Send, CheckCircle2 } from 'lucide-react';
import { useDigestHistory } from '@/lib/hooks';
import { generateDigest } from '@/lib/api';
import { toast } from 'sonner';
import { format } from 'date-fns';
import { DataTable, Column } from '@/components/DataTable';

import type { DigestRun } from '@/lib/types';

export default function DigestPage() {
  const { digestRuns, isLoading, mutate } = useDigestHistory();
  const [busy, setBusy] = useState(false);

  const handleGenerate = async () => {
    setBusy(true);
    toast.info('Generating digest...');
    try {
      await generateDigest();
      mutate();
      toast.success('Digest generated and sent.');
    } catch {
      toast.error('Failed to generate digest. Check API logs.');
    } finally {
      setBusy(false);
    }
  };

  const columns: Column<DigestRun>[] = [
    {
      header: 'Run Date',
      accessorKey: 'run_date',
      cell: (run) => (
        <span className="font-medium text-slate-100">
          {format(new Date(run.run_date), 'MMM d, yyyy h:mm a')}
        </span>
      )
    },
    {
      header: 'Total Leads',
      accessorKey: 'total_leads',
      cell: (run) => <span className="font-semibold text-slate-300">{run.total_leads}</span>
    },
    {
      header: 'Hot',
      accessorKey: 'hot_count',
      cell: (run) => <span className="text-rose-400 font-bold">{run.hot_count}</span>
    },
    {
      header: 'Warm',
      accessorKey: 'warm_count',
      cell: (run) => <span className="text-amber-400 font-bold">{run.warm_count}</span>
    },
    {
      header: 'Cold',
      accessorKey: 'cold_count',
      cell: (run) => <span className="text-slate-400 font-semibold">{run.cold_count}</span>
    },
    {
      header: 'Status',
      accessorKey: 'status',
      cell: (run) => (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 capitalize">
          <CheckCircle2 className="h-3 w-3" />
          {run.status}
        </span>
      )
    }
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100">Daily Digest</h1>
          <p className="text-sm text-slate-400 mt-1">
            Track email digests of newly scored and segmented leads.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => mutate()}
            className="btn-secondary"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </button>
          <button
            onClick={handleGenerate}
            disabled={busy}
            className="btn-primary bg-indigo-600 hover:bg-indigo-500"
          >
            <Send className="h-4 w-4 mr-2" />
            {busy ? 'Generating…' : 'Generate & Send Digest'}
          </button>
        </div>
      </div>

      <div className="enterprise-card overflow-hidden">
        {isLoading ? (
          <div className="p-8 space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-12 w-full animate-pulse bg-slate-800 rounded-lg" />
            ))}
          </div>
        ) : digestRuns.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-slate-800 border border-slate-700 mb-4">
              <Mail className="h-8 w-8 text-slate-500" />
            </div>
            <h3 className="text-lg font-medium text-slate-100">No digests found</h3>
            <p className="mt-1 text-sm text-slate-400">Click generate to create your first lead digest.</p>
          </div>
        ) : (
          <DataTable
            data={digestRuns}
            columns={columns}
            keyExtractor={(run) => run.id.toString()}
          />
        )}
      </div>
    </div>
  );
}
