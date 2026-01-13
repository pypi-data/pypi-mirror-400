"""Visualization utilities for Computer Use tool.

Functions for drawing markers on images to visualize model predictions.
"""

from pathlib import Path

from PIL import Image, ImageColor, ImageDraw


def draw_point(
    image: str | Path | Image.Image,
    point: list[int] | tuple[int, int],
    color: str | tuple = "red",
    radius_ratio: float = 0.05,
    center_dot: bool = True,
) -> Image.Image:
    """Draw a point marker on an image to highlight a GUI element.

    Creates a semi-transparent circle with an optional center dot
    to visualize where the model predicts to click.

    Args:
        image: Image file path or PIL Image object.
        point: (x, y) coordinate to mark.
        color: Color name (e.g., "red", "green") or RGB tuple.
        radius_ratio: Radius as ratio of min image dimension (default 0.05 = 5%).
        center_dot: Whether to draw a small center dot.

    Returns:
        New PIL Image with the point marker drawn.

    Example:
        ```python
        from lookit.utils import draw_point

        # Mark where the model predicted to click
        result_image = draw_point("screenshot.png", [500, 300], color="green")
        result_image.save("result.png")
        ```
    """
    # Load image if path
    if isinstance(image, (str, Path)):
        image = Image.open(image)
    else:
        image = image.copy()

    # Parse color
    if isinstance(color, str):
        try:
            rgb = ImageColor.getrgb(color)
            fill_color = rgb + (128,)  # Add alpha for semi-transparency
        except ValueError:
            fill_color = (255, 0, 0, 128)  # Default red
    else:
        fill_color = color if len(color) == 4 else color + (128,)

    # Create overlay for transparency
    overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    # Calculate radius based on image size
    radius = min(image.size) * radius_ratio
    x, y = point

    # Draw main circle
    draw.ellipse(
        [(x - radius, y - radius), (x + radius, y + radius)],
        fill=fill_color,
    )

    # Draw center dot
    if center_dot:
        center_radius = radius * 0.15
        draw.ellipse(
            [(x - center_radius, y - center_radius), (x + center_radius, y + center_radius)],
            fill=(0, 255, 0, 255),  # Solid green
        )

    # Composite overlay onto image
    image = image.convert("RGBA")
    result = Image.alpha_composite(image, overlay)

    return result.convert("RGB")


def draw_action(
    image: str | Path | Image.Image,
    action: str,
    coordinate: list[int] | tuple[int, int] | None = None,
    text: str | None = None,
) -> Image.Image:
    """Draw visualization for a computer use action.

    Args:
        image: Image file path or PIL Image object.
        action: Action type (left_click, type, etc.).
        coordinate: (x, y) coordinate for click actions.
        text: Text for type action (shown as annotation).

    Returns:
        Annotated PIL Image.
    """
    # Load image if path
    if isinstance(image, (str, Path)):
        image = Image.open(image)
    else:
        image = image.copy()

    # Color mapping for different actions
    action_colors = {
        "left_click": "green",
        "right_click": "blue",
        "double_click": "yellow",
        "triple_click": "orange",
        "middle_click": "purple",
        "mouse_move": "cyan",
        "left_click_drag": "magenta",
    }

    if coordinate and action in action_colors:
        image = draw_point(image, coordinate, color=action_colors[action])

    return image


def draw_trajectory(
    image: str | Path | Image.Image,
    points: list[list[int] | tuple[int, int]],
    color: str = "blue",
    line_width: int = 2,
) -> Image.Image:
    """Draw a trajectory of points on an image.

    Useful for visualizing drag operations or mouse movement paths.

    Args:
        image: Image file path or PIL Image object.
        points: List of (x, y) coordinates forming the trajectory.
        color: Line and point color.
        line_width: Width of connecting lines.

    Returns:
        PIL Image with trajectory drawn.
    """
    if isinstance(image, (str, Path)):
        image = Image.open(image)
    else:
        image = image.copy()

    if len(points) < 2:
        if points:
            return draw_point(image, points[0], color=color)
        return image

    draw = ImageDraw.Draw(image)

    # Draw lines connecting points
    for i in range(len(points) - 1):
        draw.line([tuple(points[i]), tuple(points[i + 1])], fill=color, width=line_width)

    # Draw points
    for i, point in enumerate(points):
        # Start point in green, end point in red, others in specified color
        if i == 0:
            image = draw_point(image, point, color="green", radius_ratio=0.03)
        elif i == len(points) - 1:
            image = draw_point(image, point, color="red", radius_ratio=0.03)
        else:
            image = draw_point(image, point, color=color, radius_ratio=0.02, center_dot=False)

    return image
