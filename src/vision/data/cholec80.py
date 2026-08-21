"""
Cholec80 dataset loader.

TODO: Implement proper loading of videos, phase labels, and tool presence.
"""

from pathlib import Path
from torch.utils.data import Dataset


class Cholec80Dataset(Dataset):
    def __init__(self, root: str | Path, transform=None):
        self.root = Path(root)
        self.transform = transform
        # TODO: load video paths and annotations

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, idx):
        raise NotImplementedError
