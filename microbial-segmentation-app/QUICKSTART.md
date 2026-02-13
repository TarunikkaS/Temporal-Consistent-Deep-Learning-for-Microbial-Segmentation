# Quick Start Guide

## Prerequisites

- Python 3.9+
- Node.js 18+
- Model checkpoint: `temporal_unet_TC_finetuned.pt`

## Backend Setup (5 minutes)

```bash
# Navigate to backend
cd microbial-segmentation-app/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy your model checkpoint to backend folder
cp /path/to/temporal_unet_TC_finetuned.pt ./temporal_unet_TC_finetuned.pt

# Create directories
mkdir -p uploads outputs

# Start backend server
chmod +x run.sh
./run.sh
# Or: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at http://localhost:8000

## Frontend Setup (3 minutes)

Open a new terminal:

```bash
# Navigate to frontend
cd microbial-segmentation-app/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at http://localhost:3000

## Testing

### Test backend inference:

```bash
cd microbial-segmentation-app/scripts
python test_local.py \
  --input /path/to/video.mp4 \
  --checkpoint ../backend/temporal_unet_TC_finetuned.pt \
  --max-frames 50
```

### Test with dataset:

```bash
python test_local.py \
  --input /path/to/dataset.zip \
  --checkpoint ../backend/temporal_unet_TC_finetuned.pt \
  --threshold 0.5 \
  --min-area 300
```

## Using the Application

1. **Open browser** → http://localhost:3000

2. **Upload file:**
   - Drag & drop MP4 video or ZIP dataset
   - OR click "Browse Files"

3. **Configure parameters:**
   - Threshold: 0.5 (adjust for sensitivity)
   - Min Area: 300 pixels (filter small noise)
   - Species & Dataset name (optional)

4. **Click "Run Segmentation"**
   - Monitor progress bar
   - Wait for processing (can take 5-15 minutes depending on video length)

5. **View results:**
   - Frame-by-frame overlay player
   - Biomass growth chart
   - Phenotype distribution
   - Division-like event timeline

6. **Download outputs:**
   - Overlay video (MP4)
   - Metrics CSV

## Troubleshooting

### Backend won't start:
```bash
# Check if port 8000 is in use
lsof -i :8000
# Kill process if needed
kill -9 <PID>
```

### Frontend won't start:
```bash
# Check if port 3000 is in use
lsof -i :3000
# Or run on different port
npm run dev -- -p 3001
```

### Model loading error:
- Verify checkpoint path in backend folder
- Check model architecture matches training
- Try CPU mode: set `DEVICE=cpu` in .env

### Out of memory:
- Reduce video resolution
- Process fewer frames at once
- Use CPU instead of GPU

### Low IoU scores:
- Adjust threshold (try 0.3-0.7)
- Modify min_area (try 100-500)
- Check frame normalization

## Production Deployment

### Backend:
```bash
# Use production ASGI server
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend:
```bash
# Build for production
npm run build
npm run start
```

### Docker (optional):

Create `backend/Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `frontend/Dockerfile`:
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json .
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

Docker Compose:
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/outputs:/app/outputs
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
```

## API Documentation

Once backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Support

For issues or questions, check:
- README.md for detailed documentation
- Backend logs in terminal
- Browser console for frontend errors
- Network tab for API calls
