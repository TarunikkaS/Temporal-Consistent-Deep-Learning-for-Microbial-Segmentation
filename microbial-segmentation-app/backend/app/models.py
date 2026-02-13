"""
UNetTemporalFlow model architecture.
Matches the exact architecture from training (eval_iou_strack.py).
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


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
    def __init__(self, n_channels, n_classes, bilinear=False):
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


def load_model(checkpoint_path: str, device: str = "cuda") -> UNetTemporalFlow:
    """
    Load pretrained model from checkpoint.
    
    Args:
        checkpoint_path: Path to .pt checkpoint file
        device: Device to load model on ('cuda' or 'cpu')
    
    Returns:
        Loaded model in eval mode
    """
    model = UNetTemporalFlow(n_channels=13, n_classes=1)
    
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
            state_dict = checkpoint
            print("Loaded checkpoint as state_dict")
    else:
        state_dict = checkpoint
        print("Loaded checkpoint as plain state_dict")
    
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    
    print("✓ Model loaded successfully")
    return model
