"""Image utility functions for Computer Use tool."""

import base64
from io import BytesIO
from pathlib import Path

from PIL import Image


def load_image(image_path: str | Path) -> Image.Image:
    """Load an image from file path.

    Args:
        image_path: Path to the image file.

    Returns:
        PIL Image object.
    """
    return Image.open(image_path)


def encode_image_to_base64(image: str | Path | Image.Image, format: str = "PNG") -> str:
    """Encode an image to base64 string.

    Args:
        image: Either a file path or PIL Image object.
        format: Image format for encoding (PNG, JPEG, etc.).

    Returns:
        Base64 encoded string of the image.
    """
    if isinstance(image, (str, Path)):
        with open(image, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    # PIL Image
    buffer = BytesIO()
    image.save(buffer, format=format)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def create_image_message(
    image: str | Path | Image.Image,
    text: str,
    format: str = "PNG",
) -> list[dict]:
    """Create a multimodal message with image and text for LangChain.

    Args:
        image: Image file path or PIL Image object.
        text: Text prompt to accompany the image.
        format: Image format (PNG, JPEG).

    Returns:
        List of content items for HumanMessage.

    Example:
        ```python
        from langchain_core.messages import HumanMessage

        content = create_image_message("screenshot.png", "Click the submit button")
        message = HumanMessage(content=content)
        ```
    """
    b64_image = encode_image_to_base64(image, format=format)
    mime_type = f"image/{format.lower()}"

    return [
        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64_image}"}},
        {"type": "text", "text": text},
    ]


def get_image_dimensions(image: str | Path | Image.Image) -> tuple[int, int]:
    """Get width and height of an image.

    Args:
        image: Image file path or PIL Image object.

    Returns:
        Tuple of (width, height) in pixels.
    """
    if isinstance(image, (str, Path)):
        with Image.open(image) as img:
            return img.size
    return image.size
