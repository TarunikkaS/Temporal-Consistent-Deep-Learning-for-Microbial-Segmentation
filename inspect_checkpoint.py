import torch

checkpoint = torch.load("temporal_unet_TC_finetuned.pt", map_location='cpu')
if isinstance(checkpoint, dict):
    if 'model_state' in checkpoint:
        state_dict = checkpoint['model_state']
    elif 'state_dict' in checkpoint:
        state_dict = checkpoint['state_dict']
    else:
        state_dict = checkpoint
else:
    state_dict = checkpoint

print("Checkpoint keys:")
for key in sorted(state_dict.keys()):
    print(f"  {key}: {state_dict[key].shape}")
