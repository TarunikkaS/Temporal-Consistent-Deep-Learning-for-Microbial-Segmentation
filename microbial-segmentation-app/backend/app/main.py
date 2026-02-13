"""
FastAPI application: REST API endpoints for segmentation service.
"""
import os
import uuid
import shutil
from pathlib import Path
from typing import Optional
import threading

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import UPLOAD_DIR, OUTPUT_DIR, MAX_UPLOAD_SIZE, DEFAULT_THRESHOLD, DEFAULT_MIN_AREA
from .job_manager import job_manager, JobStatus
from .inference import InferenceEngine

# Initialize FastAPI app
app = FastAPI(
    title="Microbial Segmentation API",
    description="Temporal segmentation of microbial time-lapse videos",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for outputs
app.mount("/static", StaticFiles(directory=str(OUTPUT_DIR)), name="static")

# Initialize inference engine (lazy loading)
inference_engine = None


def get_inference_engine():
    """Get or create inference engine instance."""
    global inference_engine
    if inference_engine is None:
        inference_engine = InferenceEngine()
    return inference_engine


# Response models
class UploadResponse(BaseModel):
    job_id: str
    status: str
    message: str


class StatusResponse(BaseModel):
    job_id: str
    status: str
    progress: float
    stage: str
    message: str
    error: Optional[str] = None


class ResultsResponse(BaseModel):
    job_id: str
    status: str
    frames: list
    metrics: dict
    video_url: str
    csv_url: str
    total_frames: int
    fps: float


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Microbial Segmentation API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/api/upload",
            "status": "/api/status/{job_id}",
            "results": "/api/results/{job_id}"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    threshold: float = Form(DEFAULT_THRESHOLD),
    min_area: int = Form(DEFAULT_MIN_AREA),
    species: Optional[str] = Form(None),
    dataset_name: Optional[str] = Form(None)
):
    """
    Upload video or dataset zip for processing.
    
    Args:
        file: MP4 video or dataset zip file
        threshold: Segmentation threshold (default: 0.5)
        min_area: Minimum component area in pixels (default: 300)
        species: Optional species name
        dataset_name: Optional dataset name
    
    Returns:
        Job information with job_id
    """
    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_UPLOAD_SIZE / 1e6} MB"
        )
    
    # Validate file type
    filename = file.filename.lower()
    if filename.endswith('.mp4'):
        file_type = "video"
    elif filename.endswith('.zip'):
        file_type = "dataset"
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only .mp4 and .zip files are supported."
        )
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Save uploaded file
    upload_path = UPLOAD_DIR / job_id
    upload_path.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_path / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create job
    job = job_manager.create_job(job_id, file_type, file.filename)
    
    # Start processing in background thread
    processing_kwargs = {
        "threshold": threshold,
        "min_area": min_area,
        "species": species,
        "dataset_name": dataset_name
    }
    
    thread = threading.Thread(
        target=process_file_background,
        args=(job_id, str(file_path), file_type, processing_kwargs)
    )
    thread.daemon = True
    thread.start()
    
    return UploadResponse(
        job_id=job_id,
        status=job["status"],
        message=f"File uploaded successfully. Processing started."
    )


@app.get("/api/status/{job_id}", response_model=StatusResponse)
async def get_status(job_id: str):
    """
    Get job status and progress.
    
    Args:
        job_id: Job identifier
    
    Returns:
        Job status information
    """
    status = job_manager.get_job_status(job_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return StatusResponse(**status)


@app.get("/api/results/{job_id}")
async def get_results(job_id: str):
    """
    Get job results.
    
    Args:
        job_id: Job identifier
    
    Returns:
        Processing results with metrics and output URLs
    """
    job = job_manager.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job["status"] == JobStatus.FAILED:
        raise HTTPException(
            status_code=500,
            detail=f"Job failed: {job.get('error', 'Unknown error')}"
        )
    
    if job["status"] != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=202,
            detail=f"Job still processing. Status: {job['status']}"
        )
    
    results = job_manager.get_job_results(job_id)
    
    if not results:
        raise HTTPException(status_code=404, detail="Results not found")
    
    return JSONResponse(content=results)


@app.post("/api/process-example")
async def process_example(
    example_id: str = Form(...),
    threshold: float = Form(DEFAULT_THRESHOLD),
    min_area: int = Form(DEFAULT_MIN_AREA)
):
    """
    Process a preloaded example dataset.
    
    Args:
        example_id: Example dataset identifier
        threshold: Segmentation threshold
        min_area: Minimum component area
    
    Returns:
        Job information with job_id
    """
    # Map example IDs to actual dataset paths
    example_paths = {
        "lysobacter_dataset1": "/Users/tarunikkasuresh/untitled folder/Lysobacter/Time-lapse_dataset1",
        "lysobacter_dataset2": "/Users/tarunikkasuresh/untitled folder/Lysobacter/Time-lapse_dataset2",
        "pputida_dataset1": "/Users/tarunikkasuresh/untitled folder/Pputida/Time-lapse_dataset1",
        "pputida_dataset2": "/Users/tarunikkasuresh/untitled folder/Pputida/Time-lapse_dataset2",
        "pveronii_dataset1": "/Users/tarunikkasuresh/untitled folder/Pveronii/Time-lapse_dataset1",
        "pveronii_dataset2": "/Users/tarunikkasuresh/untitled folder/Pveronii/Time-lapse_dataset2",
        "rahnella_dataset1": "/Users/tarunikkasuresh/untitled folder/Rahnella/Time-lapse_dataset1",
        "rahnella_dataset2": "/Users/tarunikkasuresh/untitled folder/Rahnella/Time-lapse_dataset2"
    }
    
    # Extract species from example_id
    species_map = {
        "lysobacter": "Lysobacter",
        "pputida": "Pputida", 
        "pveronii": "Pveronii",
        "rahnella": "Rahnella"
    }
    species_key = example_id.split("_")[0]
    species = species_map.get(species_key, "Unknown")
    
    if example_id not in example_paths:
        raise HTTPException(status_code=404, detail=f"Example {example_id} not found")
    
    dataset_path = Path(example_paths[example_id])
    if not dataset_path.exists():
        raise HTTPException(status_code=404, detail=f"Dataset path does not exist: {dataset_path}")
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Create job
    job = job_manager.create_job(job_id, "dataset", example_id)
    
    # Start processing in background thread
    processing_kwargs = {
        "threshold": threshold,
        "min_area": min_area,
        "species": species,
        "dataset_name": example_id
    }
    
    thread = threading.Thread(
        target=process_example_background,
        args=(job_id, str(dataset_path), processing_kwargs)
    )
    thread.daemon = True
    thread.start()
    
    return UploadResponse(
        job_id=job_id,
        status=job["status"],
        message=f"Processing example {example_id}"
    )


@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str):
    """
    Delete job and its outputs.
    
    Args:
        job_id: Job identifier
    
    Returns:
        Deletion confirmation
    """
    job = job_manager.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Delete upload files
    upload_path = UPLOAD_DIR / job_id
    if upload_path.exists():
        shutil.rmtree(upload_path)
    
    # Delete output files
    output_path = OUTPUT_DIR / job_id
    if output_path.exists():
        shutil.rmtree(output_path)
    
    return {"message": f"Job {job_id} deleted successfully"}


def process_file_background(job_id: str, file_path: str, file_type: str, kwargs: dict):
    """
    Background task for processing uploaded file.
    
    Args:
        job_id: Job identifier
        file_path: Path to uploaded file
        file_type: 'video' or 'dataset'
        kwargs: Additional processing parameters
    """
    try:
        engine = get_inference_engine()
        
        if file_type == "video":
            results = engine.process_video(file_path, job_id, **kwargs)
        elif file_type == "dataset":
            results = engine.process_dataset(file_path, job_id, **kwargs)
        else:
            raise ValueError(f"Unknown file type: {file_type}")
        
        # Cleanup upload
        upload_path = UPLOAD_DIR / job_id
        if upload_path.exists():
            shutil.rmtree(upload_path)
            
    except Exception as e:
        job_manager.mark_failed(job_id, str(e))
        print(f"Error processing job {job_id}: {e}")


def process_example_background(job_id: str, dataset_path: str, kwargs: dict):
    """
    Background task for processing preloaded example dataset.
    
    Args:
        job_id: Job identifier
        dataset_path: Path to example dataset directory
        kwargs: Additional processing parameters
    """
    try:
        engine = get_inference_engine()
        results = engine.process_dataset(dataset_path, job_id, **kwargs)
            
    except Exception as e:
        job_manager.mark_failed(job_id, str(e))
        print(f"Error processing example job {job_id}: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
