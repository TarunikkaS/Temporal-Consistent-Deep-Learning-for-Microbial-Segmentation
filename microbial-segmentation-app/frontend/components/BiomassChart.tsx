'use client';

import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Metrics } from '@/types';

interface BiomassChartProps {
  metrics: Metrics;
}

export default function BiomassChart({ metrics }: BiomassChartProps) {
  // Prepare data for chart
  const chartData = metrics.time.map((time, idx) => ({
    time: time.toFixed(2),
    'Predicted Area': metrics.area_pred[idx],
    ...(metrics.area_gt ? { 'Ground Truth Area': metrics.area_gt[idx] } : {}),
    'Growth Rate': metrics.growth_pred[idx] * 1000, // Scale for visibility
  }));

  return (
    <div className="bg-dark-matter rounded-2xl border border-white/10 p-8 shadow-card-elevation transition-all duration-300 hover:-translate-y-1 hover:border-bitcoin-orange/30">
      <h3 className="text-2xl font-heading font-semibold text-white mb-6 flex items-center gap-2">
        <span className="text-bitcoin-orange">━</span> Biomass & Growth
      </h3>
      
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis
            dataKey="time"
            label={{ value: 'Time (s)', position: 'insideBottom', offset: -5, style: { fill: '#94A3B8', fontFamily: 'monospace' } }}
            stroke="#94A3B8"
            style={{ fontSize: '12px', fontFamily: 'monospace' }}
          />
          <YAxis 
            label={{ value: 'Area (pixels)', angle: -90, position: 'insideLeft', style: { fill: '#94A3B8', fontFamily: 'monospace' } }} 
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
          <Line
            type="monotone"
            dataKey="Predicted Area"
            stroke="#F7931A"
            strokeWidth={3}
            dot={false}
            filter="url(#glow)"
          />
          {metrics.area_gt && (
            <Line
              type="monotone"
              dataKey="Ground Truth Area"
              stroke="#10B981"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
            />
          )}
          <defs>
            <filter id="glow">
              <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
        </LineChart>
      </ResponsiveContainer>

      {/* Statistics */}
      <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-bitcoin-orange/10 border border-bitcoin-orange/30 p-4 rounded-xl backdrop-blur-sm">
          <p className="text-xs text-stardust font-mono uppercase tracking-wider">Total Frames</p>
          <p className="text-2xl font-bold font-mono text-bitcoin-orange mt-1">{metrics.time.length}</p>
        </div>
        
        <div className="bg-green-500/10 border border-green-500/30 p-4 rounded-xl backdrop-blur-sm">
          <p className="text-xs text-stardust font-mono uppercase tracking-wider">Avg Area</p>
          <p className="text-2xl font-bold font-mono text-green-400 mt-1">
            {(metrics.area_pred.reduce((a, b) => a + b, 0) / metrics.area_pred.length).toFixed(0)}
          </p>
        </div>
        
        <div className="bg-digital-gold/10 border border-digital-gold/30 p-4 rounded-xl backdrop-blur-sm">
          <p className="text-xs text-stardust font-mono uppercase tracking-wider">Max Area</p>
          <p className="text-2xl font-bold font-mono text-digital-gold mt-1">
            {Math.max(...metrics.area_pred).toFixed(0)}
          </p>
        </div>
        
        <div className="bg-burnt-orange/10 border border-burnt-orange/30 p-4 rounded-xl backdrop-blur-sm">
          <p className="text-xs text-stardust font-mono uppercase tracking-wider">Division Events</p>
          <p className="text-2xl font-bold font-mono text-burnt-orange mt-1">
            {metrics.division_like.filter(x => x === 1).length}
          </p>
        </div>
      </div>
    </div>
  );
}
