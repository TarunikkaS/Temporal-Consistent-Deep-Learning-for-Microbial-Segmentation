'use client';

import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Play, Pause, SkipBack, SkipForward } from 'lucide-react';
import { getFileUrl } from '@/lib/api';

interface ResultsViewerProps {
  frames: string[];
  totalFrames: number;
}

export default function ResultsViewer({ frames, totalFrames }: ResultsViewerProps) {
  const [currentFrame, setCurrentFrame] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playInterval, setPlayInterval] = useState<NodeJS.Timeout | null>(null);

  const goToFrame = (index: number) => {
    const clampedIndex = Math.max(0, Math.min(index, frames.length - 1));
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
    goToFrame(frames.length - 1);
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
          if (prev >= frames.length - 1) {
            return 0; // Loop back to start
          }
          return prev + 1;
        });
      }, 100); // 10 FPS playback
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

  if (frames.length === 0) {
    return (
      <div className="bg-dark-matter rounded-2xl border border-white/10 p-8 shadow-card-elevation">
        <p className="text-stardust text-center font-mono">No frames available</p>
      </div>
    );
  }

  return (
    <div className="bg-dark-matter rounded-2xl border border-white/10 p-8 shadow-card-elevation transition-all duration-300 hover:-translate-y-1 hover:border-bitcoin-orange/30">
      <h3 className="text-2xl font-heading font-semibold text-white mb-6 flex items-center gap-2">
        <span className="text-bitcoin-orange">━</span> Frame Viewer
      </h3>

      {/* Image Display */}
      <div className="relative bg-black rounded-xl overflow-hidden border border-white/10 shadow-card-elevation" style={{ aspectRatio: '16/9' }}>
        <img
          src={getFileUrl(frames[currentFrame])}
          alt={`Frame ${currentFrame + 1}`}
          className="w-full h-full object-contain"
        />
        
        {/* Frame Counter Overlay */}
        <div className="absolute top-4 right-4 bg-black/70 backdrop-blur-sm text-white px-4 py-2 rounded-lg text-sm font-mono border border-bitcoin-orange/30 shadow-orange-glow">
          Frame <span className="text-bitcoin-orange font-bold">{currentFrame + 1}</span> / {totalFrames}
        </div>
      </div>

      {/* Controls */}
      <div className="mt-4">
        {/* Slider */}
        <input
          type="range"
          min="0"
          max={frames.length - 1}
          value={currentFrame}
          onChange={(e) => goToFrame(parseInt(e.target.value))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
        />

        {/* Playback Controls */}
        <div className="flex items-center justify-center gap-2 mt-4">
          <button
            onClick={firstFrame}
            className="p-2 bg-gray-200 rounded-md hover:bg-gray-300 transition-colors"
            title="First Frame"
          >
            <SkipBack className="w-5 h-5" />
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

        {/* Frame Input */}
        <div className="flex items-center justify-center gap-3 mt-6">
          <label className="text-sm text-stardust font-mono uppercase tracking-wider">Jump to:</label>
          <input
            type="number"
            min="1"
            max={frames.length}
            value={currentFrame + 1}
            onChange={(e) => goToFrame(parseInt(e.target.value) - 1)}
            className="w-24 px-3 py-2 bg-black/50 border-b-2 border-white/20 text-white text-sm font-mono focus-visible:border-bitcoin-orange focus-visible:outline-none transition-all duration-200"
          />
        </div>
      </div>
    </div>
  );
}
