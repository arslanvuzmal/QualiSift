'use client';

import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from 'recharts';
interface ScoreRadarProps {
  scores: { criteria_name: string; score: number; confidence?: number }[];
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
        <RadarChart cx="50%" cy="50%" outerRadius="75%" data={data}>
          <PolarGrid stroke="rgba(255,255,255,0.1)" />
          <PolarAngleAxis
            dataKey="subject"
            tick={{ fill: '#888', fontSize: 9, fontWeight: 900 }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 10]}
            tick={{ fill: '#555', fontSize: 8 }}
            axisLine={false}
          />
          <Radar
            name="Score"
            dataKey="A"
            stroke="#ffffff"
            strokeWidth={2}
            fill="#ffffff"
            fillOpacity={0.15}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
