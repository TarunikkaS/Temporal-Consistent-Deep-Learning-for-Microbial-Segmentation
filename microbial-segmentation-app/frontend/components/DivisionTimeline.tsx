'use client';

import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { Metrics } from '@/types';

interface DivisionTimelineProps {
  metrics: Metrics;
}

export default function DivisionTimeline({ metrics }: DivisionTimelineProps) {
  const totalFrames = metrics.time.length;
  
  // Get division event frames from division_like array
  const divisionFrames = metrics.division_like
    .map((val, idx) => (val === 1 ? idx : -1))
    .filter(idx => idx !== -1);
  
  // Calculate position percentage for each division event
  const divisionMarkers = divisionFrames.map((frame) => ({
    frame,
    time: metrics.time[frame]?.toFixed(2) || '0',
    position: (frame / totalFrames) * 100,
  }));

  return (
    <div className="bg-dark-matter rounded-2xl border border-white/10 p-8 shadow-card-elevation transition-all duration-300 hover:-translate-y-1 hover:border-bitcoin-orange/30">
      <h3 className="text-2xl font-heading font-semibold text-white mb-6 flex items-center gap-2">
        <span className="text-bitcoin-orange">━</span> Division-like Events
      </h3>
      
      {divisionMarkers.length === 0 ? (
        <div className="text-center py-12">
          <div className="inline-block p-4 bg-bitcoin-orange/10 border border-bitcoin-orange/30 rounded-full mb-4">
            <AlertTriangle className="w-12 h-12 text-bitcoin-orange opacity-70" />
          </div>
          <p className="text-stardust font-mono">No division-like events detected</p>
        </div>
      ) : (
        <>
          {/* Timeline */}
          <div className="relative h-20 bg-black/30 rounded-xl mb-6 p-4 border border-white/10">
            {/* Base line with gradient */}
            <div className="absolute top-1/2 left-4 right-4 h-1 bg-gradient-to-r from-burnt-orange via-bitcoin-orange to-digital-gold transform -translate-y-1/2 shadow-orange-glow" />
            
            {/* Division markers */}
            {divisionMarkers.map((marker, idx) => (
              <div
                key={idx}
                className="absolute top-1/2 transform -translate-y-1/2 -translate-x-1/2"
                style={{ left: `calc(1rem + ${marker.position}% * (100% - 2rem) / 100)` }}
              >
                <div className="relative group">
                  <div className="w-5 h-5 bg-bitcoin-orange rounded-full border-2 border-dark-matter shadow-orange-glow animate-pulse group-hover:scale-125 transition-transform" />
                  {/* Glow effect */}
                  <div className="absolute inset-0 w-5 h-5 bg-bitcoin-orange rounded-full blur-md opacity-50 group-hover:opacity-75" />
                  {/* Label */}
                  <div className="absolute top-8 left-1/2 transform -translate-x-1/2 whitespace-nowrap">
                    <p className="text-xs font-mono font-medium text-bitcoin-orange bg-black/70 backdrop-blur-sm px-2 py-1 rounded-lg border border-bitcoin-orange/30">F{marker.frame}</p>
                  </div>
                </div>
              </div>
            ))}
            
            {/* Start and end markers */}
            <div className="absolute top-1/2 left-4 transform -translate-y-1/2">
              <div className="w-3 h-3 bg-white/50 rounded-full border border-white/20" />
            </div>
            <div className="absolute top-1/2 right-4 transform -translate-y-1/2">
              <div className="w-3 h-3 bg-white/50 rounded-full border border-white/20" />
            </div>
          </div>

          {/* Event List */}
          <div className="mt-8">
            <h4 className="text-sm font-mono font-semibold text-stardust mb-4 uppercase tracking-wider">Detected Events:</h4>
            <div className="space-y-3">
              {divisionMarkers.map((marker, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-4 bg-bitcoin-orange/10 border border-bitcoin-orange/30 rounded-xl backdrop-blur-sm hover:border-bitcoin-orange/50 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="bg-bitcoin-orange/20 border border-bitcoin-orange/50 rounded-lg p-2">
                      <AlertTriangle className="w-5 h-5 text-bitcoin-orange" />
                    </div>
                    <div>
                      <p className="text-sm font-heading font-medium text-white">
                        Division Event {idx + 1}
                      </p>
                      <p className="text-xs text-stardust font-mono">
                        Frame <span className="text-bitcoin-orange">{marker.frame}</span> • Time <span className="text-bitcoin-orange">{marker.time}s</span>
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-stardust/70 font-mono">Growth spike + topology change</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Statistics */}
          <div className="mt-8 grid grid-cols-3 gap-4">
            <div className="bg-bitcoin-orange/10 border border-bitcoin-orange/30 p-4 rounded-xl backdrop-blur-sm text-center">
              <p className="text-xs text-stardust font-mono uppercase tracking-wider">Total Events</p>
              <p className="text-3xl font-bold font-mono text-bitcoin-orange mt-1">{divisionMarkers.length}</p>
            </div>
            
            <div className="bg-digital-gold/10 border border-digital-gold/30 p-4 rounded-xl backdrop-blur-sm text-center">
              <p className="text-xs text-stardust font-mono uppercase tracking-wider">Avg Interval</p>
              <p className="text-3xl font-bold font-mono text-digital-gold mt-1">
                {divisionMarkers.length > 1
                  ? Math.round((totalFrames / divisionMarkers.length))
                  : '-'}
              </p>
              <p className="text-xs text-stardust/70 font-mono mt-1">frames</p>
            </div>
            
            <div className="bg-burnt-orange/10 border border-burnt-orange/30 p-4 rounded-xl backdrop-blur-sm text-center">
              <p className="text-xs text-stardust font-mono uppercase tracking-wider">Event Rate</p>
              <p className="text-3xl font-bold font-mono text-burnt-orange mt-1">
                {((divisionMarkers.length / totalFrames) * 100).toFixed(1)}%
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
