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
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold text-slate-900">Scoring Criteria</h1>
      <p className="text-slate-600 mt-1 mb-6">
        Tune how much each criterion contributes to a lead&apos;s composite score.
        Weights must sum to <span className="font-medium">1.0</span>.
      </p>

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
