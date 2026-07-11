'use client';

import { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ScoreBadge } from './ScoreBadge';
import type { Lead } from '@/lib/types';

interface LeadCardProps {
  lead: Lead;
  onClick?: () => void;
}

export function LeadCard({ lead, onClick }: LeadCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const score = lead.composite_score?.composite_score || 0;

  return (
    <div
      className={cn(
        'border border-slate-800 rounded-lg bg-slate-900 shadow-sm hover:shadow-md transition-shadow cursor-pointer',
        isExpanded && 'ring-2 ring-indigo-500'
      )}
      onClick={onClick}
    >
      <div className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="font-semibold text-slate-100">{lead.company}</h3>
            <p className="text-sm text-slate-400">
              {lead.first_name} {lead.last_name} • {lead.job_title}
            </p>
            <p className="text-xs text-slate-500 mt-1">{lead.email}</p>
          </div>
          <div className="flex items-center gap-3">
            <ScoreBadge score={score} />
            <button
              onClick={(e) => {
                e.stopPropagation();
                setIsExpanded(!isExpanded);
              }}
              className="p-1 hover:bg-slate-800 rounded"
            >
              {isExpanded ? (
                <ChevronUp className="h-4 w-4 text-slate-400" />
              ) : (
                <ChevronDown className="h-4 w-4 text-slate-400" />
              )}
            </button>
          </div>
        </div>

        {isExpanded && (
          <div className="mt-4 pt-4 border-t border-slate-800">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h4 className="text-sm font-medium text-slate-300 mb-2">
                  Summary
                </h4>
                <p className="text-sm text-slate-400">
                  {lead.composite_score?.overall_summary || 'No summary available'}
                </p>
              </div>
              <div>
                <h4 className="text-sm font-medium text-slate-300 mb-2">
                  Suggested Action
                </h4>
                <p className="text-sm text-slate-400">
                  {lead.composite_score?.suggested_action || 'No action suggested'}
                </p>
              </div>
            </div>
            
            {lead.composite_score?.disqualify && (
              <div className="mt-3 p-3 bg-rose-500/10 border border-rose-500/20 rounded">
                <p className="text-sm text-rose-400">
                  <strong className="text-rose-300">Disqualified:</strong> {lead.composite_score.disqualify_reason || 'Low composite score'}
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
