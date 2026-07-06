'use client';

import { useState } from 'react';
import Link from 'next/link';
import { RefreshCw, Mail } from 'lucide-react';
import { useLeads } from '@/lib/hooks';
import { ScoreBadge } from '@/components/ScoreBadge';
import { generateDigest } from '@/lib/api';

export default function Dashboard() {
  const [page, setPage] = useState(1);
  const { leads, meta, isLoading, mutate } = useLeads(page, 20);
  const [isGeneratingDigest, setIsGeneratingDigest] = useState(false);

  const handleRefresh = () => {
    mutate();
  };

  const handleGenerateDigest = async () => {
    setIsGeneratingDigest(true);
    try {
      await generateDigest();
      alert('Digest generated successfully!');
    } catch (error) {
      console.error('Failed to generate digest:', error);
      alert('Failed to generate digest. Check console for details.');
    } finally {
      setIsGeneratingDigest(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-500">Loading leads...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
          <p className="text-slate-600 mt-1">
            View and manage your scored leads
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleRefresh}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
          <button
            onClick={handleGenerateDigest}
            disabled={isGeneratingDigest}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
          >
            <Mail className="h-4 w-4" />
            {isGeneratingDigest ? 'Generating...' : 'Generate Digest'}
          </button>
        </div>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-4 rounded-lg border">
          <p className="text-sm text-slate-600">Total Leads</p>
          <p className="text-2xl font-bold text-slate-900">
            {meta?.total || leads.length}
          </p>
        </div>
        <div className="bg-rose-50 p-4 rounded-lg border border-rose-200">
          <p className="text-sm text-rose-600">Hot Leads</p>
          <p className="text-2xl font-bold text-rose-800">
            {leads.filter((l) => (l.composite_score?.composite_score || 0) >= 75).length}
          </p>
        </div>
        <div className="bg-amber-50 p-4 rounded-lg border border-amber-200">
          <p className="text-sm text-amber-600">Warm Leads</p>
          <p className="text-2xl font-bold text-amber-800">
            {leads.filter((l) => {
              const score = l.composite_score?.composite_score || 0;
              return score >= 40 && score < 75;
            }).length}
          </p>
        </div>
        <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
          <p className="text-sm text-slate-600">Cold Leads</p>
          <p className="text-2xl font-bold text-slate-800">
            {leads.filter((l) => (l.composite_score?.composite_score || 0) < 40).length}
          </p>
        </div>
      </div>

      {/* Leads Table */}
      <div className="bg-white border rounded-lg overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-50 border-b">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Contact
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Company
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Score
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {leads.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-4 py-8 text-center text-slate-500">
                  No leads found. Add leads to get started.
                </td>
              </tr>
            ) : (
              leads.map((lead) => (
                <tr key={lead.id} className="hover:bg-slate-50">
                  <td className="px-4 py-4">
                    <Link href={`/leads/${lead.id}`} className="block group">
                      <p className="font-medium text-slate-900 group-hover:text-indigo-600">
                        {lead.first_name} {lead.last_name}
                      </p>
                      <p className="text-sm text-slate-500">{lead.email}</p>
                    </Link>
                  </td>
                  <td className="px-4 py-4">
                    <div>
                      <p className="font-medium text-slate-900">{lead.company}</p>
                      <p className="text-sm text-slate-500">{lead.job_title}</p>
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <ScoreBadge
                      score={lead.composite_score?.composite_score || 0}
                      size="sm"
                    />
                  </td>
                  <td className="px-4 py-4">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-800 capitalize">
                      {lead.status}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {meta && meta.total_pages > 1 && (
        <div className="flex items-center justify-between mt-4">
          <p className="text-sm text-slate-600">
            Showing page {page} of {meta.total_pages}
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-3 py-1 border rounded disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => setPage((p) => Math.min(meta.total_pages, p + 1))}
              disabled={page === meta.total_pages}
              className="px-3 py-1 border rounded disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
