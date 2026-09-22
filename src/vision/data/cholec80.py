"""
Cholec80 dataset loader.

TODO: Implement proper loading of videos, phase labels, and tool presence.
"""

from pathlib import Path
import random
import re
from torch.utils.data import Dataset

import core.config
from core.labels import PHASE_TO_ID, NUM_TOOLS
import numpy as np

def _timestamp_to_seconds(ts: str) -> float:
    """Convert 'HH:MM:SS.ff' to seconds as float."""
    h, m, s = ts.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def _video_id_from_stem(stem: str) -> int:
    """Parse the numeric video index out of a stem like 'video01' -> 1."""
    match = re.search(r"\d+", stem)
    if match is None:
        raise ValueError(f"could not parse a video id from stem: {stem!r}")
    return int(match.group())


def load_timestamps(path: str | Path) -> np.ndarray:
    """Load the timestamp column of a videoNN-timestamp.txt file as a column vector (N, 1)."""
    vec = np.loadtxt(
        path,
        dtype=np.float64,
        delimiter="\t",
        skiprows=1,           # skip the "Frame\tPhase" header
        usecols=0,            # keep only the timestamp column
        converters={0: _timestamp_to_seconds},
    )
    return vec.reshape(-1, 1)


def load_phases(path: str | Path) -> np.ndarray:
    """Load the phase column of a videoNN-phase.txt file as a column vector (N, 1) of phase IDs."""
    names = np.loadtxt(
        path,
        dtype=str,
        delimiter="\t",
        skiprows=1,           # skip the "Frame\tPhase" header
        usecols=1,            # keep only the phase name column
    )
    ids = np.array([PHASE_TO_ID[name] for name in np.atleast_1d(names)], dtype=np.float64)
    return ids.reshape(-1, 1)


def load_tools(path: str | Path, num_frames: int) -> np.ndarray:
    """Load tool presence annotations as a per-frame array (num_frames, 7).

    Tool annotations are sampled at 1 fps (every 25 frames at Cholec80's 25 fps),
    while timestamps/phases are per-frame. Each annotated row is forward-filled
    across the 25 frames it covers so the result aligns with the per-frame arrays.

    Raises:
        ValueError: if the file doesn't have exactly `NUM_TOOLS` tool columns,
            contains non-binary values, or is missing more than one 1s interval
            (25 frames) of coverage relative to `num_frames`.
    """
    path = Path(path)
    data = np.loadtxt(path, dtype=np.float64, delimiter="\t", skiprows=1)
    data = np.atleast_2d(data)
    tool_vals = data[:, 1:]  # drop the frame-index column -> (M, 7)

    if tool_vals.shape[1] != NUM_TOOLS:
        raise ValueError(
            f"{path.name}: expected {NUM_TOOLS} tool columns, got {tool_vals.shape[1]}"
        )
    if not np.isin(tool_vals, (0.0, 1.0)).all():
        raise ValueError(f"{path.name}: tool values must be binary (0 or 1)")

    per_frame = np.repeat(tool_vals, 25, axis=0)
    shortfall = num_frames - per_frame.shape[0]
    if shortfall > 0:
        if shortfall >= 25:
            # More than one missing 1s interval — likely a truncated/corrupt file,
            # not just rounding. Fail loudly instead of padding over real data loss.
            raise ValueError(
                f"{path.name}: tool annotations cover {per_frame.shape[0]} frames, "
                f"{shortfall} short of {num_frames} expected — file may be truncated"
            )
        # Pad with the last annotated row if num_frames isn't an exact multiple of 25.
        pad = np.repeat(per_frame[-1:], shortfall, axis=0)
        per_frame = np.vstack([per_frame, pad])
    return per_frame[:num_frames]


class Cholec80Dataset(Dataset):
    def __init__(self, root: str | Path, transform=None):
        self.root = Path(root)
        self.video_dir = self.root / "videos"
        self.phase_antn_dir = self.root / "phase_annotations"
        self.tool_antn_dir = self.root / "tool_annotations"
        self.transform = transform

        # Get the number of viedeo files in the dataset
        self.video_files = sorted(list(self.video_dir.glob("*.mp4")), key=lambda x: x.name)
        print(f"Found {len(self.video_files)} video files in {self.video_dir}")
        #print(f"Video files: {[video.name for video in self.video_files]}")

        # Flat (total_N, 10) array across all videos:
        # column 0 = video id (parsed from the filename stem, e.g. "video01" -> 1),
        # column 1 = timestamp seconds, column 2 = phase id, columns 3-9 = tool presence.
        # video_names maps video id -> stem, for debugging/lookup back to the source file.
        self.video_names: dict[int, str] = {}
        blocks: list[np.ndarray] = []
        for video in self.video_files:
            ts_path = self.video_dir / f"{video.stem}-timestamp.txt"
            phase_path = self.phase_antn_dir / f"{video.stem}-phase.txt"
            tool_path = self.tool_antn_dir / f"{video.stem}-tool.txt"

            if not ts_path.exists():
                print(f"[warn] missing timestamp file: {ts_path.name}")
                continue
            if not phase_path.exists():
                print(f"[warn] missing phase annotation file: {phase_path.name}")
                continue
            if not tool_path.exists():
                print(f"[warn] missing tool annotation file: {tool_path.name}")
                continue

            ts = load_timestamps(ts_path)      # (N, 1)
            phases = load_phases(phase_path)   # (M, 1)

            if ts.shape[0] != phases.shape[0]:
                print(
                    f"[warn] length mismatch for {video.stem}: "
                    f"timestamps={ts.shape[0]}, phases={phases.shape[0]} \u2014 skipping"
                )
                continue

            try:
                tools = load_tools(tool_path, num_frames=ts.shape[0])  # (N, 7)
            except ValueError as e:
                print(f"[warn] skipping {video.stem}: {e}")
                continue

            video_id = _video_id_from_stem(video.stem)
            video_id_col = np.full((ts.shape[0], 1), video_id, dtype=np.float64)
            self.video_names[video_id] = video.stem
            blocks.append(np.hstack([video_id_col, ts, phases, tools]))  # (N, 10)

        self.samples: np.ndarray = np.vstack(blocks) if blocks else np.empty((0, 10))

        # Sanity check: show per-video row counts within the merged array.
        for video_id, stem in self.video_names.items():
            count = int(np.count_nonzero(self.samples[:, 0] == video_id))
            print(f"{stem} (video_id={video_id}): rows={count}")

        # Display a random 10-row window from a random video for variety across runs.
        # suppress=True forces fixed-point notation, avoiding NumPy's automatic
        # switch to scientific notation when a row's values span a wide magnitude
        # range (e.g. a timestamp in the thousands next to a binary tool flag).
        with np.printoptions(suppress=True):
            for i in range(3):
                if self.video_names:
                    video_id = random.choice(list(self.video_names.keys()))
                    rows = np.flatnonzero(self.samples[:, 0] == video_id)
                    start = random.randint(0, max(0, rows.shape[0] - 10))
                    window = self.samples[rows[start:start + 10]]
                    print(
                        f"\nRows {start}-{start + window.shape[0] - 1} for "
                        f"{self.video_names[video_id]} "
                        f"[video_id, time_s, phase_id, tools...]:\n{window}"
                    )




    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, idx):
        raise NotImplementedError


def main():
    """Main function for testing."""
    print("CHOLEC80_PATH:", core.config.CHOLEC80_PATH)

    dataset = Cholec80Dataset(root=core.config.CHOLEC80_PATH)
    #print(f"Number of videos: {len(dataset)}")


if __name__ == "__main__":
    main()



