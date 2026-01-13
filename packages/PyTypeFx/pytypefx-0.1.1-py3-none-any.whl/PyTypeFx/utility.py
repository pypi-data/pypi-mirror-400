import os
import random
import sys
import time

from PyTypeFx.colors import PALETTES
from PyTypeFx.constant import HEX_RANDOM, RESET, RGB_COLORS


# Colors convorting funcations
def hex_to_ansi(hex_color: str) -> str:
    """
    Converts a HEX color string to an ANSI escape code for foreground text.

    Function Name: hex_to_ansi

    Args:
        hex_color (str): The HEX color string (e.g., "#RRGGBB" or "RRGGBB").

    Returns:
        str: The ANSI escape code for the given HEX color.

    Examples:
        >>> hex_to_ansi("#FFFFFF")
        '\033[38;2;255;255;255m'
    """
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return f"\033[38;2;{r};{g};{b}m"


def rgb_to_ansi(r: int, g: int, b: int) -> str:
    """
    Converts RGB color values to an ANSI escape code for foreground text.

    Function Name: rgb_to_ansi

    Args:
        r (int): The red component (0-255).
        g (int): The green component (0-255).
        b (int): The blue component (0-255).

    Returns:
        str: The ANSI escape code for the given RGB color.

    Examples:
        >>> rgb_to_ansi(255, 255, 255)
        '\033[38;2;255;255;255m'
    """
    return f"\033[38;2;{r};{g};{b}m"


def supports_ansi() -> bool:
    """
    Checks if the current terminal supports ANSI escape codes.

    Function Name: supports_ansi

    Args:
        None

    Returns:
        bool: True if ANSI is supported, False otherwise.

    Examples:
        >>> supports_ansi()
        True  # Or False, depending on the terminal environment.
    """
    if sys.platform.startswith("win"):
        return "WT_SESSION" in os.environ or sys.stdout.isatty()
    return sys.stdout.isatty()


def write(char: str) -> None:
    """
    Writes a character to stdout and flushes the buffer.

    Function Name: write

    Args:
        char (str): The character or string to write.

    Returns:
        None

    Examples:
        >>> write("H")
        >>> write("i")
    """
    sys.stdout.write(char)
    sys.stdout.flush()


def _make_delay(base_delay: float, speed: str):
    """
    Creates a function that returns a calculated delay for typing.

    The delay can be adjusted based on a speed setting ("fast", "slow", "random", etc.).
    This is an internal helper function.

    Function Name: _make_delay

    Args:
        base_delay (float): The base delay value.
        speed (str): The speed modifier ('fast', 'slow', 'random', 'none', 'normal').

    Returns:
        function: A function that takes a character and returns a calculated delay.

    Examples:
        >>> delay_fn = _make_delay(0.1, "fast")
        >>> delay_fn('a')  # doctest: +SKIP
        0.05...
    """
    base: float = float(base_delay)
    speed = (speed or "normal").lower()
    if speed == "fast":
        factor = 0.5
        return lambda c: max(0, base * factor + random.uniform(0, base * 0.06))
    elif speed == "slow":
        factor = 1.8
        return lambda c: base * factor + random.uniform(0, base * 0.06)
    elif speed == "random":
        return lambda c: base + random.uniform(0.3, 1.8)
    elif speed == "none":
        return lambda c: 0
    return lambda c: base + random.uniform(0, base * 0.06)


def _make_color(hex_colors):
    """
    Creates a function that returns an ANSI color code for a character.

    This factory function handles various color inputs: single hex, list of hex, 
    or predefined palette names like "rainbow" and "random". This is an internal
    helper function.

    Function Name: _make_color

    Args:
        hex_colors (str or list or tuple): The color definition.

    Returns:
        function or None: A function that takes a character and its index and 
                          returns an ANSI color code, or None if no color is specified.

    Examples:
        >>> color_fn = _make_color("#FF0000")
        >>> color_fn('a', 0)
        '\033[38;2;255;0;0m'
        >>> rainbow_fn = _make_color("rainbow")
        >>> rainbow_fn('b', 1)
        '\033[38;2;255;165;0m'
    """
    if not hex_colors:
        return None

    if isinstance(hex_colors, str):
        key = hex_colors.upper()
        if key in PALETTES:
            palette = PALETTES[key]
            ansi_list = [hex_to_ansi(h) for h in palette]
            return lambda c, i: ansi_list[i % len(ansi_list)]

        if hex_colors.lower() == "rainbow":
            ansi_list = [f"\033[38;2;{r};{g};{b}m" for r, g, b in RGB_COLORS]
            return lambda c, i: ansi_list[i % len(ansi_list)]
        if hex_colors.lower() == "random":
            return lambda c, i: hex_to_ansi(random.choice(HEX_RANDOM))

        try:
            ansi = hex_to_ansi(hex_colors)
            return lambda c, i: ansi
        except Exception:
            return None

    if isinstance(hex_colors, (list, tuple)) and hex_colors:
        ansi_list = [hex_to_ansi(h) for h in hex_colors]
        return lambda c, i: ansi_list[i % len(ansi_list)]

    return None


def _type_out_text(text: str, delay_fn, color_fn=None):
    """
    Types out text character by character with specified delay and color.

    This is an internal helper function that performs the core typewriter animation.

    Function Name: _type_out_text

    Args:
        text (str): The text to type out.
        delay_fn (function): A function that returns the delay for each character.
        color_fn (function, optional): A function that returns the ANSI color 
            for each character. Defaults to None.

    Returns:
        None

    Examples:
        >>> delay_fn = lambda c: 0.01
        >>> color_fn = lambda c, i: '\033[31m'
        >>> _type_out_text("Hi", delay_fn, color_fn)
    """
    for i, ch in enumerate(text):
        if color_fn:
            ansi = color_fn(ch, i)
            sys.stdout.write(f"{ansi}{ch}{RESET}")
        else:
            sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay_fn(ch))
    if not text.endswith("\n"):
        sys.stdout.write("\n")
    sys.stdout.flush()


def _hex_to_rgb(hex_color: str):
    """
    Converts a HEX color string to an RGB tuple.

    This is an internal helper function.

    Function Name: _hex_to_rgb

    Args:
        hex_color (str): The HEX color string (e.g., "#RRGGBB").

    Returns:
        tuple: An (R, G, B) tuple of integers.

    Examples:
        >>> _hex_to_rgb("#FF0000")
        (255, 0, 0)
    """
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def gradient(text: str, start_hex: str, end_hex: str):
    """
    Applies a color gradient to a string of text.

    Each character in the text is colored with an interpolated color between the
    start and end HEX values.

    Function Name: gradient

    Args:
        text (str): The text to apply the gradient to.
        start_hex (str): The starting HEX color.
        end_hex (str): The ending HEX color.

    Returns:
        str: The text with ANSI color codes applied for the gradient effect.

    Examples:
        >>> gradient("Hello", "#FF0000", "#0000FF") # doctest: +ELLIPSIS
        '\033[38;2;255;0;0mH...'
    """

    def hex_to_rgb(h):
        h = h.lstrip("#")
        return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))

    def rgb_to_ansi(r, g, b):
        return f"\033[38;2;{r};{g};{b}m"

    if not text:
        return text

    start_r, start_g, start_b = hex_to_rgb(start_hex)
    end_r, end_g, end_b = hex_to_rgb(end_hex)
    length = len(text) - 1 if len(text) > 1 else 1
    result = ""

    for i, char in enumerate(text):
        ratio = i / length
        r = int(start_r + (end_r - start_r) * ratio)
        g = int(start_g + (end_g - start_g) * ratio)
        b = int(start_b + (end_b - start_b) * ratio)
        result += f"{rgb_to_ansi(r, g, b)}{char}"
    return result + RESET
