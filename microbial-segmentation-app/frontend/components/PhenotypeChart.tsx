'use client';

import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Metrics } from '@/types';

interface PhenotypeChartProps {
  metrics: Metrics;
}

export default function PhenotypeChart({ metrics }: PhenotypeChartProps) {
  // Handle missing phenotype data
  if (!metrics.phenotype_counts || metrics.phenotype_counts.length === 0) {
    return (
      <div className="bg-dark-matter rounded-2xl border border-white/10 p-8 shadow-card-elevation">
        <h3 className="text-2xl font-heading font-semibold text-white mb-6 flex items-center gap-2">
          <span className="text-bitcoin-orange">━</span> Phenotype Distribution
        </h3>
        <p className="text-stardust text-center py-8">No phenotype data available</p>
      </div>
    );
  }

  // Sample data for visualization (every 10th frame to avoid clutter)
  const step = Math.max(1, Math.floor(metrics.phenotype_counts.length / 20));
  const chartData = metrics.phenotype_counts
    .filter((_, idx) => idx % step === 0)
    .map((counts, idx) => ({
      frame: idx * step,
      'Rod-like': counts.rod_like,
      'Elongated': counts.elongated,
      'Compact': counts.compact,
      'Other': counts.other,
    }));

  // Calculate totals
  const totals = {
    rod_like: 0,
    elongated: 0,
    compact: 0,
    other: 0,
  };

  metrics.phenotype_counts.forEach((counts) => {
    totals.rod_like += counts.rod_like;
    totals.elongated += counts.elongated;
    totals.compact += counts.compact;
    totals.other += counts.other;
  });

  const totalCells = totals.rod_like + totals.elongated + totals.compact + totals.other;

  return (
    <div className="bg-dark-matter rounded-2xl border border-white/10 p-8 shadow-card-elevation transition-all duration-300 hover:-translate-y-1 hover:border-bitcoin-orange/30">
      <h3 className="text-2xl font-heading font-semibold text-white mb-6 flex items-center gap-2">
        <span className="text-bitcoin-orange">━</span> Phenotype Distribution
      </h3>
      
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis
            dataKey="frame"
            label={{ value: 'Frame', position: 'insideBottom', offset: -5, style: { fill: '#94A3B8', fontFamily: 'monospace' } }}
            stroke="#94A3B8"
            style={{ fontSize: '12px', fontFamily: 'monospace' }}
          />
          <YAxis 
            label={{ value: 'Cell Count', angle: -90, position: 'insideLeft', style: { fill: '#94A3B8', fontFamily: 'monospace' } }}
            stroke="#94A3B8"
            style={{ fontSize: '12px', fontFamily: 'monospace' }}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#0F1115', 
              border: '1px solid rgba(247,147,26,0.3)', 
              borderRadius: '8px',
              fontFamily: 'monospace'
            }}
            labelStyle={{ color: '#94A3B8' }}
          />
          <Legend 
            wrapperStyle={{ 
              fontFamily: 'monospace',
              fontSize: '12px'
            }}
          />
          <Bar dataKey="Rod-like" stackId="a" fill="#22c55e" radius={[4, 4, 0, 0]} />
          <Bar dataKey="Elongated" stackId="a" fill="#06b6d4" />
          <Bar dataKey="Compact" stackId="a" fill="#3b82f6" />
          <Bar dataKey="Other" stackId="a" fill="#F7931A" />
        </BarChart>
      </ResponsiveContainer>

      {/* Phenotype Legend with Colors */}
      <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="flex items-center gap-3 bg-green-500/10 border border-green-500/30 p-4 rounded-xl backdrop-blur-sm">
          <div className="w-3 h-3 bg-green-500 rounded-full shadow-[0_0_8px_rgba(34,197,94,0.6)]" />
          <div>
            <p className="text-xs text-stardust font-mono uppercase tracking-wider">Rod-like</p>
            <p className="text-xl font-bold font-mono text-green-400">{totals.rod_like}</p>
            <p className="text-xs text-stardust/70 font-mono">
              {totalCells > 0 ? ((totals.rod_like / totalCells) * 100).toFixed(1) : 0}%
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 bg-cyan-500/10 border border-cyan-500/30 p-4 rounded-xl backdrop-blur-sm">
          <div className="w-3 h-3 bg-cyan-500 rounded-full shadow-[0_0_8px_rgba(6,182,212,0.6)]" />
          <div>
            <p className="text-xs text-stardust font-mono uppercase tracking-wider">Elongated</p>
            <p className="text-xl font-bold font-mono text-cyan-400">{totals.elongated}</p>
            <p className="text-xs text-stardust/70 font-mono">
              {totalCells > 0 ? ((totals.elongated / totalCells) * 100).toFixed(1) : 0}%
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 bg-blue-500/10 border border-blue-500/30 p-4 rounded-xl backdrop-blur-sm">
          <div className="w-3 h-3 bg-blue-500 rounded-full shadow-[0_0_8px_rgba(59,130,246,0.6)]" />
          <div>
            <p className="text-xs text-stardust font-mono uppercase tracking-wider">Compact</p>
            <p className="text-xl font-bold font-mono text-blue-400">{totals.compact}</p>
            <p className="text-xs text-stardust/70 font-mono">
              {totalCells > 0 ? ((totals.compact / totalCells) * 100).toFixed(1) : 0}%
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 bg-bitcoin-orange/10 border border-bitcoin-orange/30 p-4 rounded-xl backdrop-blur-sm">
          <div className="w-3 h-3 bg-bitcoin-orange rounded-full shadow-[0_0_8px_rgba(247,147,26,0.6)]" />
          <div>
            <p className="text-xs text-stardust font-mono uppercase tracking-wider">Other</p>
            <p className="text-xl font-bold font-mono text-bitcoin-orange">{totals.other}</p>
            <p className="text-xs text-stardust/70 font-mono">
              {totalCells > 0 ? ((totals.other / totalCells) * 100).toFixed(1) : 0}%
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
