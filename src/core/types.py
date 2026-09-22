"""Shared structured types used across Helix.

Pydantic schemas that cross module boundaries (vision model I/O, RAG
responses, evaluation payloads) live here. Label vocabularies referenced
by these schemas come from `core.labels` — do not redefine them locally.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

from core.labels import CHOLEC80_PHASES, CHOLEC80_TOOLS


class PhaseToolOutput(BaseModel):
    """Structured output of the vision model: a phase label plus detected tools."""

    phase: str = Field(
        ...,
        description=f"Predicted surgical phase. One of: {', '.join(CHOLEC80_PHASES)}.",
    )
    tools: List[str] = Field(
        default_factory=list,
        description=(
            "Names of tools detected in the frame. Subset of: "
            f"{', '.join(CHOLEC80_TOOLS)}."
        ),
    )
    phase_confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0,
        description="Confidence of the phase prediction, in [0, 1].",
    )
    tool_confidences: Optional[dict[str, float]] = Field(
        None,
        description="Optional per-tool confidence scores, keyed by tool name.",
    )
