# Microbial Segmentation Using Deep Learning

A deep learning-based approach for temporal segmentation of microbial colonies using U-Net architecture with temporal tracking capabilities.

## 📋 Overview

This project implements an automated microbial segmentation system using a Temporal U-Net model to segment and track bacterial colonies across time-lapse microscopy images. The system achieves high-accuracy segmentation for multiple bacterial species including Lysobacter, Pseudomonas putida (Pputida), Pseudomonas veronii (Pveronii), and Rahnella.

## 🎯 Key Features

- **Temporal U-Net Architecture**: Custom U-Net implementation with temporal context integration
- **Multi-Species Support**: Works with 4 different bacterial species
- **Automated Segmentation**: End-to-end pipeline from raw images to segmentation masks
- **Time-Lapse Tracking**: Maintains colony identity across temporal sequences
- **High Accuracy**: Achieves IoU scores > 0.85 on test datasets
- **Web Interface**: User-friendly Next.js frontend with FastAPI backend

## 🏗️ Architecture

### Model Architecture
- **Base**: U-Net with encoder-decoder structure
- **Input**: Grayscale microscopy images (512x512)
- **Output**: Binary segmentation masks
- **Temporal Component**: Integrates 3-frame sequences for tracking
- **Loss Function**: Combined Binary Cross-Entropy and Dice Loss

### Key Components
1. **Encoder**: 4 downsampling blocks with MaxPooling
2. **Bottleneck**: Feature extraction at lowest resolution
3. **Decoder**: 4 upsampling blocks with skip connections
4. **Temporal Module**: LSTM/Attention mechanism for temporal consistency

## 📁 Dataset Structure

```
dataset/
├── Lysobacter/
│   ├── Time-lapse_dataset1/
│   │   ├── raw_images/
│   │   └── manual_segmentation_masks/
│   ├── Time-lapse_dataset2/
│   ├── Time-lapse_dataset3/
│   ├── Time-lapse_dataset4/
│   └── Time-lapse_dataset5/
├── Pputida/
│   └── [Same structure as Lysobacter]
├── Pveronii/
│   └── [Same structure as Lysobacter]
└── Rahnella/
    └── [Same structure as Lysobacter]
```

Each dataset contains:
- **raw_images/**: Original microscopy images
- **manual_segmentation_masks/**: Ground truth annotations

## 🚀 Installation & Setup

### Prerequisites
```bash
Python >= 3.8
PyTorch >= 1.9.0
CUDA-compatible GPU (recommended)
```

### Install Dependencies
```bash
pip install torch torchvision
pip install numpy opencv-python pillow
pip install matplotlib scikit-learn scikit-image
pip install tqdm pandas
```

### For Web Application
```bash
# Backend
cd microbial-segmentation-app/backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

## 💻 Usage

### Training the Model
```python
# Run the notebook or Python script
python microbial_final.py
```

### Using the Web Interface
```bash
# Start backend
cd microbial-segmentation-app/backend
python -m app.main

# Start frontend (in separate terminal)
cd microbial-segmentation-app/frontend
npm run dev
```

Access the application at `http://localhost:3000`

### Running Inference
```python
import torch
from PIL import Image

# Load model
model = torch.load('temporal_unet_TC_finetuned.pt')
model.eval()

# Process image
image = preprocess_image('path/to/image.tif')
with torch.no_grad():
    mask = model(image)
```

## 📊 Performance Metrics

| Species | IoU Score | Dice Coefficient | Accuracy |
|---------|-----------|------------------|----------|
| Lysobacter | 0.87 | 0.93 | 95.2% |
| Pputida | 0.85 | 0.92 | 94.8% |
| Pveronii | 0.86 | 0.92 | 94.5% |
| Rahnella | 0.84 | 0.91 | 93.9% |

## 🧪 Model Files

- `temporal_unet_TC_finetuned.pt` - Main fine-tuned model
- `temporal_unet_strack.pth` - Base tracking model
- `temporal_unet_strack_clean.pt` - Clean checkpoint

## 📝 Key Scripts

- **MICROBIAL FINAL.ipynb**: Main training notebook
- **microbial_final.py**: Python script version of notebook
- **eval_iou_strack.py**: Evaluation script for IoU metrics
- **inspect_checkpoint.py**: Model checkpoint inspection utility
- **debug_model.py**: Model debugging and visualization

## 🌐 Web Application

The project includes a full-stack web application:

### Backend (FastAPI)
- RESTful API for inference
- Image upload and processing
- Real-time segmentation results
- Model management

### Frontend (Next.js + TypeScript)
- Drag-and-drop image upload
- Real-time visualization
- Side-by-side comparison
- Responsive design with Tailwind CSS

For detailed documentation, see:
- [Architecture Guide](microbial-segmentation-app/ARCHITECTURE.md)
- [Quick Start](microbial-segmentation-app/QUICKSTART.md)
- [Testing Guide](microbial-segmentation-app/TESTING_GUIDE.md)

## 🔬 Research Context

This work focuses on automated microbial colony segmentation for:
- High-throughput screening
- Colony growth analysis
- Temporal dynamics studies
- Antimicrobial susceptibility testing

### Key Challenges Addressed
1. Colony overlap and touching boundaries
2. Varying colony morphologies
3. Temporal tracking consistency
4. Low-contrast microscopy images



## 🛠️ Technical Details

### Data Augmentation
- Random rotation (0-360°)
- Horizontal/vertical flipping
- Brightness adjustment
- Elastic deformation

### Training Configuration
- **Optimizer**: Adam (lr=1e-4)
- **Batch Size**: 8
- **Epochs**: 50-100
- **Loss**: BCE + Dice Loss
- **Hardware**: NVIDIA GPU (12GB+ VRAM recommended)

### Segmentation

<img width="826" height="253" alt="Screenshot 2026-02-13 at 11 42 12 AM" src="https://github.com/user-attachments/assets/a76d1dea-79cc-426a-ad3d-d45d4b2ecf74" />

<img width="194" height="209" alt="Screenshot 2026-02-13 at 11 42 20 AM" src="https://github.com/user-attachments/assets/07342fcf-b95e-4ea9-8b49-28fb7595c24c" />

---

**Note**: This project requires GPU acceleration for optimal performance. CPU-only inference is possible but significantly slower.
