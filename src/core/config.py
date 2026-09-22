"""Project-wide runtime configuration.

This module holds settings that describe *where* and *how* the code runs:
filesystem paths, target device, and dataset roots. It intentionally does
NOT contain domain vocabularies (phase/tool names) — those live in
`core.labels` so they can be imported without pulling in path logic.
"""

from pathlib import Path

# --- Filesystem layout ----------------------------------------------------

# Repository root, resolved from this file's location: src/core/config.py -> repo root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# --- Runtime -------------------------------------------------------------

# Preferred torch device string ("cuda", "cpu", "mps", ...).
DEVICE = "cuda"

# --- Dataset roots -------------------------------------------------------

# Root of the Cholec80 dataset (contains `videos/`, `phase_annotations/`,
# `tool_annotations/`).
CHOLEC80_PATH = DATA_DIR / "cholec80"