"""
Job management system for tracking processing jobs.
"""
import json
import time
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
import threading
from enum import Enum


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobStage(str, Enum):
    UPLOAD = "Upload"
    PREPROCESSING = "Preprocessing"
    INFERENCE = "Inference"
    POSTPROCESSING = "Postprocessing"
    VIDEO_GENERATION = "Video Generation"
    SAVING_RESULTS = "Saving Results"


class JobManager:
    """Manages job state and progress tracking."""
    
    def __init__(self):
        self.jobs: Dict[str, Dict] = {}
        self.lock = threading.Lock()
    
    def create_job(self, job_id: str, file_type: str, filename: str) -> Dict:
        """Create a new job."""
        with self.lock:
            self.jobs[job_id] = {
                "job_id": job_id,
                "status": JobStatus.QUEUED,
                "progress": 0.0,
                "stage": JobStage.UPLOAD,
                "message": "Job queued",
                "file_type": file_type,
                "filename": filename,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "error": None,
                "results": None
            }
            return self.jobs[job_id].copy()
    
    def update_job(
        self,
        job_id: str,
        status: Optional[JobStatus] = None,
        progress: Optional[float] = None,
        stage: Optional[JobStage] = None,
        message: Optional[str] = None,
        error: Optional[str] = None,
        results: Optional[Dict] = None
    ) -> None:
        """Update job status and progress."""
        with self.lock:
            if job_id not in self.jobs:
                return
            
            job = self.jobs[job_id]
            if status is not None:
                job["status"] = status
            if progress is not None:
                job["progress"] = progress
            if stage is not None:
                job["stage"] = stage
            if message is not None:
                job["message"] = message
            if error is not None:
                job["error"] = error
            if results is not None:
                job["results"] = results
            
            job["updated_at"] = datetime.now().isoformat()
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job information."""
        with self.lock:
            return self.jobs.get(job_id, {}).copy() if job_id in self.jobs else None
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get job status for API response."""
        job = self.get_job(job_id)
        if not job:
            return None
        
        return {
            "job_id": job["job_id"],
            "status": job["status"],
            "progress": job["progress"],
            "stage": job["stage"],
            "message": job["message"],
            "error": job["error"]
        }
    
    def get_job_results(self, job_id: str) -> Optional[Dict]:
        """Get job results for API response."""
        job = self.get_job(job_id)
        if not job or job["status"] != JobStatus.COMPLETED:
            return None
        
        return job["results"]
    
    def mark_failed(self, job_id: str, error: str) -> None:
        """Mark job as failed."""
        self.update_job(
            job_id,
            status=JobStatus.FAILED,
            progress=100.0,
            error=error
        )
    
    def mark_completed(self, job_id: str, results: Dict) -> None:
        """Mark job as completed."""
        self.update_job(
            job_id,
            status=JobStatus.COMPLETED,
            progress=100.0,
            stage=JobStage.SAVING_RESULTS,
            message="Processing completed",
            results=results
        )


# Global job manager instance
job_manager = JobManager()
