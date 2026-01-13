#!/usr/bin/env python3
"""Lookit CLI - Vision-based GUI automation for LLM agents.

This CLI analyzes screenshots using vision models and outputs
minimal plain text responses optimized for LLM consumption.

Setup:
    export LOOKIT_API_KEY="your-api-key"
    export LOOKIT_MODEL="your-model-name"
    export LOOKIT_BASE_URL="https://your-api-endpoint/v1"

Usage:
    lookit "click the submit button" -s screenshot.png --mode computer
    lookit "tap the login button" -s mobile.png --mode mobile
    lookit "read all text" -s screenshot.png --mode ocr

Debug mode:
    lookit "click submit" -s screenshot.png --mode computer --debug

Output format (action modes):
    left_click 960,324
    type "hello world"
    swipe 500,800 to 500,200

Output format (ocr mode):
    [extracted text content]

Output format (errors):
    error: message describing the issue
"""

import argparse
import hashlib
import os
import sys
import tempfile
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from lookit import ComputerUseTool, MobileUseTool
from lookit.utils import (
    create_image_message,
    draw_point,
    get_image_dimensions,
    load_image,
)


def debug_log(message: str) -> None:
    """Print debug message to stderr."""
    print(f"[debug] {message}", file=sys.stderr)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="lookit",
        description="Vision-based GUI automation for LLM agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    lookit "click the submit button" -s screenshot.png --mode computer
    lookit "tap the login button" -s mobile.png --mode mobile
    lookit "read all text" -s screenshot.png --mode ocr

Debug mode:
    lookit "click submit" -s img.png --mode computer --debug

Environment Variables:
    LOOKIT_API_KEY   API key (required)
    LOOKIT_MODEL     Model name (required)
    LOOKIT_BASE_URL  API base URL (required)
        """,
    )
    parser.add_argument(
        "query",
        type=str,
        help="Natural language instruction",
    )
    parser.add_argument(
        "-s",
        "--screenshot",
        type=str,
        required=True,
        help="Path to screenshot image",
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        choices=["computer", "mobile", "ocr"],
        required=True,
        help="Mode: computer, mobile, or ocr",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=os.getenv("LOOKIT_MODEL"),
        help="Model name (env: LOOKIT_MODEL)",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default=os.getenv("LOOKIT_BASE_URL"),
        help="API base URL (env: LOOKIT_BASE_URL)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Debug mode: print info to stderr, save annotated image (action modes only)",
    )
    return parser.parse_args()


def format_action_output(tool_call: dict, tool: ComputerUseTool | MobileUseTool,
                         image_width: int, image_height: int) -> str:
    """Format a tool call as minimal plain text."""
    args = tool_call["args"]
    action = args.get("action", "unknown")
    parts = [action]

    # Handle coordinates
    if "coordinate" in args:
        coord = tool.convert_coordinates(args["coordinate"], image_width, image_height)
        parts.append(f"{coord[0]},{coord[1]}")

    # Handle second coordinate (for swipe/drag)
    if "coordinate2" in args:
        coord2 = tool.convert_coordinates(args["coordinate2"], image_width, image_height)
        parts.append(f"to {coord2[0]},{coord2[1]}")

    # Handle text
    if "text" in args:
        parts.append(f'"{args["text"]}"')

    # Handle keys
    if "keys" in args:
        parts.append("+".join(args["keys"]))

    # Handle scroll
    if "pixels" in args:
        parts.append(str(args["pixels"]))

    # Handle wait
    if "time" in args:
        parts.append(f"{args['time']}s")

    # Handle system button
    if "button" in args:
        parts.append(args["button"])

    return " ".join(parts)


def run_action_mode(
    args: argparse.Namespace,
    model: ChatOpenAI,
    image_width: int,
    image_height: int,
) -> None:
    """Run action mode - GUI interactions with tool binding."""
    debug = args.debug

    if debug:
        debug_log(f"mode: {args.mode}")
        debug_log(f"image: {image_width}x{image_height}")
        debug_log(f"model: {args.model}")
        debug_log(f"query: {args.query}")

    display_width = 1000
    display_height = 1000

    # Select tool based on mode
    if args.mode == "mobile":
        tool = MobileUseTool(
            display_width=display_width,
            display_height=display_height,
        )
    else:
        tool = ComputerUseTool(
            display_width=display_width,
            display_height=display_height,
        )

    model_with_tools = model.bind_tools([tool])
    content = create_image_message(args.screenshot, args.query)
    message = HumanMessage(content=content)

    try:
        response = model_with_tools.invoke([message])
    except Exception as e:
        print(f"error: {e}")
        sys.exit(1)

    if debug:
        debug_log(f"tool_calls: {len(response.tool_calls) if response.tool_calls else 0}")

    if not response.tool_calls:
        if debug and response.content:
            debug_log(f"raw_response: {response.content}")
        print("error: no action detected")
        sys.exit(1)

    # Output each action on its own line
    outputs = []
    for tool_call in response.tool_calls:
        output = format_action_output(tool_call, tool, image_width, image_height)
        outputs.append(output)

        if debug:
            debug_log(f"raw_args: {tool_call['args']}")

            # Save annotated image in debug mode
            if "coordinate" in tool_call["args"]:
                coord = tool.convert_coordinates(
                    tool_call["args"]["coordinate"], image_width, image_height
                )
                input_image = load_image(args.screenshot)
                result_image = draw_point(input_image, coord, color="green")

                # Generate unique filename in temp folder
                hash_input = f"{args.screenshot}{args.query}{coord}"
                file_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
                debug_path = Path(tempfile.gettempdir()) / f"lookit_{file_hash}.png"
                result_image.save(debug_path)
                debug_log(f"saved: {debug_path}")

    print("\n".join(outputs))


def run_ocr_mode(args: argparse.Namespace, model: ChatOpenAI,
                 image_width: int, image_height: int) -> None:
    """Run OCR mode - text extraction."""
    debug = args.debug

    if debug:
        debug_log(f"mode: ocr")
        debug_log(f"image: {image_width}x{image_height}")
        debug_log(f"model: {args.model}")
        debug_log(f"query: {args.query}")

    ocr_prompt = f"{args.query}\n\nExtract and return only the text content from the image."

    content = create_image_message(args.screenshot, ocr_prompt)
    message = HumanMessage(content=content)

    try:
        response = model.invoke([message])
    except Exception as e:
        print(f"error: {e}")
        sys.exit(1)

    if debug:
        debug_log(f"response_length: {len(response.content)} chars")

    print(response.content)


def main() -> None:
    """Run the lookit CLI."""
    args = parse_args()
    debug = args.debug

    model_name = args.model
    base_url = args.base_url
    api_key = os.getenv("LOOKIT_API_KEY")

    # Check required configuration
    missing = []
    if not api_key:
        missing.append("LOOKIT_API_KEY")
    if not model_name:
        missing.append("LOOKIT_MODEL")
    if not base_url:
        missing.append("LOOKIT_BASE_URL")

    if missing:
        print(f"error: missing environment variables: {', '.join(missing)}")
        sys.exit(1)

    if not Path(args.screenshot).exists():
        print(f"error: file not found: {args.screenshot}")
        sys.exit(1)

    image_width, image_height = get_image_dimensions(args.screenshot)

    if debug:
        debug_log(f"screenshot: {args.screenshot}")
        debug_log(f"base_url: {base_url}")

    model = ChatOpenAI(
        model=model_name,
        base_url=base_url,
        api_key=api_key,
    )

    if args.mode in ["computer", "mobile"]:
        run_action_mode(args, model, image_width, image_height)
    else:
        run_ocr_mode(args, model, image_width, image_height)


if __name__ == "__main__":
    main()
