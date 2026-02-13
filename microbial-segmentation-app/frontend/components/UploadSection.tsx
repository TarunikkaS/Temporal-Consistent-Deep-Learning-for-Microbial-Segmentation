'use client';

import React, { useState } from 'react';
import { Upload, FileVideo, FolderArchive, Zap } from 'lucide-react';

interface UploadSectionProps {
  onUpload: (file: File, config: UploadConfig) => void;
  isUploading: boolean;
}

export interface UploadConfig {
  threshold: number;
  minArea: number;
  species?: string;
  datasetName?: string;
}

export default function UploadSection({ onUpload, isUploading }: UploadSectionProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [threshold, setThreshold] = useState(0.5);
  const [minArea, setMinArea] = useState(300);
  const [species, setSpecies] = useState('');
  const [datasetName, setDatasetName] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleSubmit = () => {
    if (selectedFile && !isUploading) {
      const config: UploadConfig = {
        threshold,
        minArea,
        species: species || undefined,
        datasetName: datasetName || undefined,
      };
      onUpload(selectedFile, config);
    }
  };

  const fileIcon = selectedFile?.name.endsWith('.mp4') ? (
    <FileVideo className="w-12 h-12 text-bitcoin-orange" />
  ) : (
    <FolderArchive className="w-12 h-12 text-digital-gold" />
  );

  return (
    <div className="bg-dark-matter rounded-2xl border border-white/10 p-8 shadow-card-elevation transition-all duration-300 hover:-translate-y-1 hover:border-bitcoin-orange/50 hover:shadow-orange-glow">
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-burnt-orange/20 border border-burnt-orange/50 rounded-lg p-2">
          <Upload className="w-6 h-6 text-bitcoin-orange" />
        </div>
        <h2 className="text-2xl font-heading font-semibold text-white">Upload Dataset</h2>
      </div>
      
      {/* File Upload Area */}
      <div
        className={`group relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 ${
          dragActive
            ? 'border-bitcoin-orange bg-bitcoin-orange/10 shadow-orange-glow'
            : 'border-white/20 hover:border-bitcoin-orange/50 hover:bg-white/5'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        {selectedFile ? (
          <div className="flex flex-col items-center">
            <div className="relative">
              {fileIcon}
              {/* Animated glow pulse */}
              <div className="absolute inset-0 animate-ping opacity-20">
                {fileIcon}
              </div>
            </div>
            <p className="mt-4 text-base font-medium text-white font-mono">{selectedFile.name}</p>
            <p className="text-sm text-stardust font-mono mt-1">
              {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
            </p>
            <button
              onClick={() => setSelectedFile(null)}
              className="mt-4 text-sm text-burnt-orange hover:text-bitcoin-orange font-medium transition-colors"
            >
              Remove File
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <div className="relative mb-4">
              <Upload className="w-16 h-16 text-bitcoin-orange/50 group-hover:text-bitcoin-orange transition-colors duration-300" />
              {/* Animated orbital ring */}
              <div className="absolute inset-0 border-2 border-bitcoin-orange/30 rounded-full animate-spin-slow" />
            </div>
            <p className="text-white mb-2 font-medium">
              Drag and drop your file here, or click to browse
            </p>
            <p className="text-sm text-stardust mb-4">
              Supported: <span className="font-mono text-bitcoin-orange">MP4</span> video or <span className="font-mono text-bitcoin-orange">ZIP</span> dataset (max 500MB)
            </p>
            <label className="inline-block">
              <span className="px-6 py-3 bg-gradient-to-r from-burnt-orange to-bitcoin-orange text-white rounded-full cursor-pointer font-medium uppercase tracking-wider shadow-orange-glow hover:scale-105 hover:shadow-orange-glow-lg transition-all duration-300 inline-flex items-center gap-2">
                <Zap className="w-4 h-4" />
                Browse Files
              </span>
              <input
                type="file"
                accept=".mp4,.zip"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>
          </div>
        )}
      </div>

      {/* Configuration */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-mono font-medium text-stardust mb-2 uppercase tracking-wider">
            Threshold
          </label>
          <input
            type="number"
            min="0"
            max="1"
            step="0.05"
            value={threshold}
            onChange={(e) => setThreshold(parseFloat(e.target.value))}
            className="w-full h-12 px-4 bg-black/50 border-b-2 border-white/20 text-white text-sm focus-visible:border-bitcoin-orange focus-visible:outline-none focus-visible:shadow-input-focus transition-all duration-200 placeholder:text-white/30"
          />
          <p className="text-xs text-stardust/70 mt-2 font-mono">Segmentation threshold (0-1)</p>
        </div>

        <div>
          <label className="block text-sm font-mono font-medium text-stardust mb-2 uppercase tracking-wider">
            Min Area
          </label>
          <input
            type="number"
            min="0"
            step="50"
            value={minArea}
            onChange={(e) => setMinArea(parseInt(e.target.value))}
            className="w-full h-12 px-4 bg-black/50 border-b-2 border-white/20 text-white text-sm focus-visible:border-bitcoin-orange focus-visible:outline-none focus-visible:shadow-input-focus transition-all duration-200 placeholder:text-white/30"
          />
          <p className="text-xs text-stardust/70 mt-2 font-mono">Minimum component area (pixels)</p>
        </div>

        <div>
          <label className="block text-sm font-mono font-medium text-stardust mb-2 uppercase tracking-wider">
            Species <span className="text-white/30">(optional)</span>
          </label>
          <input
            type="text"
            value={species}
            onChange={(e) => setSpecies(e.target.value)}
            placeholder="e.g., E. coli"
            className="w-full h-12 px-4 bg-black/50 border-b-2 border-white/20 text-white text-sm focus-visible:border-bitcoin-orange focus-visible:outline-none focus-visible:shadow-input-focus transition-all duration-200 placeholder:text-white/30"
          />
        </div>

        <div>
          <label className="block text-sm font-mono font-medium text-stardust mb-2 uppercase tracking-wider">
            Dataset Name <span className="text-white/30">(optional)</span>
          </label>
          <input
            type="text"
            value={datasetName}
            onChange={(e) => setDatasetName(e.target.value)}
            placeholder="e.g., Experiment-01"
            className="w-full h-12 px-4 bg-black/50 border-b-2 border-white/20 text-white text-sm focus-visible:border-bitcoin-orange focus-visible:outline-none focus-visible:shadow-input-focus transition-all duration-200 placeholder:text-white/30"
          />
        </div>
      </div>

      {/* Submit Button */}
      <button
        onClick={handleSubmit}
        disabled={!selectedFile || isUploading}
        className={`mt-8 w-full h-14 rounded-full font-bold text-white uppercase tracking-widest transition-all duration-300 ${
          !selectedFile || isUploading
            ? 'bg-white/10 cursor-not-allowed opacity-50'
            : 'bg-gradient-to-r from-burnt-orange to-bitcoin-orange shadow-orange-glow hover:scale-105 hover:shadow-orange-glow-lg'
        }`}
      >
        {isUploading ? (
          <div className="flex items-center justify-center gap-3">
            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            <span>Processing...</span>
          </div>
        ) : (
          <div className="flex items-center justify-center gap-2">
            <Zap className="w-5 h-5" />
            <span>Start Analysis</span>
          </div>
        )}
      </button>
    </div>
  );
}
