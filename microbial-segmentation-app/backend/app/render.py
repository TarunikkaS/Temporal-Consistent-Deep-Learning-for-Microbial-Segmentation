"""
Render module: Generate frame images and combined triplet views.
"""
import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple
from pathlib import Path


def normalize_to_uint8(image: np.ndarray) -> np.ndarray:
    """
    Convert float image [0,1] or any range to uint8 [0,255].
    
    Args:
        image: Input image (any dtype)
    
    Returns:
        uint8 image [0, 255]
    """
    if image.dtype == np.uint8:
        return image
    
    # If float in range [0, 1]
    if image.dtype in [np.float32, np.float64]:
        if image.max() <= 1.0:
            return (image * 255).astype(np.uint8)
        else:
            # Normalize to [0, 1] then to [0, 255]
            img_min = image.min()
            img_max = image.max()
            if img_max > img_min:
                normalized = (image - img_min) / (img_max - img_min)
                return (normalized * 255).astype(np.uint8)
            else:
                return np.zeros_like(image, dtype=np.uint8)
    
    # For other integer types, scale to [0, 255]
    img_min = image.min()
    img_max = image.max()
    if img_max > img_min:
        normalized = (image - img_min) / (img_max - img_min)
        return (normalized * 255).astype(np.uint8)
    else:
        return np.zeros_like(image, dtype=np.uint8)


def create_overlay(
    original: np.ndarray,
    mask: np.ndarray,
    color: Tuple[int, int, int] = (255, 165, 0),  # Orange in RGB
    alpha: float = 0.4
) -> np.ndarray:
    """
    Create colored overlay on original image.
    
    Args:
        original: Original grayscale or RGB image
        mask: Binary mask (H, W)
        color: RGB color tuple
        alpha: Transparency factor
    
    Returns:
        RGB image with overlay (H, W, 3) uint8
    """
    # Convert original to uint8 RGB
    if len(original.shape) == 2:
        original_uint8 = normalize_to_uint8(original)
        original_rgb = cv2.cvtColor(original_uint8, cv2.COLOR_GRAY2RGB)
    else:
        original_uint8 = normalize_to_uint8(original)
        if original_uint8.shape[2] == 1:
            original_rgb = cv2.cvtColor(original_uint8[:, :, 0], cv2.COLOR_GRAY2RGB)
        else:
            original_rgb = original_uint8
    
    # Create colored mask
    overlay = original_rgb.copy()
    mask_colored = np.zeros_like(original_rgb)
    mask_colored[mask > 0] = color
    
    # Blend
    overlay = cv2.addWeighted(original_rgb, 1 - alpha, mask_colored, alpha, 0)
    
    return overlay


def create_triplet_frame(
    original: np.ndarray,
    pred_mask: np.ndarray,
    gt_mask: Optional[np.ndarray],
    frame_idx: int,
    fps: float,
    pred_area: int,
    gt_area: Optional[int],
    growth_rate: float
) -> np.ndarray:
    """
    Create 3-panel combined image: Original | GT overlay | Pred overlay.
    
    Args:
        original: Original frame (H, W) or (H, W, 3)
        pred_mask: Predicted mask (H, W)
        gt_mask: Ground truth mask (H, W) or None
        frame_idx: Frame index
        fps: Frames per second
        pred_area: Predicted area in pixels
        gt_area: GT area in pixels or None
        growth_rate: Growth rate value
    
    Returns:
        Combined RGB image (H, W*3, 3) uint8
    """
    # Convert original to uint8 RGB
    if len(original.shape) == 2:
        original_uint8 = normalize_to_uint8(original)
        original_rgb = cv2.cvtColor(original_uint8, cv2.COLOR_GRAY2RGB)
    else:
        original_uint8 = normalize_to_uint8(original)
        if original_uint8.shape[2] == 1:
            original_rgb = cv2.cvtColor(original_uint8[:, :, 0], cv2.COLOR_GRAY2RGB)
        else:
            original_rgb = original_uint8
    
    h, w = original_rgb.shape[:2]
    
    # Panel 1: Original
    panel1 = original_rgb.copy()
    
    # Panel 2: GT overlay (if available)
    if gt_mask is not None:
        panel2 = create_overlay(original, gt_mask, color=(0, 255, 0), alpha=0.4)  # Green
    else:
        panel2 = original_rgb.copy()
    
    # Panel 3: Pred overlay
    panel3 = create_overlay(original, pred_mask, color=(255, 165, 0), alpha=0.4)  # Orange
    
    # Combine horizontally
    combined = np.hstack([panel1, panel2, panel3])
    
    # Add top text bar with metrics
    time_sec = frame_idx / fps
    text_height = 60
    text_bar = np.zeros((text_height, combined.shape[1], 3), dtype=np.uint8)
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    thickness = 2
    
    # Left: Time
    time_text = f"time={time_sec:.2f}s"
    cv2.putText(text_bar, time_text, (20, 40), font, font_scale, (200, 200, 200), thickness, cv2.LINE_AA)
    
    # Center: GT area (green)
    if gt_area is not None:
        gt_text = f"GT area={gt_area}"
        text_width = cv2.getTextSize(gt_text, font, font_scale, thickness)[0][0]
        x_pos = (combined.shape[1] - text_width) // 2
        cv2.putText(text_bar, gt_text, (x_pos, 40), font, font_scale, (0, 255, 0), thickness, cv2.LINE_AA)
    
    # Right: Pred area + growth (orange)
    pred_text = f"Pred area={pred_area}  growth={growth_rate:.3f}"
    text_width = cv2.getTextSize(pred_text, font, font_scale, thickness)[0][0]
    x_pos = combined.shape[1] - text_width - 20
    cv2.putText(text_bar, pred_text, (x_pos, 40), font, font_scale, (255, 165, 0), thickness, cv2.LINE_AA)
    
    # Combine text bar with image
    result = np.vstack([text_bar, combined])
    
    return result


def save_frame_images(
    output_dir: Path,
    frame_idx: int,
    original: np.ndarray,
    pred_mask: np.ndarray,
    gt_mask: Optional[np.ndarray],
    fps: float,
    pred_area: int,
    gt_area: Optional[int],
    growth_rate: float
) -> Dict[str, str]:
    """
    Save all frame images: original, GT, pred, overlay, triplet.
    
    Args:
        output_dir: Output directory (job_id folder)
        frame_idx: Frame index
        original: Original frame
        pred_mask: Predicted mask
        gt_mask: GT mask or None
        fps: FPS for time calculation
        pred_area: Predicted area
        gt_area: GT area or None
        growth_rate: Growth rate
    
    Returns:
        Dictionary with relative URLs for each saved image
    """
    frames_dir = output_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    
    frame_num = f"{frame_idx:04d}"
    job_id = output_dir.name
    
    urls = {}
    
    # Save original
    original_uint8 = normalize_to_uint8(original)
    if len(original_uint8.shape) == 2:
        original_rgb = cv2.cvtColor(original_uint8, cv2.COLOR_GRAY2RGB)
    else:
        if original_uint8.shape[2] == 1:
            original_rgb = cv2.cvtColor(original_uint8[:, :, 0], cv2.COLOR_GRAY2RGB)
        else:
            original_rgb = original_uint8
    
    orig_path = frames_dir / f"orig_{frame_num}.png"
    cv2.imwrite(str(orig_path), cv2.cvtColor(original_rgb, cv2.COLOR_RGB2BGR))
    urls['orig'] = f"/static/{job_id}/frames/orig_{frame_num}.png"
    
    # Save GT overlay (if exists)
    if gt_mask is not None:
        gt_overlay = create_overlay(original, gt_mask, color=(0, 255, 0), alpha=0.4)
        gt_path = frames_dir / f"gt_{frame_num}.png"
        cv2.imwrite(str(gt_path), cv2.cvtColor(gt_overlay, cv2.COLOR_RGB2BGR))
        urls['gt'] = f"/static/{job_id}/frames/gt_{frame_num}.png"
    else:
        urls['gt'] = None
    
    # Save pred overlay
    pred_overlay = create_overlay(original, pred_mask, color=(255, 165, 0), alpha=0.4)
    pred_path = frames_dir / f"pred_{frame_num}.png"
    cv2.imwrite(str(pred_path), cv2.cvtColor(pred_overlay, cv2.COLOR_RGB2BGR))
    urls['pred'] = f"/static/{job_id}/frames/pred_{frame_num}.png"
    
    # Save triplet
    triplet = create_triplet_frame(
        original, pred_mask, gt_mask,
        frame_idx, fps, pred_area, gt_area, growth_rate
    )
    triplet_path = frames_dir / f"triplet_{frame_num}.png"
    cv2.imwrite(str(triplet_path), cv2.cvtColor(triplet, cv2.COLOR_RGB2BGR))
    urls['triplet'] = f"/static/{job_id}/frames/triplet_{frame_num}.png"
    
    return urls


def create_video_from_frames(
    frames: List[np.ndarray],
    output_path: Path,
    fps: float = 5.0
) -> None:
    """
    Create MP4 video from list of frames.
    
    Args:
        frames: List of RGB frames (H, W, 3) uint8
        output_path: Output video path
        fps: Frames per second
    """
    if len(frames) == 0:
        raise ValueError("No frames to write")
    
    h, w = frames[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (w, h))
    
    for frame in frames:
        frame_uint8 = normalize_to_uint8(frame)
        if len(frame_uint8.shape) == 2:
            frame_bgr = cv2.cvtColor(frame_uint8, cv2.COLOR_GRAY2BGR)
        else:
            frame_bgr = cv2.cvtColor(frame_uint8, cv2.COLOR_RGB2BGR)
        writer.write(frame_bgr)
    
    writer.release()
