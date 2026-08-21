"""
Official output schema for the vision component.

This is the contract between the vision model and the rest of Helix
(RAG, agents, etc.).
"""

from core.types import PhaseToolOutput

# Re-export for convenience
__all__ = ["PhaseToolOutput"]
