"""Computer Use Tool for LangChain.

A schema-only tool that enables vision models to output GUI interaction instructions.
The tool defines actions (click, type, scroll, etc.) but does not execute them.
It's designed for GUI grounding with vision-language models like Qwen3-VL.
"""

from typing import Any, Literal, Optional

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class ComputerUseInput(BaseModel):
    """Input schema for Computer Use tool.

    Defines all available GUI interaction actions and their parameters.
    Coordinates are normalized to 0-1000 range for display_width/height.
    """

    action: Literal[
        "key",
        "type",
        "mouse_move",
        "left_click",
        "left_click_drag",
        "right_click",
        "middle_click",
        "double_click",
        "triple_click",
        "scroll",
        "hscroll",
        "wait",
        "terminate",
        "answer",
    ] = Field(
        description="""The action to perform. The available actions are:
* `key`: Performs key down presses on the arguments passed in order, then performs key releases in reverse order.
* `type`: Type a string of text on the keyboard.
* `mouse_move`: Move the cursor to a specified (x, y) pixel coordinate on the screen.
* `left_click`: Click the left mouse button at a specified (x, y) pixel coordinate on the screen.
* `left_click_drag`: Click and drag the cursor to a specified (x, y) pixel coordinate on the screen.
* `right_click`: Click the right mouse button at a specified (x, y) pixel coordinate on the screen.
* `middle_click`: Click the middle mouse button at a specified (x, y) pixel coordinate on the screen.
* `double_click`: Double-click the left mouse button at a specified (x, y) pixel coordinate on the screen.
* `triple_click`: Triple-click the left mouse button at a specified (x, y) pixel coordinate on the screen.
* `scroll`: Performs a scroll of the mouse scroll wheel.
* `hscroll`: Performs a horizontal scroll.
* `wait`: Wait specified seconds for the change to happen.
* `terminate`: Terminate the current task and report its completion status.
* `answer`: Answer a question."""
    )

    coordinate: Optional[list[int]] = Field(
        default=None,
        description="(x, y): The x (pixels from the left edge) and y (pixels from the top edge) coordinates. Required for click/move/drag actions.",
    )

    keys: Optional[list[str]] = Field(
        default=None,
        description="Keys to press. Required only by `action=key`. Examples: ['Return'], ['Control', 'c']",
    )

    text: Optional[str] = Field(
        default=None,
        description="Required only by `action=type` and `action=answer`.",
    )

    pixels: Optional[int] = Field(
        default=None,
        description="The amount of scrolling to perform. Positive values scroll up, negative values scroll down. Required only by `action=scroll` and `action=hscroll`.",
    )

    time: Optional[float] = Field(
        default=None,
        description="The seconds to wait. Required only by `action=wait`.",
    )

    status: Optional[Literal["success", "failure"]] = Field(
        default=None,
        description="The status of the task. Required only by `action=terminate`.",
    )


class ComputerUseTool(BaseTool):
    """Tool for GUI interaction instructions with vision models.

    This is a schema-only tool that outputs structured GUI interaction instructions.
    It does NOT execute actions - it returns what action should be taken.

    Designed for use with vision-language models (Qwen3-VL, GPT-4V, etc.) that can
    analyze screenshots and determine where/how to interact with the GUI.

    Example:
        ```python
        from lookit import ComputerUseTool
        from langchain_openai import ChatOpenAI

        tool = ComputerUseTool(display_width=1000, display_height=1000)
        model = ChatOpenAI(model="qwen3-vl").bind_tools([tool])

        # Model analyzes screenshot and returns tool call with coordinates
        response = model.invoke([
            HumanMessage(content=[
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img}"}},
                {"type": "text", "text": "Click the submit button"}
            ])
        ])
        ```

    Attributes:
        display_width: Virtual display width for coordinate normalization (default: 1000)
        display_height: Virtual display height for coordinate normalization (default: 1000)
    """

    name: str = "computer_use"
    description: str = ""  # Set dynamically in __init__
    args_schema: type[BaseModel] = ComputerUseInput

    # Display dimensions for coordinate normalization
    display_width: int = 1000
    display_height: int = 1000

    def __init__(
        self,
        display_width: int = 1000,
        display_height: int = 1000,
        **kwargs: Any,
    ) -> None:
        """Initialize ComputerUseTool with display dimensions.

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
        return f"""Use a mouse and keyboard to interact with a computer, and take screenshots.
* This is an interface to a desktop GUI. You do not have access to a terminal or applications menu. You must click on desktop icons to start applications.
* Some applications may take time to start or process actions, so you may need to wait and take successive screenshots to see the results of your actions.
* The screen's resolution is {self.display_width}x{self.display_height}.
* Whenever you intend to move the cursor to click on an element like an icon, you should consult a screenshot to determine the coordinates of the element before moving the cursor.
* Make sure to click any buttons, links, icons, etc with the cursor tip in the center of the element. Don't click boxes on their edges."""

    def _run(
        self,
        action: str,
        coordinate: Optional[list[int]] = None,
        keys: Optional[list[str]] = None,
        text: Optional[str] = None,
        pixels: Optional[int] = None,
        time: Optional[float] = None,
        status: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> dict[str, Any]:
        """Return structured instruction for the requested action.

        This method does NOT execute the action - it returns what should be done.

        Args:
            action: The action to perform.
            coordinate: (x, y) coordinate for click/move actions.
            keys: Keys to press.
            text: Text for typing or answering.
            pixels: Scroll amount.
            time: Wait duration.
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
        if action in [
            "left_click",
            "right_click",
            "middle_click",
            "double_click",
            "triple_click",
            "mouse_move",
            "left_click_drag",
        ]:
            if coordinate is None:
                return {"error": f"coordinate is required for {action}"}
            instruction["coordinate"] = coordinate

        elif action == "type":
            if text is None:
                return {"error": "text is required for type action"}
            instruction["text"] = text

        elif action == "key":
            if keys is None:
                return {"error": "keys is required for key action"}
            instruction["keys"] = keys

        elif action in ["scroll", "hscroll"]:
            if pixels is None:
                return {"error": f"pixels is required for {action} action"}
            instruction["pixels"] = pixels
            instruction["direction"] = "up" if pixels > 0 else "down"
            if action == "hscroll":
                instruction["direction"] = "right" if pixels > 0 else "left"

        elif action == "wait":
            if time is None:
                return {"error": "time is required for wait action"}
            instruction["time"] = time

        elif action == "terminate":
            if status is None:
                return {"error": "status is required for terminate action"}
            instruction["status"] = status

        elif action == "answer":
            if text is None:
                return {"error": "text is required for answer action"}
            instruction["text"] = text

        return instruction

    async def _arun(
        self,
        action: str,
        coordinate: Optional[list[int]] = None,
        keys: Optional[list[str]] = None,
        text: Optional[str] = None,
        pixels: Optional[int] = None,
        time: Optional[float] = None,
        status: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> dict[str, Any]:
        """Async version of _run. Returns same structured instruction."""
        return self._run(
            action=action,
            coordinate=coordinate,
            keys=keys,
            text=text,
            pixels=pixels,
            time=time,
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
