'use client';
import React from 'react';
import dynamic from 'next/dynamic';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
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
          <PolarGrid stroke="#1e293b" />
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
