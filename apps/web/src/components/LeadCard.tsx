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
        'panel transition-all cursor-pointer border border-white/5',
        isExpanded && 'ring-2 ring-white/20'
      )}
      onClick={onClick}
    >
      <div className="p-1">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="font-black text-white text-lg tracking-tight">{lead.company}</h3>
            <p className="text-sm font-bold text-slate-400">
              {lead.first_name} {lead.last_name} • {lead.job_title}
            </p>
            <p className="text-[10px] font-black uppercase tracking-widest text-slate-600 mt-2">{lead.email}</p>
          </div>
          <div className="flex items-center gap-4">
            <ScoreBadge score={score} size="sm" />
            <button
              onClick={(e) => {
                e.stopPropagation();
                setIsExpanded(!isExpanded);
              }}
              className="p-2 hover:bg-white/5 rounded-lg border border-transparent hover:border-white/10 transition-all"
            >
              {isExpanded ? (
                <ChevronUp className="h-4 w-4 text-white" />
              ) : (
                <ChevronDown className="h-4 w-4 text-white" />
              )}
            </button>
          </div>
        </div>

        {isExpanded && (
          <div className="mt-6 pt-6 border-t border-white/5 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white/5 rounded-xl p-4 border border-white/5">
                <h4 className="text-[10px] font-black uppercase tracking-widest text-slate-500 mb-2">
                  Summary
                </h4>
                <p className="text-sm font-medium text-slate-300 leading-relaxed">
                  {lead.composite_score?.overall_summary || 'No summary available'}
                </p>
              </div>
              <div className="bg-white rounded-xl p-4 text-black border border-white/10">
                <h4 className="text-[10px] font-black uppercase tracking-widest text-black/40 mb-2">
                  Action
                </h4>
                <p className="text-sm font-black leading-relaxed">
                  {lead.composite_score?.suggested_action || 'No action suggested'}
                </p>
              </div>
            </div>
            
            {lead.composite_score?.disqualify && (
              <div className="mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
                <p className="text-xs font-black uppercase tracking-widest text-red-500">
                  <strong>Disqualified:</strong> {lead.composite_score.disqualify_reason || 'Low composite score'}
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
