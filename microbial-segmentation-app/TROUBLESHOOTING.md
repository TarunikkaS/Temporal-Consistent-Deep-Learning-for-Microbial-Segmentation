# Troubleshooting Guide

## Common Issues and Solutions

### Installation Issues

#### Issue: `pip install` fails with PyTorch
**Solution:**
```bash
# For CPU-only (Mac/Windows without CUDA):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# For CUDA 11.8:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

#### Issue: `npm install` fails
**Solution:**
```bash
# Clear cache and retry
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

#### Issue: Python virtual environment activation fails
**Solution:**
```bash
# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# If still failing, recreate:
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

### Backend Issues

#### Issue: "Model checkpoint not found"
**Solution:**
```bash
# Verify checkpoint location:
ls -la backend/temporal_unet_TC_finetuned.pt

# Copy if needed:
cp /path/to/temporal_unet_TC_finetuned.pt backend/

# Or update .env:
MODEL_PATH=/absolute/path/to/temporal_unet_TC_finetuned.pt
```

#### Issue: "CUDA out of memory"
**Solutions:**
1. Use CPU mode:
   ```bash
   # In .env:
   DEVICE=cpu
   ```

2. Process fewer frames at once (modify inference.py if needed)

3. Reduce video resolution before uploading

#### Issue: Port 8000 already in use
**Solution:**
```bash
# Find and kill the process:
lsof -ti:8000 | xargs kill -9

# Or use a different port:
uvicorn app.main:app --port 8001
```

#### Issue: "Module not found" errors
**Solution:**
```bash
# Ensure virtual environment is activated:
which python  # Should show venv/bin/python

# Reinstall requirements:
pip install -r requirements.txt

# If still failing, check Python path:
export PYTHONPATH="${PYTHONPATH}:/path/to/backend"
```

#### Issue: "Permission denied" when creating directories
**Solution:**
```bash
# Create directories manually with proper permissions:
mkdir -p backend/uploads backend/outputs
chmod 755 backend/uploads backend/outputs
```

### Frontend Issues

#### Issue: Port 3000 already in use
**Solution:**
```bash
# Kill process on port 3000:
lsof -ti:3000 | xargs kill -9

# Or use different port:
npm run dev -- -p 3001
```

#### Issue: "Cannot connect to backend" / API errors
**Solutions:**
1. Verify backend is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check CORS settings in backend/app/main.py

3. Update API URL in frontend/.env:
   ```bash
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

#### Issue: TypeScript errors
**Solution:**
```bash
# Regenerate type definitions:
npm run build

# Or run with type checking disabled (not recommended):
npm run dev --no-type-check
```

#### Issue: Tailwind styles not applying
**Solution:**
```bash
# Rebuild Tailwind:
npm run build

# Clear Next.js cache:
rm -rf .next
npm run dev
```

### Processing Issues

#### Issue: "No frames found in dataset"
**Solutions:**
1. Verify ZIP structure:
   ```bash
   unzip -l dataset.zip
   ```
   
   Should contain:
   ```
   Species/
     Species/
       Time-lapse_datasetX/
         raw_images/*.tif
         manual_segmentation_masks/*.tif
   ```

2. Check supported formats: .tif, .tiff, .png, .jpg

3. Ensure images are not corrupted

#### Issue: Low IoU / Poor segmentation results
**Solutions:**
1. Adjust threshold:
   ```
   Try values: 0.3, 0.4, 0.5, 0.6, 0.7
   ```

2. Modify min_area:
   ```
   Try values: 100, 200, 300, 500
   ```

3. Check input normalization:
   - Frames should be [0, 1]
   - Optical flow should be reasonable magnitude

4. Verify model architecture matches training

#### Issue: "Division events not detected"
**Possible causes:**
1. Growth rate variation is small
2. No topology changes (component count constant)
3. Adjust detection thresholds in config.py:
   ```python
   DIVISION_GROWTH_SPIKE_STD = 1.5  # Lower = more sensitive
   DIVISION_COMPONENT_INCREASE = 1
   ```

#### Issue: Video generation fails
**Solutions:**
1. Check OpenCV installation:
   ```bash
   python -c "import cv2; print(cv2.__version__)"
   ```

2. Install additional codecs:
   ```bash
   pip install opencv-python-headless
   ```

3. Try different codec in video_utils.py:
   ```python
   # Change from 'mp4v' to:
   codec = 'avc1'  # or 'x264'
   ```

### Performance Issues

#### Issue: Processing is very slow
**Solutions:**
1. Use GPU if available (check DEVICE=cuda in .env)

2. Reduce video resolution before uploading

3. Process fewer frames (limit in inference pipeline)

4. Check system resources:
   ```bash
   # CPU usage
   top
   
   # GPU usage (if NVIDIA)
   nvidia-smi
   ```

#### Issue: High memory usage
**Solutions:**
1. Process in smaller batches

2. Clear old outputs:
   ```bash
   rm -rf backend/outputs/*
   rm -rf backend/uploads/*
   ```

3. Restart backend server periodically

### Data Issues

#### Issue: "Invalid file type"
**Supported formats:**
- Videos: .mp4 only
- Datasets: .zip only

**Solution:**
Convert your video:
```bash
ffmpeg -i input.avi output.mp4
```

#### Issue: File too large (> 500MB)
**Solutions:**
1. Compress video:
   ```bash
   ffmpeg -i input.mp4 -vcodec h264 -acodec mp2 output.mp4
   ```

2. Reduce resolution:
   ```bash
   ffmpeg -i input.mp4 -vf scale=640:480 output.mp4
   ```

3. Increase limit in .env:
   ```
   MAX_UPLOAD_SIZE=1000000000  # 1GB
   ```

### Optical Flow Issues

#### Issue: Flow computation is slow
**Solutions:**
1. Try DIS flow instead:
   ```python
   # In preprocessing.py, change method:
   flow_method="dis"
   ```

2. Reduce flow parameters (lower quality but faster)

3. Use CPU for flow, GPU for model

#### Issue: Flow values seem wrong
**Check:**
1. Frame normalization (should be [0,1])
2. Frame conversion to uint8 for OpenCV
3. Flow magnitude is reasonable (typically -20 to +20)

### Job Management Issues

#### Issue: Job stuck in "running" state
**Solutions:**
1. Check backend logs for errors

2. Restart backend server

3. Clear job manually:
   ```bash
   rm -rf backend/uploads/{job_id}
   rm -rf backend/outputs/{job_id}
   ```

#### Issue: Results not appearing
**Solutions:**
1. Check job status via API:
   ```bash
   curl http://localhost:8000/api/status/{job_id}
   ```

2. Verify output files exist:
   ```bash
   ls -la backend/outputs/{job_id}/
   ```

3. Check file permissions

### Testing Issues

#### Issue: test_local.py fails
**Solutions:**
1. Ensure backend modules are in Python path:
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/../backend"
   ```

2. Run from scripts directory:
   ```bash
   cd scripts
   python test_local.py ...
   ```

3. Check all dependencies installed:
   ```bash
   pip list | grep torch
   pip list | grep opencv
   ```

## Getting Help

If issues persist:

1. **Check logs:**
   - Backend: Terminal output
   - Frontend: Browser console (F12)
   - Network: Browser Network tab

2. **Verify setup:**
   ```bash
   # Backend
   cd backend
   source venv/bin/activate
   python -c "import torch; print(torch.__version__)"
   python -c "from app.models import load_model; print('OK')"
   
   # Frontend
   cd frontend
   npm run build
   ```

3. **Test API directly:**
   ```bash
   # Health check
   curl http://localhost:8000/health
   
   # Upload test (replace with actual file)
   curl -X POST http://localhost:8000/api/upload \
     -F "file=@test.mp4" \
     -F "threshold=0.5" \
     -F "min_area=300"
   ```

4. **Check documentation:**
   - README.md - Full documentation
   - QUICKSTART.md - Setup guide
   - ARCHITECTURE.md - System design
   - API docs: http://localhost:8000/docs

## Debug Mode

### Enable verbose logging:

**Backend:**
```python
# In app/main.py, add:
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Frontend:**
```typescript
// In lib/api.ts, add interceptor:
api.interceptors.response.use(
  response => {
    console.log('Response:', response);
    return response;
  },
  error => {
    console.error('Error:', error);
    return Promise.reject(error);
  }
);
```

## Reset Everything

If all else fails, complete reset:

```bash
# Backend
cd backend
rm -rf venv uploads outputs __pycache__ app/__pycache__
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules .next package-lock.json
npm install

# Restart both servers
```
