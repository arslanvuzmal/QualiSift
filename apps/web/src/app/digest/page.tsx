'use client';

import { useState } from 'react';
import { Mail, RefreshCw } from 'lucide-react';
import { useDigestHistory } from '@/lib/hooks';
import { generateDigest } from '@/lib/api';

export default function DigestPage() {
  const { digestRuns, isLoading, mutate } = useDigestHistory();
  const [busy, setBusy] = useState(false);

  const handleGenerate = async () => {
    setBusy(true);
    try {
      await generateDigest();
      mutate();
    } catch (err) {
      console.error(err);
      alert('Failed to generate digest. Check the API logs.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Daily Digest</h1>
          <p className="text-slate-600 mt-1">
            Segments recently scored leads into Hot / Warm / Cold and records each run.
          </p>
        </div>
        <button
          onClick={handleGenerate}
          disabled={busy}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
        >
          <Mail className="h-4 w-4" />
          {busy ? 'Generating…' : 'Generate Digest'}
        </button>
      </div>

      <div className="bg-white border rounded-lg overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-50 border-b">
            <tr>
              {['Run date', 'Total', 'Hot', 'Warm', 'Cold', 'Status'].map((h) => (
                <th
                  key={h}
                  className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {isLoading ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-slate-500">
                  Loading…
                </td>
              </tr>
            ) : digestRuns.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-slate-500">
                  No digests yet. Click “Generate Digest” to create one.
                </td>
              </tr>
            ) : (
              digestRuns.map((run) => (
                <tr key={run.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 text-sm text-slate-700">
                    {new Date(run.run_date).toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-900 font-medium">
                    {run.total_leads}
                  </td>
                  <td className="px-4 py-3 text-sm text-rose-700 font-medium">
                    {run.hot_count}
                  </td>
                  <td className="px-4 py-3 text-sm text-amber-700 font-medium">
                    {run.warm_count}
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-600">{run.cold_count}</td>
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 capitalize">
                      {run.status}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <button
        onClick={() => mutate()}
        className="mt-4 flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900"
      >
        <RefreshCw className="h-4 w-4" />
        Refresh history
      </button>
    </div>
  );
}
