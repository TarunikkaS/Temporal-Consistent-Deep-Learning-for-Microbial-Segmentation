"""
Post-processing: mask cleaning, phenotype classification, division detection.
"""
import numpy as np
from typing import Dict, List, Tuple
from skimage import measure, morphology
from skimage.measure import regionprops
import cv2


def clean_mask(mask: np.ndarray, min_area: int = 300, erosion_kernel_size: int = 3) -> np.ndarray:
    """
    Clean segmentation mask by removing small components and applying morphology.
    
    Args:
        mask: Binary mask (H, W), values in {0, 1}
        min_area: Minimum component area in pixels
        erosion_kernel_size: Kernel size for erosion (0 to skip)
    
    Returns:
        Cleaned binary mask
    """
    mask_binary = (mask > 0).astype(np.uint8)
    
    # Remove small connected components
    labeled = measure.label(mask_binary, connectivity=2)
    props = regionprops(labeled)
    
    cleaned = np.zeros_like(mask_binary)
    for prop in props:
        if prop.area >= min_area:
            cleaned[labeled == prop.label] = 1
    
    # Optional erosion for boundary stabilization
    if erosion_kernel_size > 0:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (erosion_kernel_size, erosion_kernel_size))
        cleaned = cv2.erode(cleaned, kernel, iterations=1)
    
    return cleaned


def compute_biomass(mask: np.ndarray) -> int:
    """
    Compute biomass proxy as total foreground pixels.
    
    Args:
        mask: Binary mask (H, W)
    
    Returns:
        Biomass count (number of foreground pixels)
    """
    return int(np.sum(mask > 0))


def classify_phenotype(region) -> str:
    """
    Classify cell phenotype based on region properties.
    
    Args:
        region: Region from skimage.measure.regionprops
    
    Returns:
        Phenotype label: 'rod_like', 'elongated', 'compact', or 'other'
    """
    # Compute aspect ratio
    if region.minor_axis_length > 0:
        aspect_ratio = region.major_axis_length / region.minor_axis_length
    else:
        # Fallback to bounding box aspect ratio
        minr, minc, maxr, maxc = region.bbox
        height = maxr - minr
        width = maxc - minc
        aspect_ratio = max(height, width) / (min(height, width) + 1e-6)
    
    area = region.area
    solidity = region.solidity if hasattr(region, 'solidity') else 1.0
    
    # Classification rules
    if aspect_ratio >= 3.0:
        return "elongated"
    elif aspect_ratio >= 2.0 and aspect_ratio < 3.0:
        if area > 200:  # Reasonable area for rod
            return "rod_like"
        else:
            return "other"
    elif aspect_ratio < 1.8 and solidity >= 0.8:
        return "compact"
    else:
        return "other"


def analyze_frame(mask: np.ndarray) -> Tuple[int, Dict[str, int], List[Dict]]:
    """
    Analyze frame mask to extract biomass, phenotype counts, and component details.
    
    Args:
        mask: Binary mask (H, W)
    
    Returns:
        biomass: Total foreground pixels
        phenotype_counts: Dict with counts per phenotype
        components: List of component dicts with properties
    """
    biomass = compute_biomass(mask)
    
    # Label connected components
    labeled = measure.label(mask, connectivity=2)
    props = regionprops(labeled)
    
    phenotype_counts = {
        "rod_like": 0,
        "elongated": 0,
        "compact": 0,
        "other": 0
    }
    
    components = []
    for prop in props:
        phenotype = classify_phenotype(prop)
        phenotype_counts[phenotype] += 1
        
        components.append({
            "label": int(prop.label),
            "phenotype": phenotype,
            "area": int(prop.area),
            "centroid": (float(prop.centroid[0]), float(prop.centroid[1])),
            "bbox": (int(prop.bbox[0]), int(prop.bbox[1]), int(prop.bbox[2]), int(prop.bbox[3]))
        })
    
    return biomass, phenotype_counts, components


def detect_division_events(
    biomass_history: List[int],
    component_counts: List[int],
    growth_spike_std: float = 1.0,
    component_increase_threshold: int = 1
) -> List[int]:
    """
    Detect division-like events based on growth spikes and/or topology changes.
    
    Args:
        biomass_history: List of biomass values over time
        component_counts: List of component counts over time
        growth_spike_std: Standard deviations above mean for growth spike
        component_increase_threshold: Minimum component count increase
    
    Returns:
        List of frame indices where division-like events occur
    """
    if len(biomass_history) < 3:
        return []
    
    # Compute growth rates
    growth_rates = []
    for i in range(1, len(biomass_history)):
        if biomass_history[i - 1] > 0:
            rate = np.log(biomass_history[i] / (biomass_history[i - 1] + 1e-6))
            growth_rates.append(rate)
        else:
            growth_rates.append(0.0)
    
    if len(growth_rates) == 0:
        return []
    
    # Compute statistics
    mean_rate = np.mean(growth_rates)
    std_rate = np.std(growth_rates)
    
    # Detect events
    division_events = []
    for i in range(1, len(growth_rates)):
        frame_idx = i + 1  # Adjust for growth rate offset
        
        # Check growth spike (if std_rate > 0)
        growth_spike = False
        if std_rate > 0:
            growth_spike = growth_rates[i] > (mean_rate + growth_spike_std * std_rate)
        
        # Check topology change (component count increase)
        component_increase = False
        if frame_idx < len(component_counts) and frame_idx > 0:
            comp_change = component_counts[frame_idx] - component_counts[frame_idx - 1]
            component_increase = comp_change >= component_increase_threshold
        
        # Division event if either condition is met (more sensitive detection)
        # Original was AND - now using OR for more detections
        if growth_spike or component_increase:
            division_events.append(frame_idx)
    
    return division_events


def render_overlay(
    original_frame: np.ndarray,
    pred_mask: np.ndarray,
    components: List[Dict],
    gt_mask: np.ndarray = None,
    alpha: float = 0.4,
    show_labels: bool = True
) -> np.ndarray:
    """
    Render side-by-side comparison: raw image | predicted mask overlay.
    
    Args:
        original_frame: Original grayscale or RGB frame (H, W) or (H, W, 3)
        pred_mask: Predicted binary mask (H, W)
        components: List of component dicts from analyze_frame
        gt_mask: Optional ground truth mask for comparison
        alpha: Transparency for mask overlay
        show_labels: Whether to show phenotype labels
    
    Returns:
        Side-by-side image (H, W*2, 3), uint8
    """
    # Convert original to RGB if needed
    if len(original_frame.shape) == 2:
        # Check if it's normalized [0,1] or uint8 [0,255]
        if original_frame.dtype == np.float32 or original_frame.dtype == np.float64:
            gray_uint8 = (original_frame * 255).astype(np.uint8)
        else:
            gray_uint8 = original_frame.astype(np.uint8)
        original_rgb = cv2.cvtColor(gray_uint8, cv2.COLOR_GRAY2RGB)
    else:
        if original_frame.dtype == np.float32 or original_frame.dtype == np.float64:
            original_rgb = (original_frame * 255).astype(np.uint8)
        else:
            original_rgb = original_frame.astype(np.uint8)
        if original_rgb.shape[2] == 1:
            original_rgb = cv2.cvtColor(original_rgb[:,:,0], cv2.COLOR_GRAY2RGB)
    
    # Left side: Original raw image
    left_panel = original_rgb.copy()
    
    # Right side: Overlay with orange masks
    right_panel = original_rgb.copy()
    
    # Create orange filled mask overlay
    mask_color = (0, 165, 255)  # Orange in BGR (Bitcoin Orange #F7931A approximation)
    pred_colored = np.zeros_like(right_panel)
    pred_colored[pred_mask > 0] = mask_color
    
    # Blend with original
    right_panel = cv2.addWeighted(right_panel, 1 - alpha, pred_colored, alpha, 0)
    
    # Add text overlay showing cell count and area
    cell_count = len(components)
    total_area = int(np.sum(pred_mask > 0))
    text = f"Pred | cells={cell_count} area={total_area}"
    
    # Add text with black background
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    thickness = 2
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    
    # Draw black rectangle background on right panel
    cv2.rectangle(right_panel, (5, 5), (text_width + 15, text_height + 15), (0, 0, 0), -1)
    
    # Draw green text on right panel
    cv2.putText(right_panel, text, (10, text_height + 10), font, font_scale, (0, 255, 0), thickness, cv2.LINE_AA)
    
    # Concatenate horizontally: [Raw | Predicted]
    combined = np.hstack([left_panel, right_panel])
    
    return combined


def add_division_marker(frame: np.ndarray, frame_idx: int) -> np.ndarray:
    """
    Add division-like event marker to frame.
    
    Args:
        frame: RGB frame (H, W, 3)
        frame_idx: Frame index number
    
    Returns:
        Frame with marker text
    """
    frame = frame.copy()
    text = f"DIVISION-LIKE EVENT (Frame {frame_idx})"
    
    # Add semi-transparent red banner at top
    banner_height = 40
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (frame.shape[1], banner_height), (0, 0, 255), -1)
    frame = cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)
    
    # Add text
    cv2.putText(
        frame, text, (10, 25),
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA
    )
    
    return frame
