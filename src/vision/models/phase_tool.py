"""
Phase + Tool recognition model.

This is the main vision model for Helix v0.1.
"""

import torch
import torch.nn as nn
from vision.models.backbone import get_resnet50


class PhaseToolModel(nn.Module):
    def __init__(self, num_phases: int, num_tools: int, pretrained: bool = True):
        super().__init__()
        self.backbone = get_resnet50(pretrained=pretrained)
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Identity()

        self.phase_head = nn.Linear(in_features, num_phases)
        self.tool_head = nn.Linear(in_features, num_tools)

    def forward(self, x: torch.Tensor):
        features = self.backbone(x)
        phase_logits = self.phase_head(features)
        tool_logits = self.tool_head(features)
        return phase_logits, tool_logits
