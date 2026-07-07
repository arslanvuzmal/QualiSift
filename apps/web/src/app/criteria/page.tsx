'use client';

import { useState } from 'react';
import { useCriteria } from '@/lib/hooks';
import { CriteriaEditor } from '@/components/CriteriaEditor';
import { updateCriteria } from '@/lib/api';
import type { CriteriaConfig } from '@/lib/types';

export default function CriteriaPage() {
  const { criteria, isLoading, mutate } = useCriteria();
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleSave = async (updated: CriteriaConfig[]) => {
    setSaving(true);
    setMessage(null);
    try {
      await Promise.all(
        updated.map((c) => updateCriteria(c.id, { weight: c.weight }))
      );
      setMessage('Weights saved. New leads will be scored with these weights.');
      mutate();
    } catch (err) {
      console.error(err);
      setMessage('Failed to save weights. Check that the API is running.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-2xl space-y-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-3xl font-black tracking-tighter text-white">Scoring Criteria</h1>
        <p className="admin-muted text-sm font-medium">
          Tune how much each criterion contributes to a lead&apos;s composite score.
          Weights must sum to <span className="text-white font-black">1.0</span>.
        </p>
      </div>

      {isLoading ? (
        <p className="text-slate-500">Loading criteria…</p>
      ) : (
        <CriteriaEditor criteria={criteria} onSave={handleSave} />
      )}

      {message && (
        <p className="mt-3 text-sm text-slate-600">
          {saving ? 'Saving…' : message}
        </p>
      )}
    </div>
  );
}
