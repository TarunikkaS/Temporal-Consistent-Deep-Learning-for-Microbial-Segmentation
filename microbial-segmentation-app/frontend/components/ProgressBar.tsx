'use client';

import React from 'react';
import { Activity, CheckCircle, AlertTriangle, Loader2 } from 'lucide-react';
import { JobStatus } from '@/types';

interface ProgressBarProps {
  status: JobStatus;
}

export default function ProgressBar({ status }: ProgressBarProps) {
  const getStatusConfig = () => {
    switch (status.status) {
      case 'queued':
        return {
          color: 'bg-digital-gold',
          glowColor: 'shadow-gold-glow',
          icon: <Loader2 className="w-6 h-6 text-digital-gold animate-spin" />,
          text: 'Queued',
          bgGlow: 'bg-digital-gold/20'
        };
      case 'running':
        return {
          color: 'bg-gradient-to-r from-burnt-orange to-bitcoin-orange',
          glowColor: 'shadow-orange-glow',
          icon: <Activity className="w-6 h-6 text-bitcoin-orange animate-pulse" />,
          text: 'Processing',
          bgGlow: 'bg-bitcoin-orange/20'
        };
      case 'completed':
        return {
          color: 'bg-gradient-to-r from-bitcoin-orange to-digital-gold',
          glowColor: 'shadow-gold-glow',
          icon: <CheckCircle className="w-6 h-6 text-digital-gold" />,
          text: 'Completed',
          bgGlow: 'bg-digital-gold/20'
        };
      case 'failed':
        return {
          color: 'bg-red-500',
          glowColor: 'shadow-[0_0_20px_rgba(239,68,68,0.5)]',
          icon: <AlertTriangle className="w-6 h-6 text-red-400" />,
          text: 'Failed',
          bgGlow: 'bg-red-500/20'
        };
      default:
        return {
          color: 'bg-white/20',
          glowColor: '',
          icon: <Loader2 className="w-6 h-6 text-stardust" />,
          text: 'Unknown',
          bgGlow: 'bg-white/10'
        };
    }
  };

  const config = getStatusConfig();

  return (
    <div className="bg-dark-matter rounded-2xl border border-white/10 p-8 shadow-card-elevation">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className={`${config.bgGlow} border border-bitcoin-orange/50 rounded-lg p-2`}>
            {config.icon}
          </div>
          <h3 className="text-xl font-heading font-semibold text-white">{config.text}</h3>
        </div>
        <span className="text-2xl font-mono font-bold text-bitcoin-orange">
          {status.progress.toFixed(1)}%
        </span>
      </div>

      {/* Progress Bar */}
      <div className="relative w-full h-3 bg-black/50 rounded-full overflow-hidden border border-white/10">
        {/* Background glow effect */}
        <div 
          className={`absolute inset-0 ${config.color} opacity-20 blur-sm`}
          style={{ width: `${status.progress}%` }}
        />
        {/* Main progress bar */}
        <div
          className={`relative h-full ${config.color} ${config.glowColor} transition-all duration-500 ease-out`}
          style={{ width: `${status.progress}%` }}
        />
      </div>

      {/* Stage and Message */}
      <div className="mt-6 space-y-3">
        <div className="flex items-center gap-2">
          <span className="text-sm font-mono font-medium text-stardust uppercase tracking-wider">
            Stage:
          </span>
          <span className="text-sm font-mono text-white">
            {status.stage}
          </span>
        </div>
        <p className="text-sm text-stardust leading-relaxed">
          {status.message}
        </p>
      </div>

      {/* Error Display */}
      {status.error && (
        <div className="mt-6 p-4 bg-red-500/10 border border-red-500/50 rounded-xl backdrop-blur-sm">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-red-400 mb-1">Error:</p>
              <p className="text-sm text-red-300">{status.error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Spinner for running jobs */}
      {status.status === 'running' && (
        <div className="mt-6 flex items-center justify-center">
          <div className="relative">
            {/* Outer ring */}
            <div className="w-16 h-16 border-2 border-bitcoin-orange/30 rounded-full animate-spin-slow" />
            {/* Inner ring */}
            <div className="absolute inset-2 border-2 border-digital-gold/30 rounded-full animate-spin-reverse" />
            {/* Center glow */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-4 h-4 bg-bitcoin-orange rounded-full shadow-orange-glow animate-pulse" />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
