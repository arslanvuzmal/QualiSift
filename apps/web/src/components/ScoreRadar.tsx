'use client';

import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from 'recharts';
import type { CriteriaScore } from '@/lib/types';

interface ScoreRadarProps {
  scores: CriteriaScore[];
  height?: number;
}

export function ScoreRadar({ scores, height = 300 }: ScoreRadarProps) {
  const data = scores.map((score) => ({
    subject: score.criteria_name.replace(/_/g, ' ').toUpperCase(),
    A: score.score,
    fullMark: 10,
    confidence: score.confidence,
  }));

  return (
    <div className="w-full" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
          <PolarGrid stroke="#e2e8f0" />
          <PolarAngleAxis
            dataKey="subject"
            tick={{ fill: '#475569', fontSize: 12 }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 10]}
            tick={{ fill: '#64748b', fontSize: 10 }}
          />
          <Radar
            name="Score"
            dataKey="A"
            stroke="#4f46e5"
            strokeWidth={2}
            fill="#4f46e5"
            fillOpacity={0.3}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
