"""Mobile Use Tool for LangChain.

A schema-only tool that enables vision models to output mobile GUI interaction instructions.
The tool defines actions (tap, swipe, long_press, etc.) but does not execute them.
It's designed for GUI grounding with vision-language models like Qwen3-VL.
"""

from typing import Any, Literal, Optional

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class MobileUseInput(BaseModel):
    """Input schema for Mobile Use tool.

    Defines all available mobile GUI interaction actions and their parameters.
    Coordinates are normalized to 0-1000 range for display_width/height.
    """

    action: Literal[
        "click",
        "long_press",
        "swipe",
        "type",
        "key",
        "system_button",
        "open",
        "wait",
        "terminate",
    ] = Field(
        description="""The action to perform. The available actions are:
* `click`: Click/tap the point on the screen with coordinate (x, y).
* `long_press`: Press the point on the screen with coordinate (x, y) for specified seconds.
* `swipe`: Swipe from the starting point with coordinate (x, y) to the end point with coordinate2 (x2, y2).
* `type`: Input the specified text into the activated input box.
* `key`: Perform a key event on the mobile device (e.g., volume_up, volume_down, power, camera, clear).
* `system_button`: Press the system button (Back, Home, Menu, Enter).
* `open`: Open an app on the device by name.
* `wait`: Wait specified seconds for the change to happen.
* `terminate`: Terminate the current task and report its completion status."""
    )

    coordinate: Optional[list[int]] = Field(
        default=None,
        description="(x, y): The x (pixels from the left edge) and y (pixels from the top edge) coordinates. Required only by `action=click`, `action=long_press`, and `action=swipe`.",
    )

    coordinate2: Optional[list[int]] = Field(
        default=None,
        description="(x, y): The end coordinates for swipe gesture. Required only by `action=swipe`.",
    )

    text: Optional[str] = Field(
        default=None,
        description="Required only by `action=key`, `action=type`, and `action=open`.",
    )

    time: Optional[float] = Field(
        default=None,
        description="The seconds to wait. Required only by `action=long_press` and `action=wait`.",
    )

    button: Optional[Literal["Back", "Home", "Menu", "Enter"]] = Field(
        default=None,
        description="Back means returning to the previous interface, Home means returning to the desktop, Menu means opening the application background menu, and Enter means pressing enter. Required only by `action=system_button`.",
    )

    status: Optional[Literal["success", "failure"]] = Field(
        default=None,
        description="The status of the task. Required only by `action=terminate`.",
    )


class MobileUseTool(BaseTool):
    """Tool for mobile GUI interaction instructions with vision models.

    This is a schema-only tool that outputs structured mobile GUI interaction instructions.
    It does NOT execute actions - it returns what action should be taken.

    Designed for use with vision-language models (Qwen3-VL, GPT-4V, etc.) that can
    analyze screenshots and determine where/how to interact with the mobile GUI.

    Example:
        ```python
        from lookit import MobileUseTool
        from langchain_openai import ChatOpenAI

        tool = MobileUseTool(display_width=1000, display_height=1000)
        model = ChatOpenAI(model="qwen3-vl").bind_tools([tool])

        # Model analyzes screenshot and returns tool call with coordinates
        response = model.invoke([
            HumanMessage(content=[
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img}"}},
                {"type": "text", "text": "Tap the login button"}
            ])
        ])
        ```

    Attributes:
        display_width: Virtual display width for coordinate normalization (default: 1000)
        display_height: Virtual display height for coordinate normalization (default: 1000)
    """

    name: str = "mobile_use"
    description: str = ""  # Set dynamically in __init__
    args_schema: type[BaseModel] = MobileUseInput

    # Display dimensions for coordinate normalization
    display_width: int = 1000
    display_height: int = 1000

    def __init__(
        self,
        display_width: int = 1000,
        display_height: int = 1000,
        **kwargs: Any,
    ) -> None:
        """Initialize MobileUseTool with display dimensions.

        Args:
            display_width: Virtual display width for coordinate normalization.
            display_height: Virtual display height for coordinate normalization.
            **kwargs: Additional arguments passed to BaseTool.
        """
        super().__init__(**kwargs)
        self.display_width = display_width
        self.display_height = display_height
        # Set description dynamically with display dimensions
        self.description = self._build_description()

    def _build_description(self) -> str:
        """Build tool description with current display dimensions."""
        return f"""Use a touchscreen to interact with a mobile device, and take screenshots.
* This is an interface to a mobile device with touchscreen. You can perform actions like clicking, typing, swiping, etc.
* Some applications may take time to start or process actions, so you may need to wait and take successive screenshots to see the results of your actions.
* The screen's resolution is {self.display_width}x{self.display_height}.
* Make sure to click any buttons, links, icons, etc with the cursor tip in the center of the element. Don't click boxes on their edges unless asked."""

    def _run(
        self,
        action: str,
        coordinate: Optional[list[int]] = None,
        coordinate2: Optional[list[int]] = None,
        text: Optional[str] = None,
        time: Optional[float] = None,
        button: Optional[str] = None,
        status: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> dict[str, Any]:
        """Return structured instruction for the requested action.

        This method does NOT execute the action - it returns what should be done.

        Args:
            action: The action to perform.
            coordinate: (x, y) coordinate for tap/swipe actions.
            coordinate2: (x, y) end coordinate for swipe action.
            text: Text for typing, key events, or app name.
            time: Duration for long_press or wait.
            button: System button to press.
            status: Task completion status.
            run_manager: Callback manager (unused).

        Returns:
            Dict containing the action instruction with all relevant parameters.
        """
        instruction: dict[str, Any] = {
            "action": action,
            "display_width": self.display_width,
            "display_height": self.display_height,
        }

        # Add action-specific parameters
        if action == "click":
            if coordinate is None:
                return {"error": "coordinate is required for click action"}
            instruction["coordinate"] = coordinate

        elif action == "long_press":
            if coordinate is None:
                return {"error": "coordinate is required for long_press action"}
            if time is None:
                return {"error": "time is required for long_press action"}
            instruction["coordinate"] = coordinate
            instruction["time"] = time

        elif action == "swipe":
            if coordinate is None:
                return {"error": "coordinate is required for swipe action"}
            if coordinate2 is None:
                return {"error": "coordinate2 is required for swipe action"}
            instruction["coordinate"] = coordinate
            instruction["coordinate2"] = coordinate2

        elif action == "type":
            if text is None:
                return {"error": "text is required for type action"}
            instruction["text"] = text

        elif action == "key":
            if text is None:
                return {"error": "text (key name) is required for key action"}
            instruction["text"] = text

        elif action == "system_button":
            if button is None:
                return {"error": "button is required for system_button action"}
            instruction["button"] = button

        elif action == "open":
            if text is None:
                return {"error": "text (app name) is required for open action"}
            instruction["text"] = text

        elif action == "wait":
            if time is None:
                return {"error": "time is required for wait action"}
            instruction["time"] = time

        elif action == "terminate":
            if status is None:
                return {"error": "status is required for terminate action"}
            instruction["status"] = status

        return instruction

    async def _arun(
        self,
        action: str,
        coordinate: Optional[list[int]] = None,
        coordinate2: Optional[list[int]] = None,
        text: Optional[str] = None,
        time: Optional[float] = None,
        button: Optional[str] = None,
        status: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> dict[str, Any]:
        """Async version of _run. Returns same structured instruction."""
        return self._run(
            action=action,
            coordinate=coordinate,
            coordinate2=coordinate2,
            text=text,
            time=time,
            button=button,
            status=status,
            run_manager=run_manager,
        )

    def convert_coordinates(
        self,
        normalized_coord: list[int],
        actual_width: int,
        actual_height: int,
    ) -> list[int]:
        """Convert normalized coordinates to actual screen coordinates.

        Useful when the model outputs coordinates normalized to display_width/height
        but you need to map them to actual screen dimensions.

        Args:
            normalized_coord: [x, y] in normalized display coordinates.
            actual_width: Actual screen width in pixels.
            actual_height: Actual screen height in pixels.

        Returns:
            [x, y] in actual screen coordinates.
        """
        return [
            int(normalized_coord[0] / self.display_width * actual_width),
            int(normalized_coord[1] / self.display_height * actual_height),
        ]
