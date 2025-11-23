import base64
import io
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import adbutils
from mcp.server.fastmcp import FastMCP
from PIL import Image

# Initialize FastMCP server
mcp = FastMCP("scrcpy-mcp")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_device() -> adbutils.AdbDevice:
    """Get the first connected ADB device."""
    adb = adbutils.AdbClient(host="127.0.0.1", port=5037)
    devices = adb.device_list()
    if not devices:
        raise RuntimeError("No ADB devices connected")
    return devices[0]

@mcp.tool()
def get_screenshot() -> str:
    """
    Take a screenshot of the connected device and save it to ~/Downloads.
    Returns the path to the saved screenshot.
    """
    try:
        device = get_device()
        png_bytes = device.shell("screencap -p", encoding=None)

        if not png_bytes:
            raise RuntimeError("Failed to capture screenshot")

        # Save to Downloads folder
        downloads_dir = Path.home() / "Downloads"
        downloads_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = downloads_dir / filename

        with open(filepath, "wb") as f:
            f.write(png_bytes)

        return f"Screenshot saved to: {filepath}"
    except Exception as e:
        logger.error(f"Screenshot failed: {e}")
        raise RuntimeError(f"Screenshot failed: {str(e)}")

@mcp.tool()
def click(x: int, y: int) -> str:
    """
    Tap the screen at the specified coordinates.
    """
    try:
        device = get_device()
        device.shell(f"input tap {x} {y}")
        return f"Clicked at {x}, {y}"
    except Exception as e:
        return f"Error clicking: {str(e)}"

@mcp.tool()
def type_text(text: str) -> str:
    """
    Type the specified text.
    """
    try:
        device = get_device()
        # Escape spaces and special chars for shell
        escaped_text = text.replace(" ", "%s").replace("'", r"\'")
        device.shell(f"input text '{escaped_text}'")
        return f"Typed: {text}"
    except Exception as e:
        return f"Error typing: {str(e)}"

@mcp.tool()
def scroll(x1: int, y1: int, x2: int, y2: int, duration_ms: int = 500) -> str:
    """
    Perform a scroll (swipe) gesture from (x1, y1) to (x2, y2).
    """
    try:
        device = get_device()
        device.shell(f"input swipe {x1} {y1} {x2} {y2} {duration_ms}")
        return f"Scrolled from ({x1},{y1}) to ({x2},{y2})"
    except Exception as e:
        return f"Error scrolling: {str(e)}"

@mcp.tool()
def navigate(action: str) -> str:
    """
    Perform a navigation action.
    Allowed actions: 'home', 'back', 'menu', 'enter', 'delete'.
    """
    keycodes = {
        "home": "KEYCODE_HOME",
        "back": "KEYCODE_BACK",
        "menu": "KEYCODE_MENU",
        "enter": "KEYCODE_ENTER",
        "delete": "KEYCODE_DEL"
    }

    if action not in keycodes:
        return f"Invalid action. Allowed: {', '.join(keycodes.keys())}"

    try:
        device = get_device()
        device.shell(f"input keyevent {keycodes[action]}")
        return f"Performed navigation: {action}"
    except Exception as e:
        return f"Error navigating: {str(e)}"

if __name__ == "__main__":
    mcp.run()
