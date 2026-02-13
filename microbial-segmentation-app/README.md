# Microbial Segmentation Application

Full-stack application for temporal segmentation of microbial time-lapse videos using a pretrained UNet model with track-consistency fine-tuning.

## Features

- 🎥 Upload MP4 videos or dataset ZIP files
- 🧬 Temporal segmentation with optical flow integration
- 📊 Real-time biomass tracking and growth rate analysis
- 🎨 Phenotype classification (rod-like, elongated, compact)
- 🔬 Division-like event detection
- 📈 Interactive visualizations and metrics
- 💾 Downloadable results (video + CSV)

## Tech Stack

**Frontend:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Recharts for visualizations

**Backend:**
- FastAPI (Python 3.9+)
- PyTorch for inference
- OpenCV for video processing
- Pillow for image manipulation

## Project Structure

```
microbial-segmentation-app/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app and endpoints
│   │   ├── models.py            # UNetTemporalFlow architecture
│   │   ├── inference.py         # Inference pipeline
│   │   ├── preprocessing.py     # Optical flow & input builder
│   │   ├── postprocessing.py    # Cleaning, phenotype, division detection
│   │   ├── video_utils.py       # Video I/O utilities
│   │   ├── job_manager.py       # Job tracking and status
│   │   └── config.py            # Configuration
│   ├── outputs/                 # Generated outputs (job-based)
│   ├── uploads/                 # Temporary uploads
│   ├── requirements.txt
│   └── run.sh
├── frontend/
│   ├── app/
│   │   ├── page.tsx            # Main page
│   │   ├── layout.tsx          # Root layout
│   │   └── api/                # API proxy (optional)
│   ├── components/
│   │   ├── UploadSection.tsx   # File upload UI
│   │   ├── ProgressBar.tsx     # Job progress
│   │   ├── ResultsViewer.tsx   # Frame gallery + player
│   │   ├── BiomassChart.tsx    # Biomass over time
│   │   ├── PhenotypeChart.tsx  # Phenotype distribution
│   │   └── DivisionTimeline.tsx # Division events
│   ├── lib/
│   │   └── api.ts              # API client
│   ├── types/
│   │   └── index.ts            # TypeScript types
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── next.config.js
├── scripts/
│   └── test_local.py           # Local testing script
├── .env.example
└── README.md
```

## Installation

### Prerequisites

- Python 3.9+
- Node.js 18+
- PyTorch (CPU or GPU)
- Model checkpoint: `temporal_unet_TC_finetuned.pt`

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create necessary directories
mkdir -p uploads outputs

# Copy your model checkpoint
cp /path/to/temporal_unet_TC_finetuned.pt ./temporal_unet_TC_finetuned.pt
```

### Frontend Setup

```bash
cd frontend
npm install
```

### Environment Configuration

Create `.env` file in project root:

```env
# Backend
MODEL_PATH=backend/temporal_unet_TC_finetuned.pt
UPLOAD_DIR=backend/uploads
OUTPUT_DIR=backend/outputs
MAX_UPLOAD_SIZE=500000000
DEVICE=cuda  # or cpu

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running the Application

### Start Backend (Terminal 1)

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at `http://localhost:8000`

### Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

Frontend will be available at `http://localhost:3000`

## Usage

1. **Open browser** to `http://localhost:3000`

2. **Upload file:**
   - MP4 video of microbial time-lapse, OR
   - ZIP file with dataset structure (STRack-like)

3. **Configure parameters:**
   - Threshold (default: 0.5)
   - Min area (default: 300 pixels)
   - Species name (optional)

4. **Run segmentation** - Monitor progress bar

5. **View results:**
   - Frame-by-frame overlay player
   - Biomass growth chart
   - Phenotype distribution over time
   - Division-like event markers

6. **Download outputs:**
   - Overlay video (MP4)
   - Metrics CSV (time, biomass, growth rate, phenotypes, division events)

## API Endpoints

### POST `/api/upload`
Upload video or dataset zip for processing.

**Body (multipart/form-data):**
- `file`: video file (mp4) or dataset zip
- `threshold`: float (default: 0.5)
- `min_area`: int (default: 300)
- `species`: string (optional)
- `dataset_name`: string (optional)

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "queued"
}
```

### GET `/api/status/{job_id}`
Get job progress and current stage.

**Response:**
```json
{
  "job_id": "uuid",
  "status": "running",
  "progress": 45.5,
  "stage": "Inference",
  "message": "Processing frame 91/200"
}
```

### GET `/api/results/{job_id}`
Get final results and metrics.

**Response:**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "frames": ["/outputs/uuid/frames/frame_0001.png", ...],
  "metrics": {
    "time": [0, 1, 2, ...],
    "biomass_pred": [1500, 1520, ...],
    "biomass_gt": [1480, 1510, ...],
    "growth_rate": [0.013, 0.012, ...],
    "phenotype_counts": [
      {"rod_like": 5, "elongated": 2, "compact": 1, "other": 0},
      ...
    ],
    "division_events": [45, 78, 132]
  },
  "video_url": "/outputs/uuid/overlay.mp4",
  "csv_url": "/outputs/uuid/metrics.csv"
}
```

## Testing

Run local inference test:

```bash
cd scripts
python test_local.py --input /path/to/video.mp4 --checkpoint ../backend/temporal_unet_TC_finetuned.pt
```

## Model Details

**Architecture:** UNetTemporalFlow
- Input: 13 channels (5 grayscale frames + 8 optical flow channels)
- Output: 1 channel (binary segmentation mask)
- Temporal attention at bottleneck
- Skip connections for spatial detail preservation

**Preprocessing:**
- Frames normalized to [0, 1]
- Optical flow computed using Farneback method
- Temporal window: T=5 frames

**Post-processing:**
- Small component removal (< 300 pixels)
- Morphological cleaning
- Connected component analysis for phenotype classification

## Phenotype Classification

- **Rod-like** (green): aspect ratio ≥ 2.0, moderate area
- **Elongated** (cyan): aspect ratio ≥ 3.0 or high skeleton length
- **Compact** (blue): aspect ratio < 1.8, high solidity
- **Other** (yellow): remaining cells

## Division-like Event Detection

Events detected when:
1. Growth spike: growth_rate > mean + 2×std
2. Topology change: component_count increases by ≥1

## Troubleshooting

**Model fails to load:**
- Verify checkpoint path in `.env`
- Check model architecture matches training configuration

**Low IoU scores:**
- Adjust threshold parameter
- Check frame normalization
- Verify optical flow computation

**Out of memory:**
- Reduce batch processing size
- Use CPU instead of GPU for smaller datasets
- Process fewer frames at once

## License

MIT License
