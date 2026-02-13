"""
Configuration settings for the backend application.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "temporal_unet_TC_finetuned.pt"))
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads")))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", str(BASE_DIR / "outputs")))

# Create directories
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# Model settings
DEVICE = os.getenv("DEVICE", "cuda")
TEMPORAL_WINDOW = 5  # T=5 frames
INPUT_CHANNELS = 13  # 5 frames + 8 flow channels

# Processing settings
DEFAULT_THRESHOLD = 0.5
DEFAULT_MIN_AREA = 300
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 500_000_000))  # 500MB

# Phenotype classification thresholds
PHENOTYPE_THRESHOLDS = {
    "rod_like": {"aspect_ratio_min": 2.0, "aspect_ratio_max": 3.0},
    "elongated": {"aspect_ratio_min": 3.0},
    "compact": {"aspect_ratio_max": 1.8, "solidity_min": 0.8},
}

# Division detection
DIVISION_GROWTH_SPIKE_STD = 2.0  # growth_rate > mean + 2*std
DIVISION_COMPONENT_INCREASE = 1  # component count increase
