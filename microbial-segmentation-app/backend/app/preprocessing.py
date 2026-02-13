"""
Preprocessing utilities: optical flow computation and 13-channel input construction.
"""
import numpy as np
import cv2
import torch
from typing import List, Tuple


def compute_optical_flow(frame1: np.ndarray, frame2: np.ndarray, method: str = "farneback") -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute optical flow between two grayscale frames.
    
    Args:
        frame1: First frame (H, W), grayscale, float32 [0, 1]
        frame2: Second frame (H, W), grayscale, float32 [0, 1]
        method: Flow computation method ('farneback' or 'dis')
    
    Returns:
        flow_x: Horizontal flow component (H, W)
        flow_y: Vertical flow component (H, W)
    """
    # Convert to uint8 [0, 255]
    if frame1.max() <= 1.0:
        frame1 = (frame1 * 255).astype(np.uint8)
    if frame2.max() <= 1.0:
        frame2 = (frame2 * 255).astype(np.uint8)
    
    if method == "farneback":
        flow = cv2.calcOpticalFlowFarneback(
            frame1, frame2, None,
            pyr_scale=0.5,
            levels=3,
            winsize=15,
            iterations=3,
            poly_n=5,
            poly_sigma=1.2,
            flags=0
        )
    elif method == "dis":
        dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
        flow = dis.calc(frame1, frame2, None)
    else:
        raise ValueError(f"Unknown optical flow method: {method}")
    
    flow_x = flow[..., 0]  # Horizontal flow
    flow_y = flow[..., 1]  # Vertical flow
    
    return flow_x, flow_y


def build_13channel_input(frames: List[np.ndarray], flow_method: str = "farneback") -> torch.Tensor:
    """
    Build 13-channel input tensor from 5 consecutive frames.
    
    Args:
        frames: List of 5 grayscale frames (H, W), float32 [0, 1]
        flow_method: Optical flow computation method
    
    Returns:
        input_tensor: (13, H, W) tensor
            - Channels 0-4: 5 grayscale frames
            - Channels 5-12: 8 optical flow channels (dx, dy between consecutive frames)
    """
    assert len(frames) == 5, f"Expected 5 frames, got {len(frames)}"
    
    # Stack grayscale frames
    gray_stack = np.stack(frames, axis=0)  # (5, H, W)
    
    # Compute optical flow between consecutive frames (0->1, 1->2, 2->3, 3->4)
    # This matches the working eval_iou_strack.py script
    flow_channels = []
    for i in range(4):
        flow_x, flow_y = compute_optical_flow(frames[i], frames[i + 1], method=flow_method)
        flow_channels.append(flow_x)
        flow_channels.append(flow_y)
    
    flow_stack = np.stack(flow_channels, axis=0)  # (8, H, W)
    
    # Concatenate: 5 gray + 8 flow = 13 channels
    input_array = np.concatenate([gray_stack, flow_stack], axis=0)  # (13, H, W)
    
    return torch.from_numpy(input_array).float()


def normalize_frame(frame: np.ndarray, method: str = "minmax") -> np.ndarray:
    """
    Normalize frame to [0, 1] range.
    
    Args:
        frame: Input frame (H, W) or (H, W, C)
        method: Normalization method ('minmax' or 'global')
    
    Returns:
        Normalized frame as float32 [0, 1]
    """
    frame = frame.astype(np.float32)
    
    if method == "minmax":
        min_val = frame.min()
        max_val = frame.max()
        if max_val > min_val:
            frame = (frame - min_val) / (max_val - min_val)
        else:
            frame = np.zeros_like(frame)
    elif method == "global":
        # Assume input is uint8 [0, 255]
        frame = frame / 255.0
    else:
        raise ValueError(f"Unknown normalization method: {method}")
    
    return frame


def convert_to_grayscale(frame: np.ndarray) -> np.ndarray:
    """
    Convert frame to grayscale if needed.
    
    Args:
        frame: Input frame (H, W) or (H, W, C)
    
    Returns:
        Grayscale frame (H, W)
    """
    if len(frame.shape) == 3:
        if frame.shape[2] == 3:  # RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        elif frame.shape[2] == 4:  # RGBA
            frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2GRAY)
        elif frame.shape[2] == 1:  # Already grayscale
            frame = frame.squeeze(-1)
    return frame


def prepare_frames_for_inference(frames: List[np.ndarray], normalize_method: str = "minmax") -> List[np.ndarray]:
    """
    Prepare frames for inference: convert to grayscale and normalize.
    
    Args:
        frames: List of frames (can be RGB or grayscale)
        normalize_method: Normalization method
    
    Returns:
        List of preprocessed frames (H, W), float32 [0, 1]
    """
    processed = []
    for frame in frames:
        # Convert to grayscale
        gray = convert_to_grayscale(frame)
        # Normalize
        normalized = normalize_frame(gray, method=normalize_method)
        processed.append(normalized)
    return processed
