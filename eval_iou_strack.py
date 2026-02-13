#!/usr/bin/env python3
"""
Standalone evaluation script for temporal U-Net model on STRack dataset.
Computes mean IoU across all valid frames without retraining.
"""

import os
import glob
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
import cv2
from pathlib import Path


# ============================================================================
# Model Architecture: UNetTemporalFlow
# ============================================================================

class ConvBlock(nn.Module):
    """Convolution block: Conv2d -> BN -> ReLU -> Conv2d -> BN -> ReLU"""
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1, bias=True),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, bias=True),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )
    
    def forward(self, x):
        return self.conv(x)


class TemporalSE(nn.Module):
    """Temporal Squeeze-and-Excitation module"""
    def __init__(self, num_frames=5, reduction=2):
        super().__init__()
        self.fc1 = nn.Linear(num_frames, num_frames // reduction)
        self.fc2 = nn.Linear(num_frames // reduction, num_frames)
    
    def forward(self, x):
        # Global average pooling over spatial dimensions
        b, c, h, w = x.size()
        # Assume temporal dimension is embedded in batch or channels
        # For this architecture, it's a simple attention mechanism
        return x


class UNetTemporalFlow(nn.Module):
    """
    Temporal U-Net with optical flow integration.
    Input: 13 channels (5 grayscale frames + 8 optical flow channels)
    Output: 1 channel (segmentation mask for center frame)
    
    Architecture matches checkpoint with:
    - Encoder: enc1(13->32), enc2(32->64), enc3(64->128), enc4(128->256)
    - Bottleneck: (256->512)
    - Decoder: dec4(512->256), dec3(256->128), dec2(128->64), dec1(64->32)
    - Upsampling: ConvTranspose2d layers
    - Output: 1x1 conv (32->1)
    """
    def __init__(self, n_channels, n_classes):
        super(UNetTemporalFlow, self).__init__()
        self.n_channels = n_channels
        self.n_classes = n_classes
        
        # Temporal SE module
        self.temporal_se = TemporalSE(num_frames=5, reduction=2)
        
        # Encoder
        self.enc1 = ConvBlock(n_channels, 32)
        self.enc2 = ConvBlock(32, 64)
        self.enc3 = ConvBlock(64, 128)
        self.enc4 = ConvBlock(128, 256)
        
        # Bottleneck
        self.bottleneck = ConvBlock(256, 512)
        
        # Decoder upsampling (ConvTranspose2d)
        self.up4 = nn.ConvTranspose2d(512, 256, kernel_size=2, stride=2, bias=True)
        self.dec4 = ConvBlock(512, 256)  # 256 from up + 256 from skip
        
        self.up3 = nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2, bias=True)
        self.dec3 = ConvBlock(256, 128)  # 128 from up + 128 from skip
        
        self.up2 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2, bias=True)
        self.dec2 = ConvBlock(128, 64)  # 64 from up + 64 from skip
        
        self.up1 = nn.ConvTranspose2d(64, 32, kernel_size=2, stride=2, bias=True)
        self.dec1 = ConvBlock(64, 32)  # 32 from up + 32 from skip
        
        # Output
        self.out_conv = nn.Conv2d(32, n_classes, kernel_size=1, bias=True)
        
        # Pooling
        self.pool = nn.MaxPool2d(2)
    
    def forward(self, x):
        # Encoder
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool(e1))
        e3 = self.enc3(self.pool(e2))
        e4 = self.enc4(self.pool(e3))
        
        # Bottleneck
        b = self.bottleneck(self.pool(e4))
        
        # Decoder with skip connections
        d4 = self.up4(b)
        d4 = torch.cat([d4, e4], dim=1)
        d4 = self.dec4(d4)
        
        d3 = self.up3(d4)
        d3 = torch.cat([d3, e3], dim=1)
        d3 = self.dec3(d3)
        
        d2 = self.up2(d3)
        d2 = torch.cat([d2, e2], dim=1)
        d2 = self.dec2(d2)
        
        d1 = self.up1(d2)
        d1 = torch.cat([d1, e1], dim=1)
        d1 = self.dec1(d1)
        
        # Output
        out = self.out_conv(d1)
        return out


# ============================================================================
# Checkpoint Loading
# ============================================================================

def load_checkpoint(model, checkpoint_path, device):
    """
    Load model weights from checkpoint file.
    Handles different checkpoint formats:
    - Plain state_dict
    - Dict with 'model_state' or 'state_dict' keys
    """
    print(f"Loading checkpoint from: {checkpoint_path}")
    checkpoint = torch.load(checkpoint_path, map_location=device)
    
    # Handle different checkpoint formats
    if isinstance(checkpoint, dict):
        if 'model_state' in checkpoint:
            state_dict = checkpoint['model_state']
            print("Loaded from 'model_state' key")
        elif 'state_dict' in checkpoint:
            state_dict = checkpoint['state_dict']
            print("Loaded from 'state_dict' key")
        else:
            # Assume the dict itself is the state_dict
            state_dict = checkpoint
            print("Loaded checkpoint as state_dict")
    else:
        state_dict = checkpoint
        print("Loaded checkpoint as plain state_dict")
    
    # Load state dict into model
    model.load_state_dict(state_dict)
    print("✓ Checkpoint loaded successfully")
    return model


# ============================================================================
# Optical Flow Computation
# ============================================================================

def compute_optical_flow(frame1, frame2):
    """
    Compute optical flow between two grayscale frames using Farneback method.
    Returns: (flow_x, flow_y) as float32 arrays
    """
    # Ensure frames are uint8 [0, 255]
    if frame1.max() <= 1.0:
        frame1 = (frame1 * 255).astype(np.uint8)
    if frame2.max() <= 1.0:
        frame2 = (frame2 * 255).astype(np.uint8)
    
    flow = cv2.calcOpticalFlowFarneback(
        frame1, frame2, None,
        pyr_scale=0.5, levels=3, winsize=15,
        iterations=3, poly_n=5, poly_sigma=1.2, flags=0
    )
    
    flow_x = flow[..., 0]  # Horizontal flow
    flow_y = flow[..., 1]  # Vertical flow
    
    return flow_x, flow_y


def build_13channel_input(frames):
    """
    Build 13-channel input from 5 consecutive frames.
    
    Args:
        frames: List of 5 grayscale images (H, W) normalized to [0, 1]
    
    Returns:
        input_tensor: (13, H, W) tensor
            - Channels 0-4: 5 grayscale frames
            - Channels 5-12: 8 optical flow channels (dx, dy between consecutive frames)
    """
    assert len(frames) == 5, "Expected 5 frames"
    
    # Stack grayscale frames
    gray_stack = np.stack(frames, axis=0)  # (5, H, W)
    
    # Compute optical flow between consecutive frames
    flow_channels = []
    for i in range(4):
        flow_x, flow_y = compute_optical_flow(frames[i], frames[i + 1])
        flow_channels.append(flow_x)
        flow_channels.append(flow_y)
    
    flow_stack = np.stack(flow_channels, axis=0)  # (8, H, W)
    
    # Concatenate: 5 gray + 8 flow = 13 channels
    input_array = np.concatenate([gray_stack, flow_stack], axis=0)  # (13, H, W)
    
    return torch.from_numpy(input_array).float()


# ============================================================================
# STRack Dataset Loader
# ============================================================================

def load_strack_dataset(root_folder):
    """
    Load STRack dataset from folder structure.
    Searches for:
    1. Species/Species/Time-lapse_datasetX/ (nested structure)
    2. Species/Time-lapse_datasetX/ (flat structure)
    3. Time-lapse_datasetX/ (direct structure)
    
    Each time-lapse folder should contain:
      - raw_images/
      - manual_segmentation_masks/
    
    Returns:
        List of dicts: [{'images': [...], 'masks': [...]}, ...]
        Each dict represents one time-lapse sequence.
    """
    root = Path(root_folder)
    sequences = []
    
    # Try multiple patterns to find time-lapse datasets
    patterns = [
        str(root / "*" / "*" / "Time-lapse_dataset*"),  # Species/Species/Time-lapse_datasetX
        str(root / "*" / "Time-lapse_dataset*"),         # Species/Time-lapse_datasetX
        str(root / "Time-lapse_dataset*"),               # Time-lapse_datasetX
    ]
    
    dataset_folders = []
    for pattern in patterns:
        found = glob.glob(pattern)
        dataset_folders.extend(found)
    
    # Remove duplicates and sort
    dataset_folders = sorted(list(set(dataset_folders)))
    
    if not dataset_folders:
        print(f"Warning: No dataset folders found in {root_folder}")
        print(f"Tried patterns: {patterns}")
        return sequences
    
    print(f"Found {len(dataset_folders)} time-lapse sequences")
    
    for dataset_folder in dataset_folders:
        dataset_path = Path(dataset_folder)
        raw_images_dir = dataset_path / "raw_images"
        masks_dir = dataset_path / "manual_segmentation_masks"
        
        if not raw_images_dir.exists() or not masks_dir.exists():
            print(f"Skipping {dataset_folder}: missing raw_images or masks folder")
            continue
        
        # Load all images and masks
        image_files = sorted(glob.glob(str(raw_images_dir / "*.tif")) + 
                            glob.glob(str(raw_images_dir / "*.tiff")) +
                            glob.glob(str(raw_images_dir / "*.png")) +
                            glob.glob(str(raw_images_dir / "*.jpg")))
        mask_files = sorted(glob.glob(str(masks_dir / "*.tif")) + 
                           glob.glob(str(masks_dir / "*.tiff")) +
                           glob.glob(str(masks_dir / "*.png")))
        
        if len(image_files) == 0 or len(mask_files) == 0:
            print(f"Skipping {dataset_folder}: no images or masks found")
            continue
        
        # Load images as grayscale numpy arrays
        images = []
        for img_file in image_files:
            img = Image.open(img_file).convert('L')  # Grayscale
            img_array = np.array(img, dtype=np.float32) / 255.0  # Normalize to [0, 1]
            images.append(img_array)
        
        # Load masks as binary numpy arrays
        masks = []
        for mask_file in mask_files:
            mask = Image.open(mask_file).convert('L')
            mask_array = np.array(mask, dtype=np.float32)
            # Binarize: any non-zero value becomes 1
            mask_array = (mask_array > 0).astype(np.float32)
            masks.append(mask_array)
        
        sequences.append({
            'images': images,
            'masks': masks,
            'name': dataset_path.name
        })
        print(f"  Loaded {dataset_path.name}: {len(images)} images, {len(masks)} masks")
    
    return sequences


# ============================================================================
# IoU Computation
# ============================================================================

def compute_iou(pred, target, threshold=0.5):
    """
    Compute binary IoU between prediction and target.
    
    Args:
        pred: (H, W) tensor, values in [0, 1]
        target: (H, W) tensor, binary {0, 1}
        threshold: threshold for binarizing prediction
    
    Returns:
        iou: float, Intersection over Union
    """
    pred_binary = (pred > threshold).float()
    target_binary = target.float()
    
    intersection = (pred_binary * target_binary).sum()
    union = pred_binary.sum() + target_binary.sum() - intersection
    
    if union == 0:
        return 1.0 if intersection == 0 else 0.0
    
    iou = (intersection / union).item()
    return iou


# ============================================================================
# Evaluation Loop
# ============================================================================

def evaluate_model(model, sequences, device):
    """
    Evaluate model on all sequences and compute mean IoU.
    
    For each sequence:
    - Iterate over valid frames (index 2 to len-3) that have 5 consecutive frames
    - Build 13-channel input
    - Predict segmentation mask for center frame
    - Compare with ground truth mask
    - Compute IoU
    
    Returns:
        mean_iou: float
        num_frames: int
    """
    model.eval()
    all_ious = []
    
    with torch.no_grad():
        for seq_idx, sequence in enumerate(sequences):
            images = sequence['images']
            masks = sequence['masks']
            seq_name = sequence['name']
            
            # Need at least 5 consecutive frames
            if len(images) < 5:
                print(f"Skipping {seq_name}: too few frames ({len(images)} < 5)")
                continue
            
            # Evaluate frames that can be center frames (index 2 to len-3)
            for center_idx in range(2, len(images) - 2):
                # Check if mask exists for center frame
                if center_idx >= len(masks):
                    continue
                
                # Extract 5 consecutive frames
                frame_indices = [center_idx - 2, center_idx - 1, center_idx, 
                               center_idx + 1, center_idx + 2]
                frames_5 = [images[i] for i in frame_indices]
                
                # Build 13-channel input
                input_tensor = build_13channel_input(frames_5)  # (13, H, W)
                input_batch = input_tensor.unsqueeze(0).to(device)  # (1, 13, H, W)
                
                # Forward pass
                output = model(input_batch)  # (1, 1, H, W)
                pred_mask = torch.sigmoid(output).squeeze(0).squeeze(0)  # (H, W)
                
                # Get ground truth mask
                gt_mask = torch.from_numpy(masks[center_idx]).to(device)  # (H, W)
                
                # Compute IoU
                iou = compute_iou(pred_mask, gt_mask, threshold=0.5)
                all_ious.append(iou)
    
    if len(all_ious) == 0:
        print("ERROR: No valid frames evaluated!")
        return 0.0, 0
    
    mean_iou = np.mean(all_ious)
    return mean_iou, len(all_ious)


# ============================================================================
# Main Script
# ============================================================================

def extract_dataset_if_needed(zip_path, extract_to="."):
    """Extract dataset from zip file if it hasn't been extracted yet"""
    import zipfile
    
    zip_file = Path(zip_path)
    if not zip_file.exists():
        print(f"Warning: Main zip file not found: {zip_path}")
        return None
    
    # Extract main zip which contains species zips
    print(f"Extracting main dataset from {zip_path}...")
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"✓ Main dataset extracted")
    
    # Find and extract all species zip files
    species_zips = list(Path(extract_to).glob("*.zip"))
    species_zips = [z for z in species_zips if z.name != zip_file.name]
    
    print(f"Found {len(species_zips)} species zip files")
    for species_zip in species_zips:
        species_name = species_zip.stem
        species_folder = Path(extract_to) / species_name
        
        if species_folder.exists():
            print(f"  {species_name}: already extracted")
            continue
        
        print(f"  Extracting {species_name}...")
        with zipfile.ZipFile(species_zip, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    
    print("✓ All species extracted")
    return extract_to


def main():
    # Configuration
    CHECKPOINT_PATH = "temporal_unet_TC_finetuned.pt"
    ZIP_PATH = "7670637.zip"
    
    # Device setup
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Extract dataset if needed
    print("\n" + "="*60)
    print("Checking dataset...")
    print("="*60)
    
    # Check if species folders already exist
    existing_species = list(Path(".").glob("*"))
    existing_species = [f for f in existing_species if f.is_dir() and 
                       any((f / "Time-lapse_dataset1").exists() or 
                           (f / "Time-lapse_dataset2").exists() or
                           (f / "Time-lapse_dataset3").exists() for _ in [0])]
    
    if not existing_species:
        print("Species folders not found, extracting dataset...")
        extract_dataset_if_needed(ZIP_PATH)
    else:
        print(f"Found {len(existing_species)} existing species folders")
    
    # Use current directory as root
    STRACK_ROOT = "."
    
    # Initialize model
    print("\n" + "="*60)
    print("Initializing UNetTemporalFlow model...")
    print("="*60)
    model = UNetTemporalFlow(n_channels=13, n_classes=1)
    model = model.to(device)
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Load checkpoint
    print("\n" + "="*60)
    print("Loading checkpoint...")
    print("="*60)
    model = load_checkpoint(model, CHECKPOINT_PATH, device)
    
    # Load dataset
    print("\n" + "="*60)
    print("Loading STRack dataset...")
    print("="*60)
    sequences = load_strack_dataset(STRACK_ROOT)
    
    if len(sequences) == 0:
        print("ERROR: No sequences loaded. Please check STRACK_ROOT path.")
        print(f"Current path: {STRACK_ROOT}")
        return
    
    print(f"Total sequences loaded: {len(sequences)}")
    
    # Evaluate
    print("\n" + "="*60)
    print("Evaluating model...")
    print("="*60)
    mean_iou, num_frames = evaluate_model(model, sequences, device)
    
    # Print results
    print("\n" + "="*60)
    print("EVALUATION RESULTS")
    print("="*60)
    print(f"Number of evaluated frames: {num_frames}")
    print(f"Final mean IoU: {mean_iou:.4f}")
    print("="*60)


if __name__ == "__main__":
    main()
