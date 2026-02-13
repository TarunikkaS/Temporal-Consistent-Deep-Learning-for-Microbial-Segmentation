"""
Video processing utilities: read/write videos, extract frames.
"""
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional
import zipfile
import tempfile
import shutil
from PIL import Image


def read_video_frames(video_path: str) -> Tuple[List[np.ndarray], float]:
    """
    Read all frames from video file.
    
    Args:
        video_path: Path to video file (mp4, avi, etc.)
    
    Returns:
        frames: List of frames (H, W, 3) as uint8 RGB
        fps: Frame rate of video
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        fps = 30.0  # Default fallback
    
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(frame_rgb)
    
    cap.release()
    return frames, fps


def write_video(
    output_path: str,
    frames: List[np.ndarray],
    fps: float = 30.0,
    codec: str = "mp4v"
) -> None:
    """
    Write frames to video file.
    
    Args:
        output_path: Output video path
        frames: List of frames (H, W, 3) as uint8 RGB
        fps: Frame rate
        codec: Video codec (mp4v, avc1, etc.)
    """
    if len(frames) == 0:
        raise ValueError("No frames to write")
    
    height, width = frames[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*codec)
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    
    for frame in frames:
        # Convert RGB to BGR
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        out.write(frame_bgr)
    
    out.release()


def extract_dataset_from_zip(
    zip_path: str,
    extract_dir: Optional[str] = None
) -> Tuple[List[np.ndarray], List[np.ndarray], str]:
    """
    Extract frames and masks from dataset zip file.
    Handles STRack-like structure.
    
    Args:
        zip_path: Path to zip file
        extract_dir: Optional extraction directory (uses temp if None)
    
    Returns:
        frames: List of frames (H, W) grayscale float32 [0, 1]
        masks: List of masks (H, W) binary {0, 1}, or empty if no masks
        extract_path: Path where files were extracted
    """
    if extract_dir is None:
        extract_dir = tempfile.mkdtemp()
    
    extract_path = Path(extract_dir)
    extract_path.mkdir(exist_ok=True, parents=True)
    
    # Extract zip
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    
    # Find image and mask directories
    image_dirs = []
    mask_dirs = []
    
    for root, dirs, files in extract_path.rglob("*"):
        root_path = Path(root)
        if "raw_images" in str(root_path).lower() or "images" in str(root_path).lower():
            if any(f.endswith(('.tif', '.tiff', '.png', '.jpg')) for f in files):
                image_dirs.append(root_path)
        if "mask" in str(root_path).lower() or "segmentation" in str(root_path).lower():
            if any(f.endswith(('.tif', '.tiff', '.png')) for f in files):
                mask_dirs.append(root_path)
    
    # Load frames from first found directory
    frames = []
    masks = []
    
    if image_dirs:
        image_dir = image_dirs[0]
        image_files = sorted([
            f for f in image_dir.iterdir()
            if f.suffix.lower() in ['.tif', '.tiff', '.png', '.jpg', '.jpeg']
        ])
        
        for img_file in image_files:
            img = Image.open(img_file).convert('L')
            img_array = np.array(img, dtype=np.float32) / 255.0
            frames.append(img_array)
    
    # Load masks if available
    if mask_dirs:
        mask_dir = mask_dirs[0]
        mask_files = sorted([
            f for f in mask_dir.iterdir()
            if f.suffix.lower() in ['.tif', '.tiff', '.png']
        ])
        
        for mask_file in mask_files:
            mask = Image.open(mask_file).convert('L')
            mask_array = np.array(mask, dtype=np.float32)
            mask_array = (mask_array > 0).astype(np.float32)
            masks.append(mask_array)
    
    return frames, masks, str(extract_path)


def save_frame_as_png(frame: np.ndarray, output_path: str) -> None:
    """
    Save frame as PNG image.
    
    Args:
        frame: Frame to save (H, W) or (H, W, 3)
        output_path: Output path for PNG
    """
    if frame.dtype == np.float32 or frame.dtype == np.float64:
        if frame.max() <= 1.0:
            frame = (frame * 255).astype(np.uint8)
        else:
            frame = frame.astype(np.uint8)
    
    if len(frame.shape) == 3 and frame.shape[2] == 3:
        # RGB to BGR for OpenCV
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    cv2.imwrite(str(output_path), frame)


def create_frame_sequence(
    all_frames: List[np.ndarray],
    window_size: int = 5
) -> List[Tuple[int, List[np.ndarray]]]:
    """
    Create temporal windows for inference.
    
    Args:
        all_frames: All frames in sequence
        window_size: Temporal window size (default: 5)
    
    Returns:
        List of (center_idx, window_frames) tuples
    """
    sequences = []
    half_window = window_size // 2
    
    for center_idx in range(half_window, len(all_frames) - half_window):
        window_frames = [
            all_frames[center_idx - half_window + i]
            for i in range(window_size)
        ]
        sequences.append((center_idx, window_frames))
    
    return sequences
