"""Shared types used across Helix."""

from typing import List, Optional
from pydantic import BaseModel, Field


class PhaseToolOutput(BaseModel):
    """Structured output of the vision model (Phase + Tools)."""

    phase: str = Field(..., description="Predicted surgical phase")
    tools: List[str] = Field(default_factory=list, description="List of detected tools")
    phase_confidence: Optional[float] = Field(None, description="Confidence of the phase prediction (0-1)")
    tool_confidences: Optional[dict[str, float]] = Field(
        None, description="Optional per-tool confidence scores"
    )
