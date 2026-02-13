# Model Files

Due to GitHub file size limitations, the trained model files are not included in this repository.

## Required Model Files

Please download the following model files separately:

1. **temporal_unet_TC_finetuned.pt** (30 MB) - Main fine-tuned model
2. **temporal_unet_strack.pth** (89 MB) - Base tracking model  
3. **temporal_unet_strack_clean.pt** (30 MB) - Clean checkpoint

## Placement

After downloading, place the model files in the project root directory:
```
/
├── temporal_unet_TC_finetuned.pt
├── temporal_unet_strack.pth
├── temporal_unet_strack_clean.pt
└── ...
```

For the web application, also copy `temporal_unet_TC_finetuned.pt` to:
```
microbial-segmentation-app/backend/temporal_unet_TC_finetuned.pt
```

## Alternative: Train Your Own Model

You can train your own models using the provided [MICROBIAL FINAL.ipynb](MICROBIAL%20FINAL.ipynb) notebook with the included dataset.
