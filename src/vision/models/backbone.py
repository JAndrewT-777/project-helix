"""Shared backbone models (ResNet, etc.)."""

import torch.nn as nn
from torchvision import models


def get_resnet50(pretrained: bool = True) -> nn.Module:
    """Return a ResNet-50 backbone."""
    weights = models.ResNet50_Weights.DEFAULT if pretrained else None
    model = models.resnet50(weights=weights)
    return model
