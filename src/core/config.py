"""Project-wide configuration and constants."""

from pathlib import Path

# Project root (adjust if needed)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Common paths
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Device
DEVICE = "cuda"  # or "cpu"
