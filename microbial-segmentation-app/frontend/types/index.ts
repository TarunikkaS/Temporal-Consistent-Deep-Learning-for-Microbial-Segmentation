export interface JobStatus {
  job_id: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  progress: number;
  stage: string;
  message: string;
  error?: string;
}

export interface PhenotypeCounts {
  rod_like: number;
  elongated: number;
  compact: number;
  other: number;
}

export interface Metrics {
  time: number[];
  area_pred: number[];
  area_gt?: number[];
  growth_pred: number[];
  division_like: number[];
  component_count?: number[];
  phenotype_counts?: PhenotypeCounts[];
}

export interface JobResults {
  job_id: string;
  n_frames: number;
  fps: number;
  triplet_frames: string[];
  orig_frames: string[];
  pred_frames: string[];
  gt_frames: (string | null)[];
  video_url: string;
  csv_url: string;
  metrics: Metrics;
}

export interface UploadResponse {
  job_id: string;
  status: string;
  message: string;
}

export type AppState = 'idle' | 'uploading' | 'running' | 'results' | 'error';
