'use client';

import React, { useState, useEffect } from 'react';
import { Download, RefreshCw, Microscope, Upload as UploadIcon, Database } from 'lucide-react';
import UploadSection, { UploadConfig } from '@/components/UploadSection';
import ExamplesGallery from '@/components/ExamplesGallery';
import ProgressBar from '@/components/ProgressBar';
import FrameViewer from '@/components/FrameViewer';
import BiomassChart from '@/components/BiomassChart';
import PhenotypeChart from '@/components/PhenotypeChart';
import DivisionTimeline from '@/components/DivisionTimeline';
import { uploadFile, getJobStatus, getJobResults, processExample } from '@/lib/api';
import { AppState, JobStatus, JobResults } from '@/types';

type TabType = 'upload' | 'examples';

export default function Home() {
  const [activeTab, setActiveTab] = useState<TabType>('examples');
  const [appState, setAppState] = useState<AppState>('idle');
  const [jobId, setJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const [results, setResults] = useState<JobResults | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Poll for job status
  useEffect(() => {
    if (jobId && appState === 'running') {
      const pollInterval = setInterval(async () => {
        try {
          const status = await getJobStatus(jobId);
          setJobStatus(status);

          if (status.status === 'completed') {
            // Fetch results
            const jobResults = await getJobResults(jobId);
            setResults(jobResults);
            setAppState('results');
            clearInterval(pollInterval);
          } else if (status.status === 'failed') {
            setError(status.error || 'Processing failed');
            setAppState('error');
            clearInterval(pollInterval);
          }
        } catch (err: any) {
          console.error('Error polling status:', err);
        }
      }, 2000); // Poll every 2 seconds

      return () => clearInterval(pollInterval);
    }
  }, [jobId, appState]);

  const handleUpload = async (file: File, config: UploadConfig) => {
    try {
      setAppState('uploading');
      setError(null);

      const response = await uploadFile(
        file,
        config.threshold,
        config.minArea,
        config.species,
        config.datasetName
      );

      setJobId(response.job_id);
      setAppState('running');
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Upload failed');
      setAppState('error');
    }
  };

  const handleSelectExample = async (exampleId: string) => {
    try {
      setAppState('uploading');
      setError(null);
      
      const response = await processExample(exampleId);
      setJobId(response.job_id);
      setAppState('running');
      
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load example');
      setAppState('error');
    }
  };

  const handleReset = () => {
    setAppState('idle');
    setJobId(null);
    setJobStatus(null);
    setResults(null);
    setError(null);
    setActiveTab('examples');
  };

  const handleDownload = (url: string, filename: string) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen py-24 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="flex items-center justify-center gap-4 mb-6">
            <div className="relative">
              <Microscope className="w-16 h-16 text-bitcoin-orange" />
              {/* Animated glow */}
              <div className="absolute inset-0 blur-lg">
                <Microscope className="w-16 h-16 text-bitcoin-orange opacity-50 animate-pulse" />
              </div>
            </div>
            <h1 className="text-4xl sm:text-5xl md:text-7xl font-heading font-bold text-white leading-tight">
              Microbial <span className="gradient-text">Segmentation</span>
            </h1>
          </div>
          <p className="text-stardust max-w-2xl mx-auto text-base md:text-lg leading-relaxed">
            Automated temporal segmentation of microbial time-lapse videos using
            deep learning. Upload your video or dataset to analyze cell growth,
            phenotypes, and <span className="text-bitcoin-orange font-semibold">division events</span>.
          </p>
        </div>

        {/* Error Display */}
        {appState === 'error' && (
          <div className="mb-8 p-6 bg-red-500/10 border border-red-500/50 rounded-2xl backdrop-blur-sm shadow-[0_0_20px_rgba(239,68,68,0.3)]">
            <h3 className="text-red-400 font-heading font-semibold mb-2 flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Error
            </h3>
            <p className="text-red-300 text-sm mb-4">{error}</p>
            <button
              onClick={handleReset}
              className="px-6 py-2 bg-red-500/20 border border-red-500/50 text-red-400 rounded-full hover:bg-red-500/30 hover:border-red-500 transition-all duration-300 font-medium uppercase text-sm tracking-wider"
            >
              Go Back
            </button>
          </div>
        )}

        {/* Tab Navigation */}
        {(appState === 'idle' || appState === 'uploading') && (
          <div className="mb-8">
            <div className="flex border-b border-white/10">
              <button
                onClick={() => setActiveTab('examples')}
                className={`flex items-center gap-2 px-6 py-4 font-mono font-medium uppercase text-sm tracking-widest transition-all duration-300 ${
                  activeTab === 'examples'
                    ? 'border-b-2 border-bitcoin-orange text-bitcoin-orange shadow-[0_4px_12px_-4px_rgba(247,147,26,0.5)]'
                    : 'text-stardust hover:text-white border-b-2 border-transparent'
                }`}
              >
                <Database className="w-5 h-5" />
                Examples
              </button>
              <button
                onClick={() => setActiveTab('upload')}
                className={`flex items-center gap-2 px-6 py-4 font-mono font-medium uppercase text-sm tracking-widest transition-all duration-300 ${
                  activeTab === 'upload'
                    ? 'border-b-2 border-bitcoin-orange text-bitcoin-orange shadow-[0_4px_12px_-4px_rgba(247,147,26,0.5)]'
                    : 'text-stardust hover:text-white border-b-2 border-transparent'
                }`}
              >
                <UploadIcon className="w-5 h-5" />
                Upload
              </button>
            </div>
          </div>
        )}

        {/* Tab Content */}
        {(appState === 'idle' || appState === 'uploading') && (
          <>
            {activeTab === 'examples' && (
              <ExamplesGallery onSelectExample={handleSelectExample} />
            )}
            {activeTab === 'upload' && (
              <UploadSection
                onUpload={handleUpload}
                isUploading={appState === 'uploading'}
              />
            )}
          </>
        )}

        {/* Progress Section */}
        {appState === 'running' && jobStatus && (
          <div className="mb-6">
            <ProgressBar status={jobStatus} />
          </div>
        )}

        {/* Results Section */}
        {appState === 'results' && results && (
          <div>
            {/* Action Buttons */}
            <div className="mb-12 flex flex-wrap gap-4 justify-center">
              <button
                onClick={() => handleDownload(results.video_url, 'overlay_video.mp4')}
                className="flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-burnt-orange to-bitcoin-orange text-white rounded-full font-bold uppercase tracking-widest shadow-orange-glow hover:scale-105 hover:shadow-orange-glow-lg transition-all duration-300"
              >
                <Download className="w-5 h-5" />
                Video
              </button>
              
              <button
                onClick={() => handleDownload(results.csv_url, 'metrics.csv')}
                className="flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-bitcoin-orange to-digital-gold text-white rounded-full font-bold uppercase tracking-widest shadow-gold-glow hover:scale-105 hover:shadow-gold-glow transition-all duration-300"
              >
                <Download className="w-5 h-5" />
                Data CSV
              </button>
              
              <button
                onClick={handleReset}
                className="flex items-center gap-2 px-8 py-4 bg-white/10 border-2 border-white/20 text-white rounded-full font-bold uppercase tracking-widest hover:bg-white/20 hover:border-bitcoin-orange/50 transition-all duration-300"
              >
                <RefreshCw className="w-5 h-5" />
                New Analysis
              </button>
            </div>

            {/* Video Player */}
            <div className="mb-8 bg-dark-matter rounded-2xl border border-white/10 p-8 shadow-card-elevation">
              <h3 className="text-2xl font-heading font-semibold text-white mb-6 flex items-center gap-2">
                <span className="text-bitcoin-orange">━</span> Video Output
              </h3>
              <div className="bg-black rounded-xl overflow-hidden border border-white/10">
                <video controls className="w-full" src={results.video_url}>
                  Your browser does not support the video tag.
                </video>
              </div>
            </div>

            {/* Results Grid */}
            <div className="space-y-8">
              {/* Frame Viewer */}
              <FrameViewer
                orig_frames={results.orig_frames}
                gt_frames={results.gt_frames}
                pred_frames={results.pred_frames}
                triplet_frames={results.triplet_frames}
                n_frames={results.n_frames}
                fps={results.fps}
                metrics={results.metrics}
              />

              {/* Charts Row 1 */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <BiomassChart metrics={results.metrics} />
                <PhenotypeChart metrics={results.metrics} />
              </div>

              {/* Charts Row 2 */}
              <div className="grid grid-cols-1 gap-6">
                <DivisionTimeline metrics={results.metrics} />
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="mt-24 text-center border-t border-white/10 pt-12">
          <p className="text-stardust font-mono text-sm mb-2">
            Powered by <span className="text-bitcoin-orange font-semibold">UNetTemporalFlow</span> with track-consistency fine-tuning
          </p>
          <p className="text-stardust/70 text-xs font-mono">
            Built with <span className="text-white">Next.js</span> · <span className="text-white">FastAPI</span> · <span className="text-white">PyTorch</span>
          </p>
        </div>
      </div>
    </div>
  );
}
