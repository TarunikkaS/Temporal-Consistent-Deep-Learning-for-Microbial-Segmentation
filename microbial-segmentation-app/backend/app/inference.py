"""
Inference pipeline: orchestrates the full segmentation workflow.
"""
import torch
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import shutil

from .models import load_model
from .preprocessing import prepare_frames_for_inference, build_13channel_input
from .postprocessing import (
    clean_mask, analyze_frame, detect_division_events
)
from .render import save_frame_images, create_video_from_frames, create_overlay
from .video_utils import (
    read_video_frames, extract_dataset_from_zip,
    create_frame_sequence
)
from .job_manager import job_manager, JobStatus, JobStage
from .config import MODEL_PATH, OUTPUT_DIR, DEVICE, DEFAULT_THRESHOLD, DEFAULT_MIN_AREA


class InferenceEngine:
    """Main inference engine for segmentation pipeline."""
    
    def __init__(self, model_path: str = MODEL_PATH, device: str = DEVICE):
        """Initialize inference engine with model."""
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.model = load_model(model_path, str(self.device))
        print(f"Model loaded on device: {self.device}")
    
    def process_video(
        self,
        video_path: str,
        job_id: str,
        threshold: float = DEFAULT_THRESHOLD,
        min_area: int = DEFAULT_MIN_AREA,
        **kwargs
    ) -> Dict:
        """
        Process video file end-to-end.
        
        Args:
            video_path: Path to MP4 video
            job_id: Unique job identifier
            threshold: Segmentation threshold
            min_area: Minimum component area
        
        Returns:
            Results dictionary
        """
        try:
            # Update status
            job_manager.update_job(
                job_id,
                status=JobStatus.RUNNING,
                stage=JobStage.PREPROCESSING,
                progress=5.0,
                message="Reading video frames"
            )
            
            # Read video
            frames_rgb, fps = read_video_frames(video_path)
            
            # Convert to grayscale and normalize
            frames_gray = prepare_frames_for_inference(frames_rgb)
            
            # Run inference
            results = self._run_inference_pipeline(
                frames_gray=frames_gray,
                frames_rgb=frames_rgb,
                gt_masks=None,
                job_id=job_id,
                threshold=threshold,
                min_area=min_area,
                fps=fps
            )
            
            return results
            
        except Exception as e:
            job_manager.mark_failed(job_id, str(e))
            raise
    
    def process_dataset(
        self,
        dataset_path: str,
        job_id: str,
        threshold: float = DEFAULT_THRESHOLD,
        min_area: int = DEFAULT_MIN_AREA,
        **kwargs
    ) -> Dict:
        """
        Process dataset zip file or directory.
        
        Args:
            dataset_path: Path to dataset zip or directory
            job_id: Unique job identifier
            threshold: Segmentation threshold
            min_area: Minimum component area
        
        Returns:
            Results dictionary
        """
        try:
            # Update status
            job_manager.update_job(
                job_id,
                status=JobStatus.RUNNING,
                stage=JobStage.PREPROCESSING,
                progress=5.0,
                message="Loading dataset"
            )
            
            dataset_path_obj = Path(dataset_path)
            
            # Check if it's a directory or zip
            if dataset_path_obj.is_dir():
                # Load directly from directory
                frames_gray, gt_masks = self._load_frames_from_directory(dataset_path)
                extract_path = None
            else:
                # Extract dataset from zip
                frames_gray, gt_masks, extract_path = extract_dataset_from_zip(dataset_path)
            
            if len(frames_gray) == 0:
                raise ValueError("No frames found in dataset")
            
            # Convert grayscale to RGB for visualization
            frames_rgb = [np.stack([f, f, f], axis=-1) for f in frames_gray]
            
            # Run inference
            results = self._run_inference_pipeline(
                frames_gray=frames_gray,
                frames_rgb=frames_rgb,
                gt_masks=gt_masks if len(gt_masks) > 0 else None,
                job_id=job_id,
                threshold=threshold,
                min_area=min_area,
                fps=2.0  # Slower playback for time-lapse datasets (2 fps)
            )
            
            # Cleanup extraction if needed
            if extract_path:
                try:
                    shutil.rmtree(extract_path)
                except:
                    pass
            
            return results
            
        except Exception as e:
            job_manager.mark_failed(job_id, str(e))
            raise
    
    def _load_frames_from_directory(self, directory: str) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """
        Load frames from a directory of image files.
        
        Args:
            directory: Path to directory containing images (or parent with raw_images subdirectory)
        
        Returns:
            Tuple of (frames_gray, gt_masks) - frames_gray are float32 [0,1], gt_masks are uint8 binary
        """
        from PIL import Image
        import glob
        
        dir_path = Path(directory)
        
        # Check if this is a STRACK-style dataset with subdirectories
        raw_images_dir = dir_path / "raw_images" if (dir_path / "raw_images").exists() else dir_path
        masks_dir = dir_path / "manual_segmentation_masks" if (dir_path / "manual_segmentation_masks").exists() else None
        
        # Find all image files (TIFF, PNG, JPG)
        image_patterns = ['*.tif', '*.tiff', '*.TIF', '*.TIFF', '*.png', '*.PNG', '*.jpg', '*.JPG', '*.jpeg', '*.JPEG']
        image_files = []
        for pattern in image_patterns:
            image_files.extend(sorted(raw_images_dir.glob(pattern)))
        
        if not image_files:
            raise ValueError(f"No image files found in {raw_images_dir}")
        
        frames_gray = []
        for img_path in image_files:
            img = Image.open(img_path)
            # Handle all image types - normalize to float32 [0, 1]
            if img.mode in ['I;16', 'I;16B', 'I;16L', 'I']:
                # 16-bit images: convert to numpy and normalize
                arr = np.array(img, dtype=np.float32)
            elif img.mode != 'L':
                img = img.convert('L')
                arr = np.array(img, dtype=np.float32)
            else:
                arr = np.array(img, dtype=np.float32)
            
            # Normalize to [0, 1]
            arr_min, arr_max = arr.min(), arr.max()
            if arr_max > arr_min:
                arr = (arr - arr_min) / (arr_max - arr_min)
            else:
                arr = np.zeros_like(arr)
            frames_gray.append(arr)
        
        # Load ground truth masks if available
        gt_masks = []
        if masks_dir and masks_dir.exists():
            mask_files = []
            for pattern in image_patterns:
                mask_files.extend(sorted(masks_dir.glob(pattern)))
            
            for mask_path in mask_files:
                mask_img = Image.open(mask_path)
                if mask_img.mode in ['I;16', 'I;16B', 'I;16L', 'I']:
                    mask_array = np.array(mask_img, dtype=np.float32)
                    # Threshold at midpoint
                    mask_binary = (mask_array > (mask_array.max() / 2)).astype(np.uint8)
                else:
                    if mask_img.mode != 'L':
                        mask_img = mask_img.convert('L')
                    mask_array = np.array(mask_img, dtype=np.uint8)
                    # Binarize mask (assume non-zero pixels are foreground)
                    mask_binary = (mask_array > 0).astype(np.uint8)
                gt_masks.append(mask_binary)
        
        return frames_gray, gt_masks
    
    def _run_inference_pipeline(
        self,
        frames_gray: List[np.ndarray],
        frames_rgb: List[np.ndarray],
        gt_masks: Optional[List[np.ndarray]],
        job_id: str,
        threshold: float,
        min_area: int,
        fps: float
    ) -> Dict:
        """Run complete inference pipeline."""
        
        # Create output directories
        output_dir = OUTPUT_DIR / job_id
        frames_dir = output_dir / "frames"
        frames_dir.mkdir(parents=True, exist_ok=True)
        
        # Normalize frames to [0, 1] for model input
        frames_normalized = []
        for frame in frames_gray:
            if frame.dtype == np.uint8:
                # Convert uint8 [0, 255] to float32 [0, 1]
                frame_norm = frame.astype(np.float32) / 255.0
            elif frame.max() > 1.0:
                # Already float but not normalized
                frame_norm = (frame - frame.min()) / (frame.max() - frame.min() + 1e-8)
            else:
                frame_norm = frame.astype(np.float32)
            frames_normalized.append(frame_norm)
        
        # Create temporal windows
        job_manager.update_job(
            job_id,
            stage=JobStage.INFERENCE,
            progress=10.0,
            message="Creating temporal windows"
        )
        
        sequences = create_frame_sequence(frames_normalized, window_size=5)
        total_frames = len(sequences)
        
        # Storage for results
        all_masks = []
        all_biomass = []
        all_phenotype_counts = []
        all_components_list = []
        overlay_frames = []
        
        # Inference loop
        for idx, (center_idx, window_frames) in enumerate(sequences):
            # Progress update
            progress = 10.0 + (idx / total_frames) * 50.0
            if idx % max(1, total_frames // 20) == 0:
                job_manager.update_job(
                    job_id,
                    progress=progress,
                    message=f"Inference: frame {idx + 1}/{total_frames}"
                )
            
            # Build input tensor
            input_tensor = build_13channel_input(window_frames)
            input_batch = input_tensor.unsqueeze(0).to(self.device)
            
            # Forward pass
            with torch.no_grad():
                output = self.model(input_batch)
                pred_mask = torch.sigmoid(output).squeeze(0).squeeze(0).cpu().numpy()
            
            # Threshold and clean
            pred_mask_binary = (pred_mask > threshold).astype(np.float32)
            pred_mask_clean = clean_mask(pred_mask_binary, min_area=min_area)
            
            all_masks.append(pred_mask_clean)
            
            # Analyze frame
            biomass, phenotype_counts, components = analyze_frame(pred_mask_clean)
            all_biomass.append(biomass)
            all_phenotype_counts.append(phenotype_counts)
            all_components_list.append(components)
        
        # Post-processing
        job_manager.update_job(
            job_id,
            stage=JobStage.POSTPROCESSING,
            progress=65.0,
            message="Detecting division events"
        )
        
        # Detect division events
        component_counts = [len(comps) for comps in all_components_list]
        division_events = detect_division_events(
            all_biomass,
            component_counts,
            growth_spike_std=2.0,
            component_increase_threshold=1
        )
        
        # Compute growth rates
        growth_rates = []
        for i in range(1, len(all_biomass)):
            if all_biomass[i - 1] > 0:
                rate = np.log(all_biomass[i] / (all_biomass[i - 1] + 1e-6))
                growth_rates.append(rate)
            else:
                growth_rates.append(0.0)
        growth_rates.insert(0, 0.0)  # First frame has no growth rate
        
        # Generate overlays
        job_manager.update_job(
            job_id,
            stage=JobStage.VIDEO_GENERATION,
            progress=70.0,
            message="Generating overlay frames"
        )
        
        orig_frames = []
        gt_frames = []
        pred_frames = []
        triplet_frames = []
        overlay_frames_for_video = []
        
        for idx, (center_idx, _) in enumerate(sequences):
            progress = 70.0 + (idx / total_frames) * 20.0
            if idx % max(1, total_frames // 10) == 0:
                job_manager.update_job(
                    job_id,
                    progress=progress,
                    message=f"Rendering: frame {idx + 1}/{total_frames}"
                )
            
            # Get corresponding data
            original_frame = frames_rgb[center_idx]
            pred_mask = all_masks[idx]
            gt_mask = gt_masks[center_idx] if gt_masks and center_idx < len(gt_masks) else None
            
            # Get areas
            pred_area = all_biomass[idx]
            gt_area = int(np.sum(gt_mask > 0)) if gt_mask is not None else None
            growth_rate = growth_rates[idx]
            
            # Save all frame variants
            urls = save_frame_images(
                output_dir,
                idx,
                original_frame,
                pred_mask,
                gt_mask,
                fps,
                pred_area,
                gt_area,
                growth_rate
            )
            
            orig_frames.append(urls['orig'])
            gt_frames.append(urls['gt'])
            pred_frames.append(urls['pred'])
            triplet_frames.append(urls['triplet'])
            
            # Create overlay for video
            overlay = create_overlay(original_frame, pred_mask, color=(255, 165, 0), alpha=0.4)
            overlay_frames_for_video.append(overlay)
        
        # Generate output video
        job_manager.update_job(
            job_id,
            progress=90.0,
            message="Creating output video"
        )
        
        video_path = output_dir / "overlay.mp4"
        create_video_from_frames(overlay_frames_for_video, video_path, fps=fps)
        
        # Save metrics CSV
        job_manager.update_job(
            job_id,
            progress=95.0,
            message="Saving metrics"
        )
        
        # Prepare metrics DataFrame
        metrics_data = {
            "frame": list(range(len(all_biomass))),
            "time": [i / fps for i in range(len(all_biomass))],
            "area_pred": all_biomass,
            "growth_pred": growth_rates,
            "component_count": component_counts,
            "rod_like": [pc["rod_like"] for pc in all_phenotype_counts],
            "elongated": [pc["elongated"] for pc in all_phenotype_counts],
            "compact": [pc["compact"] for pc in all_phenotype_counts],
            "other": [pc["other"] for pc in all_phenotype_counts],
            "division_like": [1 if i in division_events else 0 for i in range(len(all_biomass))]
        }
        
        # Add GT biomass if available
        if gt_masks:
            area_gt = []
            for idx, (center_idx, _) in enumerate(sequences):
                if center_idx < len(gt_masks):
                    area_gt.append(int(np.sum(gt_masks[center_idx] > 0)))
                else:
                    area_gt.append(0)
            metrics_data["area_gt"] = area_gt
        
        df = pd.DataFrame(metrics_data)
        csv_path = output_dir / "metrics.csv"
        df.to_csv(csv_path, index=False)
        
        # Prepare full URL results
        base_url = "http://localhost:8000"
        
        results = {
            "job_id": job_id,
            "n_frames": total_frames,
            "fps": float(fps),
            "triplet_frames": [f"{base_url}{url}" for url in triplet_frames],
            "orig_frames": [f"{base_url}{url}" for url in orig_frames],
            "pred_frames": [f"{base_url}{url}" for url in pred_frames],
            "gt_frames": [f"{base_url}{url}" if url else None for url in gt_frames],
            "video_url": f"{base_url}/static/{job_id}/overlay.mp4",
            "csv_url": f"{base_url}/static/{job_id}/metrics.csv",
            "metrics": {
                "time": [float(t) for t in metrics_data["time"]],
                "area_pred": [int(a) for a in metrics_data["area_pred"]],
                "area_gt": [int(a) for a in metrics_data["area_gt"]] if metrics_data.get("area_gt") else None,
                "growth_pred": [float(g) for g in metrics_data["growth_pred"]],
                "division_like": [int(d) for d in metrics_data["division_like"]],
                "component_count": [int(c) for c in metrics_data["component_count"]],
                "phenotype_counts": [
                    {
                        "rod_like": int(metrics_data["rod_like"][i]),
                        "elongated": int(metrics_data["elongated"][i]),
                        "compact": int(metrics_data["compact"][i]),
                        "other": int(metrics_data["other"][i])
                    }
                    for i in range(len(metrics_data["rod_like"]))
                ]
            }
        }
        
        # Mark job as completed
        job_manager.mark_completed(job_id, results)
        
        return results
