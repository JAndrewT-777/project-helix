"""Image and video transforms for the vision pipeline."""

from torchvision import transforms

def get_default_transforms(image_size: int = 224):
    """Return standard training/inference transforms."""
    return transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ])
