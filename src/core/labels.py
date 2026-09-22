"""Dataset label vocabularies and id<->name mappings.

Single source of truth for class names and integer IDs across the project
(dataset loaders, models, evaluation, RAG). Any module that needs to encode
or decode a phase / tool label should import from here so we never have two
copies of the mapping drifting apart.

Cholec80 defines:
  * 7 mutually-exclusive surgical phases (per-frame, 25 fps).
  * 7 binary tool-presence labels (per-frame, 1 fps).

Ordering below matches the Cholec80 README so that class IDs are stable and
compatible with published baselines.
"""

from typing import Final

# --- Cholec80 phases -----------------------------------------------------

# Canonical phase order from the Cholec80 README. Tuple index == class ID.
CHOLEC80_PHASES: Final[tuple[str, ...]] = (
    "Preparation",
    "CalotTriangleDissection",
    "ClippingCutting",
    "GallbladderDissection",
    "GallbladderPackaging",
    "CleaningCoagulation",
    "GallbladderRetraction",
)
NUM_PHASES: Final[int] = len(CHOLEC80_PHASES)

PHASE_TO_ID: Final[dict[str, int]] = {name: i for i, name in enumerate(CHOLEC80_PHASES)}
ID_TO_PHASE: Final[dict[int, str]] = {i: name for i, name in enumerate(CHOLEC80_PHASES)}

# --- Cholec80 tools ------------------------------------------------------

# Canonical tool order from the Cholec80 README. Tuple index == class ID.
# Each label is a *binary* presence flag; multiple tools may be present in
# the same frame.
CHOLEC80_TOOLS: Final[tuple[str, ...]] = (
    "Grasper",
    "Bipolar",
    "Hook",
    "Scissors",
    "Clipper",
    "Irrigator",
    "SpecimenBag",
)
NUM_TOOLS: Final[int] = len(CHOLEC80_TOOLS)

TOOL_TO_ID: Final[dict[str, int]] = {name: i for i, name in enumerate(CHOLEC80_TOOLS)}
ID_TO_TOOL: Final[dict[int, str]] = {i: name for i, name in enumerate(CHOLEC80_TOOLS)}
