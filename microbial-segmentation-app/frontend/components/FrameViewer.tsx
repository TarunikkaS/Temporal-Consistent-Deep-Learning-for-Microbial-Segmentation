'use client';

import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Play, Pause, SkipBack, SkipForward } from 'lucide-react';

interface FrameViewerProps {
  orig_frames: (string | null)[];
  gt_frames: (string | null)[];
  pred_frames: (string | null)[];
  triplet_frames: (string | null)[];
  n_frames: number;
  fps: number;
  metrics: {
    time: number[];
    area_pred: number[];
    area_gt?: number[];
    growth_pred: number[];
    division_like: number[];
  };
}

export default function FrameViewer({
  orig_frames,
  gt_frames,
  pred_frames,
  triplet_frames,
  n_frames,
  fps,
  metrics
}: FrameViewerProps) {
  const [currentFrame, setCurrentFrame] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playInterval, setPlayInterval] = useState<NodeJS.Timeout | null>(null);
  const [viewMode, setViewMode] = useState<'triplet' | 'separate'>('separate');

  // Debug: Log frame data
  React.useEffect(() => {
    console.log('FrameViewer received:', {
      orig_frames: orig_frames.length,
      gt_frames: gt_frames.length,
      pred_frames: pred_frames.length,
      sample_orig: orig_frames[0],
      sample_gt: gt_frames[0],
      sample_pred: pred_frames[0]
    });
  }, [orig_frames, gt_frames, pred_frames]);

  const goToFrame = (index: number) => {
    const clampedIndex = Math.max(0, Math.min(index, n_frames - 1));
    setCurrentFrame(clampedIndex);
  };

  const nextFrame = () => {
    goToFrame(currentFrame + 1);
  };

  const prevFrame = () => {
    goToFrame(currentFrame - 1);
  };

  const firstFrame = () => {
    goToFrame(0);
  };

  const lastFrame = () => {
    goToFrame(n_frames - 1);
  };

  const togglePlay = () => {
    if (isPlaying) {
      // Stop playing
      if (playInterval) {
        clearInterval(playInterval);
        setPlayInterval(null);
      }
      setIsPlaying(false);
    } else {
      // Start playing
      setIsPlaying(true);
      const interval = setInterval(() => {
        setCurrentFrame((prev) => {
          if (prev >= n_frames - 1) {
            return 0; // Loop back to start
          }
          return prev + 1;
        });
      }, 200); // 5 FPS playback
      setPlayInterval(interval);
    }
  };

  // Cleanup interval on unmount
  React.useEffect(() => {
    return () => {
      if (playInterval) {
        clearInterval(playInterval);
      }
    };
  }, [playInterval]);

  if (n_frames === 0) {
    return (
      <div className="bg-dark-matter rounded-2xl border border-white/10 p-8 shadow-card-elevation">
        <p className="text-stardust text-center font-mono">No frames available</p>
      </div>
    );
  }

  // Get current metrics
  const time = metrics.time[currentFrame] || 0;
  const area_pred = metrics.area_pred[currentFrame] || 0;
  const area_gt = metrics.area_gt ? metrics.area_gt[currentFrame] : null;
  const growth = metrics.growth_pred[currentFrame] || 0;
  const isDivision = metrics.division_like[currentFrame] === 1;

  return (
    <div className="bg-dark-matter rounded-2xl border border-white/10 p-8 shadow-card-elevation transition-all duration-300 hover:-translate-y-1 hover:border-bitcoin-orange/30">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-2xl font-heading font-semibold text-white flex items-center gap-2">
          <span className="text-bitcoin-orange">━</span> Frame Viewer
        </h3>
        
        {/* View Mode Toggle */}
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode('separate')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              viewMode === 'separate'
                ? 'bg-bitcoin-orange text-white'
                : 'bg-white/10 text-stardust hover:bg-white/20'
            }`}
          >
            3-Panel
          </button>
          <button
            onClick={() => setViewMode('triplet')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              viewMode === 'triplet'
                ? 'bg-bitcoin-orange text-white'
                : 'bg-white/10 text-stardust hover:bg-white/20'
            }`}
          >
            Combined
          </button>
        </div>
      </div>

      {/* Metrics Bar */}
      <div className="mb-4 p-4 bg-black/50 rounded-lg border border-white/10 flex items-center justify-between">
        <div className="text-sm text-stardust">
          <span className="font-mono">time = </span>
          <span className="text-white font-bold">{time.toFixed(2)}s</span>
        </div>
        
        {area_gt !== null && (
          <div className="text-sm">
            <span className="font-mono text-stardust">GT area = </span>
            <span className="text-green-400 font-bold">{area_gt}</span>
          </div>
        )}
        
        <div className="text-sm">
          <span className="font-mono text-stardust">Pred area = </span>
          <span className="text-orange-400 font-bold">{area_pred}</span>
          <span className="ml-4 font-mono text-stardust">growth = </span>
          <span className="text-orange-400 font-bold">{growth.toFixed(3)}</span>
        </div>
      </div>

      {/* Division Event Warning */}
      {isDivision && (
        <div className="mb-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg">
          <p className="text-red-400 font-semibold text-sm flex items-center gap-2">
            <span className="animate-pulse">⚠️</span> Division-like event detected
          </p>
        </div>
      )}

      {/* Image Display */}
      {viewMode === 'triplet' ? (
        // Single combined triplet image
        <div className="relative bg-black rounded-xl overflow-hidden border border-white/10 shadow-card-elevation">
          {triplet_frames[currentFrame] ? (
            <img
              src={triplet_frames[currentFrame]!}
              alt={`Triplet Frame ${currentFrame + 1}`}
              className="w-full h-auto"
            />
          ) : (
            <div className="w-full aspect-video flex items-center justify-center text-stardust">
              Loading...
            </div>
          )}
        </div>
      ) : (
        // Three separate panels
        <div className="grid grid-cols-3 gap-4">
          {/* Original */}
          <div className="bg-black rounded-xl overflow-hidden border border-white/10">
            <div className="p-2 bg-black/70 border-b border-white/10">
              <p className="text-xs text-stardust font-mono text-center">Original</p>
            </div>
            {orig_frames[currentFrame] ? (
              <img
                src={orig_frames[currentFrame]!}
                alt={`Original ${currentFrame + 1}`}
                className="w-full h-auto"
              />
            ) : (
              <div className="w-full aspect-square flex items-center justify-center text-stardust text-sm">
                No image
              </div>
            )}
          </div>

          {/* Ground Truth */}
          <div className="bg-black rounded-xl overflow-hidden border border-green-500/30">
            <div className="p-2 bg-black/70 border-b border-green-500/30">
              <p className="text-xs text-green-400 font-mono text-center">Ground Truth</p>
            </div>
            {gt_frames[currentFrame] ? (
              <img
                src={gt_frames[currentFrame]!}
                alt={`GT ${currentFrame + 1}`}
                className="w-full h-auto"
              />
            ) : (
              <div className="w-full aspect-square flex items-center justify-center text-stardust text-sm">
                No GT
              </div>
            )}
          </div>

          {/* Prediction */}
          <div className="bg-black rounded-xl overflow-hidden border border-orange-500/30">
            <div className="p-2 bg-black/70 border-b border-orange-500/30">
              <p className="text-xs text-orange-400 font-mono text-center">Prediction</p>
            </div>
            {pred_frames[currentFrame] ? (
              <img
                src={pred_frames[currentFrame]!}
                alt={`Pred ${currentFrame + 1}`}
                className="w-full h-auto"
              />
            ) : (
              <div className="w-full aspect-square flex items-center justify-center text-stardust text-sm">
                No image
              </div>
            )}
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="mt-6">
        {/* Slider */}
        <input
          type="range"
          min="0"
          max={n_frames - 1}
          value={currentFrame}
          onChange={(e) => goToFrame(parseInt(e.target.value))}
          className="w-full h-2 bg-white/20 rounded-lg appearance-none cursor-pointer accent-bitcoin-orange"
        />

        {/* Playback Controls */}
        <div className="flex items-center justify-center gap-2 mt-4">
          <button
            onClick={firstFrame}
            className="p-2 bg-white/10 border border-white/20 rounded-lg hover:bg-white/20 transition-all"
            title="First Frame"
          >
            <SkipBack className="w-5 h-5 text-white" />
          </button>
          
          <button
            onClick={prevFrame}
            className="p-3 bg-white/10 border border-white/20 rounded-lg hover:bg-bitcoin-orange/20 hover:border-bitcoin-orange/50 transition-all duration-300"
            title="Previous Frame"
          >
            <ChevronLeft className="w-5 h-5 text-white" />
          </button>
          
          <button
            onClick={togglePlay}
            className="p-4 bg-gradient-to-r from-burnt-orange to-bitcoin-orange rounded-lg hover:scale-105 shadow-orange-glow hover:shadow-orange-glow-lg transition-all duration-300"
            title={isPlaying ? 'Pause' : 'Play'}
          >
            {isPlaying ? <Pause className="w-6 h-6 text-white" /> : <Play className="w-6 h-6 text-white" />}
          </button>
          
          <button
            onClick={nextFrame}
            className="p-3 bg-white/10 border border-white/20 rounded-lg hover:bg-bitcoin-orange/20 hover:border-bitcoin-orange/50 transition-all duration-300"
            title="Next Frame"
          >
            <ChevronRight className="w-5 h-5 text-white" />
          </button>
          
          <button
            onClick={lastFrame}
            className="p-3 bg-white/10 border border-white/20 rounded-lg hover:bg-bitcoin-orange/20 hover:border-bitcoin-orange/50 transition-all duration-300"
            title="Last Frame"
          >
            <SkipForward className="w-5 h-5 text-white" />
          </button>
        </div>

        {/* Frame Counter */}
        <div className="flex items-center justify-center gap-3 mt-6">
          <label className="text-sm text-stardust font-mono uppercase tracking-wider">Jump to frame:</label>
          <input
            type="number"
            min="1"
            max={n_frames}
            value={currentFrame + 1}
            onChange={(e) => goToFrame(parseInt(e.target.value) - 1)}
            className="w-24 px-3 py-2 bg-black/50 border-b-2 border-white/20 text-white text-sm font-mono focus-visible:border-bitcoin-orange focus-visible:outline-none transition-all duration-200"
          />
          <span className="text-stardust text-sm font-mono">/ {n_frames}</span>
        </div>
      </div>
    </div>
  );
}
