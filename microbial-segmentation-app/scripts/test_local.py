#!/usr/bin/env python3
"""
Test script for local inference on a video or dataset.
Computes mean IoU if ground truth is available.
"""
import argparse
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.models import load_model
from app.preprocessing import prepare_frames_for_inference, build_13channel_input
from app.postprocessing import clean_mask, analyze_frame
from app.video_utils import read_video_frames, extract_dataset_from_zip, create_frame_sequence
import torch
import numpy as np


def compute_iou(pred: np.ndarray, target: np.ndarray, threshold: float = 0.5) -> float:
    """Compute IoU between prediction and target."""
    pred_binary = (pred > threshold).astype(np.float32)
    target_binary = (target > 0).astype(np.float32)
    
    intersection = np.sum(pred_binary * target_binary)
    union = np.sum(pred_binary) + np.sum(target_binary) - intersection
    
    if union == 0:
        return 1.0 if intersection == 0 else 0.0
    
    return intersection / union


def test_inference(
    input_path: str,
    checkpoint_path: str,
    device: str = "cuda",
    threshold: float = 0.5,
    min_area: int = 300,
    max_frames: int = 50
):
    """Run inference test on video or dataset."""
    
    print("=" * 60)
    print("Microbial Segmentation Test Script")
    print("=" * 60)
    
    # Load model
    print(f"\nLoading model from: {checkpoint_path}")
    device_obj = torch.device(device if torch.cuda.is_available() else "cpu")
    model = load_model(checkpoint_path, str(device_obj))
    print(f"✓ Model loaded on device: {device_obj}")
    
    # Load input
    print(f"\nLoading input from: {input_path}")
    
    if input_path.endswith('.mp4'):
        print("Input type: Video")
        frames_rgb, fps = read_video_frames(input_path)
        frames_gray = prepare_frames_for_inference(frames_rgb)
        gt_masks = None
    elif input_path.endswith('.zip'):
        print("Input type: Dataset ZIP")
        frames_gray, gt_masks, _ = extract_dataset_from_zip(input_path)
        frames_rgb = [np.stack([f, f, f], axis=-1) for f in frames_gray]
        fps = 5.0
    else:
        raise ValueError("Unsupported input format. Use .mp4 or .zip")
    
    print(f"✓ Loaded {len(frames_gray)} frames")
    if gt_masks:
        print(f"✓ Found {len(gt_masks)} ground truth masks")
    
    # Create sequences
    sequences = create_frame_sequence(frames_gray, window_size=5)
    
    # Limit frames for testing
    if max_frames > 0:
        sequences = sequences[:max_frames]
        print(f"⚠ Limited to first {len(sequences)} frames for testing")
    
    print(f"\nRunning inference on {len(sequences)} frames...")
    
    # Inference loop
    all_ious = []
    all_biomass = []
    
    model.eval()
    with torch.no_grad():
        for idx, (center_idx, window_frames) in enumerate(sequences):
            # Progress
            if idx % max(1, len(sequences) // 10) == 0:
                print(f"  Processing frame {idx + 1}/{len(sequences)}...")
            
            # Build input
            input_tensor = build_13channel_input(window_frames)
            input_batch = input_tensor.unsqueeze(0).to(device_obj)
            
            # Forward pass
            output = model(input_batch)
            pred_mask = torch.sigmoid(output).squeeze(0).squeeze(0).cpu().numpy()
            
            # Clean mask
            pred_mask_binary = (pred_mask > threshold).astype(np.float32)
            pred_mask_clean = clean_mask(pred_mask_binary, min_area=min_area)
            
            # Analyze
            biomass, phenotype_counts, components = analyze_frame(pred_mask_clean)
            all_biomass.append(biomass)
            
            # Compute IoU if GT available
            if gt_masks and center_idx < len(gt_masks):
                iou = compute_iou(pred_mask, gt_masks[center_idx], threshold=threshold)
                all_ious.append(iou)
    
    # Results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Frames evaluated: {len(sequences)}")
    print(f"Average biomass: {np.mean(all_biomass):.1f} pixels")
    print(f"Max biomass: {np.max(all_biomass):.1f} pixels")
    
    if all_ious:
        mean_iou = np.mean(all_ious)
        print(f"\n✓ Mean IoU: {mean_iou:.4f}")
        print(f"  Min IoU: {np.min(all_ious):.4f}")
        print(f"  Max IoU: {np.max(all_ious):.4f}")
        print(f"  Std IoU: {np.std(all_ious):.4f}")
    else:
        print("\n⚠ No ground truth available - IoU not computed")
    
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Test microbial segmentation inference"
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Input video (.mp4) or dataset zip (.zip)"
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        required=True,
        help="Path to model checkpoint (.pt)"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda",
        help="Device to use (cuda or cpu)"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Segmentation threshold (default: 0.5)"
    )
    parser.add_argument(
        "--min-area",
        type=int,
        default=300,
        help="Minimum component area (default: 300)"
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=50,
        help="Maximum frames to process (0 for all, default: 50)"
    )
    
    args = parser.parse_args()
    
    try:
        test_inference(
            input_path=args.input,
            checkpoint_path=args.checkpoint,
            device=args.device,
            threshold=args.threshold,
            min_area=args.min_area,
            max_frames=args.max_frames
        )
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
