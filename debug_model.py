import torch
import numpy as np
from PIL import Image
import sys
sys.path.append('.')

# Quick test
from eval_iou_strack import UNetTemporalFlow, load_checkpoint, build_13channel_input

device = torch.device('cpu')
model = UNetTemporalFlow(n_channels=13, n_classes=1)
model = load_checkpoint(model, "temporal_unet_TC_finetuned.pt", device)
model.eval()

# Load a sample image
img_path = "Lysobacter/Time-lapse_dataset1/raw_images/pic_001.tif"
img = Image.open(img_path).convert('L')
img_array = np.array(img, dtype=np.float32) / 255.0

print(f"Image shape: {img_array.shape}")
print(f"Image range: [{img_array.min():.3f}, {img_array.max():.3f}]")

# Create dummy 5 frames (using same image)
frames = [img_array] * 5

# Build input
input_tensor = build_13channel_input(frames)
print(f"Input shape: {input_tensor.shape}")
print(f"Input range: [{input_tensor.min():.3f}, {input_tensor.max():.3f}]")

# Forward pass
with torch.no_grad():
    input_batch = input_tensor.unsqueeze(0)
    output = model(input_batch)
    pred = torch.sigmoid(output)
    
print(f"Output shape: {output.shape}")
print(f"Output range: [{output.min():.3f}, {output.max():.3f}]")
print(f"Prediction (sigmoid) range: [{pred.min():.3f}, {pred.max():.3f}]")
print(f"Prediction mean: {pred.mean():.3f}")
print(f"Prediction > 0.5: {(pred > 0.5).sum().item()} pixels")

# Check mask
mask_path = "Lysobacter/Time-lapse_dataset1/manual_segmentation_masks/pic_001.tif"
mask = Image.open(mask_path).convert('L')
mask_array = np.array(mask, dtype=np.float32)
mask_binary = (mask_array > 0).astype(np.float32)

print(f"\nMask shape: {mask_binary.shape}")
print(f"Mask sum (positive pixels): {mask_binary.sum():.0f}")
print(f"Mask percentage: {100 * mask_binary.mean():.2f}%")
