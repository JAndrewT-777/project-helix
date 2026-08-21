"""Post-processing utilities for vision model outputs."""

import torch
import torch.nn.functional as F


def logits_to_phase(logits: torch.Tensor, phase_names: list[str]) -> tuple[str, float]:
    """Convert phase logits to phase name + confidence."""
    probs = F.softmax(logits, dim=-1)
    conf, idx = torch.max(probs, dim=-1)
    return phase_names[idx.item()], conf.item()


def logits_to_tools(logits: torch.Tensor, tool_names: list[str], threshold: float = 0.5) -> list[str]:
    """Convert tool logits to list of detected tools."""
    probs = torch.sigmoid(logits)
    detected = [name for name, p in zip(tool_names, probs[0]) if p >= threshold]
    return detected
