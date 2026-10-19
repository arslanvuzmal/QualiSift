'use client';
import React from 'react';
import dynamic from 'next/dynamic';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from 'recharts';

interface ScoreRadarProps {
  data: {
    subject: string;
    score: number;
    fullMark: number;
  }[];
}

function ScoreRadarComponent({ data }: ScoreRadarProps) {
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="75%" data={data}>
          <PolarGrid stroke="#1e293b" />
          {/* Criterion scores are 0–10; without a fixed domain the chart picks its own scale. */}
          <PolarRadiusAxis domain={[0, 10]} tick={false} axisLine={false} />
          <PolarAngleAxis 
            dataKey="subject" 
            tick={{ fill: '#94a3b8', fontSize: 12, fontWeight: 500 }}
          />
          <Radar
            name="Score"
            dataKey="score"
            stroke="#6366f1"
            strokeWidth={2}
            fill="rgba(99, 102, 241, 0.2)"
            fillOpacity={1}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}

export const ScoreRadar = dynamic(() => Promise.resolve(ScoreRadarComponent), {
  ssr: false,
});
