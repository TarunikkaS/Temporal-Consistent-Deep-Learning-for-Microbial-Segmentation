# System Architecture

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                            │
│                    http://localhost:3000                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ HTTP/REST API
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js 14)                        │
├─────────────────────────────────────────────────────────────────┤
│  Components:                                                     │
│  • UploadSection      → File upload & config                    │
│  • ProgressBar        → Real-time status                        │
│  • ResultsViewer      → Frame player                            │
│  • BiomassChart       → Growth visualization                    │
│  • PhenotypeChart     → Cell type distribution                  │
│  • DivisionTimeline   → Event detection                         │
│                                                                  │
│  State Management:                                               │
│  idle → uploading → running → results                           │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ API Calls
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                             │
│                   http://localhost:8000                          │
├─────────────────────────────────────────────────────────────────┤
│  Endpoints:                                                      │
│  • POST /api/upload        → Initiate job                       │
│  • GET  /api/status/{id}   → Poll progress                      │
│  • GET  /api/results/{id}  → Fetch results                      │
│  • Static /outputs/        → Serve files                        │
│                                                                  │
│  Job Manager:                                                    │
│  • Thread-safe job tracking                                     │
│  • Progress updates (0-100%)                                    │
│  • Stage tracking                                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ Process in background thread
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Inference Pipeline                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. INPUT HANDLING                                              │
│     ├─ Video (.mp4) → Extract frames                           │
│     └─ Dataset (.zip) → Extract images + masks                 │
│                                                                  │
│  2. PREPROCESSING                                               │
│     ├─ Convert to grayscale                                     │
│     ├─ Normalize to [0,1]                                       │
│     └─ Create temporal windows (T=5)                            │
│                                                                  │
│  3. OPTICAL FLOW                                                │
│     ├─ Compute flow between consecutive frames                 │
│     ├─ Farneback algorithm (OpenCV)                            │
│     └─ Generate 8 flow channels (dx,dy × 4)                    │
│                                                                  │
│  4. INPUT CONSTRUCTION                                          │
│     ├─ Stack 5 grayscale frames                                │
│     ├─ Stack 8 optical flow channels                           │
│     └─ Create 13-channel tensor [1,13,H,W]                     │
│                                                                  │
│  5. DEEP LEARNING INFERENCE                                     │
│     ┌─────────────────────────────────────┐                   │
│     │    UNetTemporalFlow Model           │                   │
│     │  ┌───────────────────────────────┐  │                   │
│     │  │  Encoder (Down sampling)      │  │                   │
│     │  │  • DoubleConv + MaxPool       │  │                   │
│     │  │  • 64 → 128 → 256 → 512       │  │                   │
│     │  └───────────┬───────────────────┘  │                   │
│     │              ↓                       │                   │
│     │  ┌───────────────────────────────┐  │                   │
│     │  │  Bottleneck                   │  │                   │
│     │  │  • 1024 channels              │  │                   │
│     │  │  • Temporal Attention         │  │                   │
│     │  └───────────┬───────────────────┘  │                   │
│     │              ↓                       │                   │
│     │  ┌───────────────────────────────┐  │                   │
│     │  │  Decoder (Up sampling)        │  │                   │
│     │  │  • UpConv + Skip connections  │  │                   │
│     │  │  • 512 → 256 → 128 → 64       │  │                   │
│     │  └───────────┬───────────────────┘  │                   │
│     │              ↓                       │                   │
│     │  ┌───────────────────────────────┐  │                   │
│     │  │  Output Conv                  │  │                   │
│     │  │  • 1 channel (mask)           │  │                   │
│     │  └───────────────────────────────┘  │                   │
│     └─────────────────────────────────────┘                   │
│     Output: [1,1,H,W] logits → sigmoid → [0,1]                │
│                                                                  │
│  6. POST-PROCESSING                                             │
│     ├─ Threshold at 0.5 → binary mask                          │
│     ├─ Remove small components (< min_area)                    │
│     ├─ Morphological cleaning                                  │
│     └─ Connected component labeling                            │
│                                                                  │
│  7. ANALYSIS                                                    │
│     ├─ Biomass: sum of foreground pixels                       │
│     ├─ Growth rate: log(biomass[t] / biomass[t-1])            │
│     ├─ Phenotype classification:                               │
│     │   ├─ Rod-like (green)                                    │
│     │   ├─ Elongated (cyan)                                    │
│     │   ├─ Compact (blue)                                      │
│     │   └─ Other (yellow)                                      │
│     └─ Division detection:                                      │
│         ├─ Growth spike (> mean + 2σ)                          │
│         └─ Topology change (component↑)                        │
│                                                                  │
│  8. VISUALIZATION                                               │
│     ├─ Render overlay on original frame                        │
│     ├─ Color-code by phenotype                                 │
│     ├─ Add labels and markers                                  │
│     └─ Mark division events                                    │
│                                                                  │
│  9. OUTPUT GENERATION                                           │
│     ├─ Save overlay frames as PNG                              │
│     ├─ Create video from frames (MP4)                          │
│     └─ Export metrics to CSV                                   │
│                                                                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ Save to disk
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      File System                                 │
├─────────────────────────────────────────────────────────────────┤
│  outputs/                                                        │
│    └── {job_id}/                                                │
│        ├── frames/                                              │
│        │   ├── frame_0001.png                                   │
│        │   ├── frame_0002.png                                   │
│        │   └── ...                                              │
│        ├── overlay.mp4                                          │
│        └── metrics.csv                                          │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Upload Flow
```
User → Upload File → Frontend → POST /api/upload
                                      ↓
                                 Create Job ID
                                      ↓
                                 Start Background Thread
                                      ↓
                                 Return Job ID
                                      ↓
                                 Frontend starts polling
```

### Processing Flow
```
Background Thread:
1. Load file from disk
2. Extract frames/masks
3. For each temporal window:
   a. Build 13-channel input
   b. Run model inference
   c. Post-process mask
   d. Analyze frame
   e. Update progress
4. Detect division events
5. Generate overlays
6. Create video
7. Save metrics CSV
8. Mark job complete
```

### Results Flow
```
Frontend polling → GET /api/status/{id}
                        ↓
                   Job complete?
                        ↓
              GET /api/results/{id}
                        ↓
              Display results + charts
                        ↓
              User downloads video/CSV
```

## Technology Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **HTTP Client**: Axios

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.9+
- **Deep Learning**: PyTorch
- **Computer Vision**: OpenCV
- **Image Processing**: Pillow, scikit-image
- **Data**: NumPy, Pandas
- **Server**: Uvicorn

### Infrastructure
- **Job Management**: Threading + in-memory store
- **File Storage**: Local filesystem
- **API**: RESTful HTTP/JSON
- **Static Files**: FastAPI StaticFiles

## Key Algorithms

### Optical Flow (Farneback)
```python
flow = cv2.calcOpticalFlowFarneback(
    frame1, frame2,
    pyr_scale=0.5,    # Pyramid scale
    levels=3,          # Pyramid levels
    winsize=15,        # Window size
    iterations=3,      # Iterations at each level
    poly_n=5,          # Polynomial expansion
    poly_sigma=1.2     # Gaussian sigma
)
```

### Phenotype Classification
```python
aspect_ratio = major_axis / minor_axis

if aspect_ratio >= 3.0:
    → Elongated
elif aspect_ratio >= 2.0:
    → Rod-like
elif aspect_ratio < 1.8 and solidity >= 0.8:
    → Compact
else:
    → Other
```

### Division Detection
```python
growth_spike = growth_rate[t] > (mean + 2*std)
topology_change = component_count[t] - component_count[t-1] >= 1

if growth_spike AND topology_change:
    → Division event at frame t
```

## Performance Characteristics

- **Throughput**: ~5-10 frames/second on GPU
- **Memory**: ~2-4 GB for typical videos
- **Latency**: 
  - Upload: < 1s
  - Processing: 5-15 min for 200 frame video
  - Results retrieval: < 1s

## Scalability Considerations

Current implementation uses:
- In-memory job storage (not persistent)
- Local file system
- Single-threaded processing per job

For production scale:
- Add Redis for job queue
- Use cloud storage (S3/GCS)
- Implement worker pools
- Add database for job history
- Add authentication/authorization
