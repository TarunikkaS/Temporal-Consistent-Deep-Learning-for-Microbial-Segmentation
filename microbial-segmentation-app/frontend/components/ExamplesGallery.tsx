'use client';

import React from 'react';
import { Play, Download, Database } from 'lucide-react';

interface ExampleVideo {
  id: string;
  bacteriaType: string;
  description: string;
  thumbnail: string;
  frames: number;
  duration: string;
}

interface ExamplesGalleryProps {
  onSelectExample: (exampleId: string) => void;
}

const EXAMPLE_VIDEOS: ExampleVideo[] = [
  {
    id: 'lysobacter_dataset1',
    bacteriaType: 'Lysobacter',
    description: 'Time-lapse Dataset 1',
    thumbnail: '/lysobacter/dataset1/thumb.tif',
    frames: 16,
    duration: '16 frames'
  },
  {
    id: 'lysobacter_dataset2',
    bacteriaType: 'Lysobacter',
    description: 'Time-lapse Dataset 2',
    thumbnail: '/lysobacter/dataset2/thumb.tif',
    frames: 16,
    duration: '16 frames'
  },
  {
    id: 'pputida_dataset1',
    bacteriaType: 'Pputida',
    description: 'Time-lapse Dataset 1',
    thumbnail: '/pputida/dataset1/thumb.tif',
    frames: 16,
    duration: '16 frames'
  },
  {
    id: 'pputida_dataset2',
    bacteriaType: 'Pputida',
    description: 'Time-lapse Dataset 2',
    thumbnail: '/pputida/dataset2/thumb.tif',
    frames: 16,
    duration: '16 frames'
  },
  {
    id: 'pveronii_dataset1',
    bacteriaType: 'Pveronii',
    description: 'Time-lapse Dataset 1',
    thumbnail: '/pveronii/dataset1/thumb.tif',
    frames: 16,
    duration: '16 frames'
  },
  {
    id: 'pveronii_dataset2',
    bacteriaType: 'Pveronii',
    description: 'Time-lapse Dataset 2',
    thumbnail: '/pveronii/dataset2/thumb.tif',
    frames: 16,
    duration: '16 frames'
  },
  {
    id: 'rahnella_dataset1',
    bacteriaType: 'Rahnella',
    description: 'Time-lapse Dataset 1',
    thumbnail: '/rahnella/dataset1/thumb.tif',
    frames: 16,
    duration: '16 frames'
  },
  {
    id: 'rahnella_dataset2',
    bacteriaType: 'Rahnella',
    description: 'Time-lapse Dataset 2',
    thumbnail: '/rahnella/dataset2/thumb.tif',
    frames: 16,
    duration: '16 frames'
  }
];

export default function ExamplesGallery({ onSelectExample }: ExamplesGalleryProps) {
  // Group examples by bacteria type
  const groupedExamples = EXAMPLE_VIDEOS.reduce((acc, video) => {
    if (!acc[video.bacteriaType]) {
      acc[video.bacteriaType] = [];
    }
    acc[video.bacteriaType].push(video);
    return acc;
  }, {} as Record<string, ExampleVideo[]>);

  const getBacteriaColor = (type: string) => {
    const colors: Record<string, string> = {
      'E. coli': 'bg-blue-500/10 border-blue-500/30',
      'Bacillus subtilis': 'bg-green-500/10 border-green-500/30',
      'Staphylococcus aureus': 'bg-purple-500/10 border-purple-500/30',
      'Pseudomonas aeruginosa': 'bg-bitcoin-orange/10 border-bitcoin-orange/30'
    };
    return colors[type] || 'bg-white/5 border-white/10';
  };

  const getBacteriaBadgeColor = (type: string) => {
    const colors: Record<string, string> = {
      'E. coli': 'bg-blue-500/20 text-blue-400 border border-blue-500/50',
      'Bacillus subtilis': 'bg-green-500/20 text-green-400 border border-green-500/50',
      'Staphylococcus aureus': 'bg-purple-500/20 text-purple-400 border border-purple-500/50',
      'Pseudomonas aeruginosa': 'bg-bitcoin-orange/20 text-bitcoin-orange border border-bitcoin-orange/50'
    };
    return colors[type] || 'bg-white/10 text-stardust border border-white/20';
  };

  return (
    <div className="bg-dark-matter rounded-2xl border border-white/10 p-8 shadow-card-elevation transition-all duration-300">
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-bitcoin-orange/20 border border-bitcoin-orange/50 rounded-lg p-2">
          <Database className="w-6 h-6 text-bitcoin-orange" />
        </div>
        <div>
          <h2 className="text-2xl font-heading font-semibold text-white">Example Dataset Videos</h2>
          <p className="text-sm text-stardust">Select any example to run segmentation analysis</p>
        </div>
      </div>

      <div className="space-y-8">
        {Object.entries(groupedExamples).map(([bacteriaType, videos]) => (
          <div key={bacteriaType}>
            {/* Bacteria Type Header */}
            <div className="flex items-center gap-2 mb-4">
              <span className={`px-3 py-1 rounded-lg text-sm font-mono font-semibold uppercase tracking-wider ${getBacteriaBadgeColor(bacteriaType)}`}>
                {bacteriaType}
              </span>
              <span className="text-sm text-stardust font-mono">
                {videos.length} example{videos.length !== 1 ? 's' : ''}
              </span>
            </div>

            {/* Video Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {videos.map((video) => (
                <div
                  key={video.id}
                  className={`group border-2 rounded-xl overflow-hidden transition-all duration-300 cursor-pointer ${getBacteriaColor(bacteriaType)} hover:-translate-y-1 hover:shadow-orange-glow`}
                  onClick={() => onSelectExample(video.id)}
                >
                  {/* Thumbnail */}
                  <div className="relative bg-black aspect-video flex items-center justify-center overflow-hidden">
                    {/* Placeholder for thumbnail - in real app, this would be an actual image */}
                    <div className="absolute inset-0 bg-gradient-to-br from-void via-dark-matter to-void flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                      <div className="relative">
                        <Play className="w-16 h-16 text-bitcoin-orange opacity-60 group-hover:opacity-100 transition-opacity" />
                        <div className="absolute inset-0 blur-md">
                          <Play className="w-16 h-16 text-bitcoin-orange opacity-50" />
                        </div>
                      </div>
                    </div>
                    <div className="absolute top-2 right-2 bg-black/70 backdrop-blur-sm text-white px-2 py-1 rounded-lg text-xs font-mono border border-white/20">
                      {video.frames} frames
                    </div>
                  </div>

                  {/* Info */}
                  <div className="p-4 bg-black/30">
                    <h3 className="font-heading font-semibold text-white mb-2">
                      {video.description}
                    </h3>
                    <div className="flex items-center justify-between text-sm">
                      <span className="flex items-center gap-1 text-stardust font-mono">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {video.duration}
                      </span>
                      <button
                        className="text-bitcoin-orange hover:text-digital-gold font-medium font-mono uppercase text-xs tracking-wider flex items-center gap-1 transition-colors"
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectExample(video.id);
                        }}
                      >
                        Analyze
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Info Banner */}
      <div className="mt-8 p-4 bg-bitcoin-orange/10 border border-bitcoin-orange/30 rounded-xl backdrop-blur-sm">
        <div className="flex items-start gap-3">
          <svg className="w-5 h-5 text-bitcoin-orange mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div className="text-sm">
            <p className="font-medium font-mono text-bitcoin-orange mb-1 uppercase tracking-wider">Example Dataset</p>
            <p className="text-stardust leading-relaxed">
              These examples are from the STRack dataset, containing time-lapse microscopy of various bacterial species. 
              Each video includes ground truth segmentation masks for validation.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
