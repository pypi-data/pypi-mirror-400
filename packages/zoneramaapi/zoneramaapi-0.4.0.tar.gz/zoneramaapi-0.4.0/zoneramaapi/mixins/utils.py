import base64
from pathlib import Path


def load_image_base64(image_path: Path) -> str:
    """Load an image file and return it as a base64-encoded string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
