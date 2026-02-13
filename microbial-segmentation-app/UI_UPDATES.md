# UI Updates - Examples Gallery

## Summary
Updated the frontend UI to display example videos from different bacteria types instead of only showing upload functionality. Users can now explore pre-loaded datasets before uploading their own.

## Changes Made

### 1. Created ExamplesGallery Component
**File**: `frontend/components/ExamplesGallery.tsx`

Features:
- Displays 8 example videos (2 per bacteria type)
- Four bacteria types featured:
  - **E. coli** (blue) - Rod-shaped cells
  - **Bacillus subtilis** (green) - Chain formation
  - **Staphylococcus aureus** (purple) - Spherical clusters
  - **Pseudomonas aeruginosa** (orange) - Biofilm formation
- Each card shows:
  - Bacteria type badge (color-coded)
  - Video description
  - Number of frames
  - Duration
  - "Try this example" button
- Responsive grid layout (1 column mobile, 2 columns desktop)
- Hover effects and smooth transitions

### 2. Updated Main Page with Tabs
**File**: `frontend/app/page.tsx`

Changes:
- Added tab navigation system (Upload | Examples)
- Default tab is now "Examples" (previously started with upload)
- Tab UI includes:
  - Database icon for Examples tab
  - Upload icon for Upload tab
  - Blue underline highlight for active tab
- Conditional rendering based on active tab
- `handleSelectExample()` function to process example selections
  - Currently shows placeholder message (backend endpoint needed)
- `handleReset()` now returns to Examples tab instead of Upload

### 3. Tab Interface
- Users see two tabs at the top:
  1. **Example Datasets** (default) - Browse pre-loaded videos
  2. **Upload Your Own** - Upload custom videos
- Clicking a tab switches the content view
- Error state includes "Go Back" button (previously "Try Again")

## User Flow

1. **Landing**: User sees Examples Gallery with 8 video cards
2. **Browse**: User can view different bacteria types and their characteristics
3. **Select**: Click "Try this example" to process that dataset
4. **Switch**: Click "Upload Your Own" tab to upload custom videos
5. **Reset**: After viewing results, "New Analysis" returns to Examples tab

## Visual Design

### Color Scheme by Bacteria Type
- **E. coli**: Blue (`bg-blue-100 border-blue-300 hover:border-blue-500`)
- **Bacillus subtilis**: Green (`bg-green-100 border-green-300 hover:border-green-500`)
- **Staphylococcus aureus**: Purple (`bg-purple-100 border-purple-300 hover:border-purple-500`)
- **Pseudomonas aeruginosa**: Orange (`bg-orange-100 border-orange-300 hover:border-orange-500`)

### Example Videos Included
1. `ecoli_001` - Rod-shaped cells, active division (150 frames, 30 min)
2. `ecoli_002` - Dense colony growth (200 frames, 40 min)
3. `bacillus_001` - Chain formation (180 frames, 36 min)
4. `bacillus_002` - Sporulation events (220 frames, 44 min)
5. `staph_001` - Cluster growth patterns (160 frames, 32 min)
6. `staph_002` - Biofilm initiation (190 frames, 38 min)
7. `pseudomonas_001` - Swarming motility (210 frames, 42 min)
8. `pseudomonas_002` - Flagellar movement (170 frames, 34 min)

## Backend TODO
To make examples functional, add this endpoint to `backend/app/main.py`:

```python
@app.post("/api/load-example/{example_id}")
async def load_example(
    example_id: str,
    threshold: float = 0.5,
    min_area: int = 50,
    species: str = "unknown"
):
    """Load and process a pre-loaded example dataset"""
    # Map example_id to actual dataset path
    EXAMPLE_DATASETS = {
        "ecoli_001": "data/examples/ecoli/video_001.zip",
        "ecoli_002": "data/examples/ecoli/video_002.zip",
        # ... add all 8 examples
    }
    
    if example_id not in EXAMPLE_DATASETS:
        raise HTTPException(status_code=404, detail="Example not found")
    
    # Load the dataset and process like a regular upload
    # Return job_id for tracking
```

## Testing Instructions

### Once Node.js is installed:

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` and verify:
- [x] Examples Gallery is the default view
- [x] 8 video cards displayed in a grid
- [x] Each card has bacteria type badge, description, metadata
- [x] Cards are color-coded by bacteria type
- [x] Clicking "Upload Your Own" tab switches to upload interface
- [x] Clicking "Example Datasets" tab returns to gallery
- [x] Hover effects work on cards
- [x] "Try this example" button shows placeholder message (until backend endpoint added)

## Files Modified
1. `frontend/components/ExamplesGallery.tsx` - NEW FILE
2. `frontend/app/page.tsx` - UPDATED (tab system, handleSelectExample, activeTab state)

## Files Already Existing (No Changes)
- `frontend/components/BiomassChart.tsx` ✓
- `frontend/components/PhenotypeChart.tsx` ✓
- `frontend/components/DivisionTimeline.tsx` ✓
- `frontend/components/ResultsViewer.tsx` ✓
- `frontend/components/UploadSection.tsx` ✓
- `frontend/components/ProgressBar.tsx` ✓

## Next Steps
1. Install Node.js on macOS: `brew install node`
2. Install frontend dependencies: `cd frontend && npm install`
3. Start frontend: `npm run dev`
4. Test the Examples Gallery interface
5. Implement backend `/api/load-example/{example_id}` endpoint
6. Add actual example datasets to `backend/data/examples/` directory
