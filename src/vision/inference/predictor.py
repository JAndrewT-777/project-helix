"""
High-level predictor interface.

This is the main entry point the rest of Helix will use.
"""

from pathlib import Path
from typing import Union
import torch
from PIL import Image

from core.types import PhaseToolOutput
from vision.models.phase_tool import PhaseToolModel
from vision.data.transforms import get_default_transforms


class PhaseToolPredictor:
    def __init__(self, model: PhaseToolModel, device: str = "cuda", class_names: dict = None):
        self.model = model.to(device)
        self.model.eval()
        self.device = device
        self.transform = get_default_transforms()
        self.class_names = class_names or {}

    @torch.inference_mode()
    def predict(self, image: Union[str, Path, Image.Image]) -> PhaseToolOutput:
        """
        Run inference on a single image and return structured output.
        """
        if isinstance(image, (str, Path)):
            image = Image.open(image).convert("RGB")

        tensor = self.transform(image).unsqueeze(0).to(self.device)
        phase_logits, tool_logits = self.model(tensor)

        # TODO: convert logits → phase name + tool list + confidences
        raise NotImplementedError("Implement logit → PhaseToolOutput conversion")
