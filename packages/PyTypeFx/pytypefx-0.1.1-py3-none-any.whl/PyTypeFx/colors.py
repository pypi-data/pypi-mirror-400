"""\nReusable color palette for TypeFx.

Supports:
    - Foreground colors
    - Background colors
    - Bright colors
    - HEX / RGB colors
    - Reset/Formatting color
    - Hex color conversion
    - Extended named colors

Designed to integrate with TypeFx's text writing functions.
"""

# Reset / Formatting Colors
RESET = "\033[0m"
BOLD = "\033[1m"
BIM = "\033[2m"
UNDERLINE = "\033[4m"
INVERT = "\033[7m"
ITALIC = "\033[3m"
BLINK = "\033[5m"
REVERSE = "\033[7m"
BLINK_FAST = "\033[6m"
BLINK_SLOW = "\033[25m"
BRIGHT = "\033[1m"
BRIGHT_FOREGROUND = "\033[9m"
BRIGHT_BACKGROUND = "\033[10m"
BRIGHT_HEX = "\033[10m"

# Foreground Colors (Basic)
BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
GRAY = "\033[90m"

# Foreground Colors (Bright)
BRIGHT_BLACK = "\033[90m"
BRIGHT_RED = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN = "\033[96m"
BRIGHT_WHITE = "\033[97m"

# Background Colors (Basic)
BG_BLACK = "\033[40m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"
BG_MAGENTA = "\033[45m"
BG_CYAN = "\033[46m"
BG_WHITE = "\033[47m"
BG_GRAY = "\033[100m"

# Background Colors (Bright)
BG_BRIGHT_BLACK = "\033[100m"
BG_BRIGHT_RED = "\033[101m"
BG_BRIGHT_GREEN = "\033[102m"
BG_BRIGHT_YELLOW = "\033[103m"
BG_BRIGHT_BLUE = "\033[104m"
BG_BRIGHT_MAGENTA = "\033[105m"
BG_BRIGHT_CYAN = "\033[106m"
BG_BRIGHT_WHITE = "\033[107m"

# Extended Named Foreground Colors
ORANGE = "\033[38;2;255;165;0m"
PURPLE = "\033[38;2;128;0;128m"
PINK = "\033[38;2;255;105;180m"
TEAL = "\033[38;2;0;128;128m"
VIOLET = "\033[38;2;148;0;211m"
TURQUOISE = "\033[38;2;64;224;208m"
LIME = "\033[38;2;50;205;50m"
GOLD = "\033[38;2;255;215;0m"
SILVER = "\033[38;2;192;192;192m"
MARRON = "\033[38;2;128;0;0m"
NAVY = "\033[38;2;0;0;128m"
OLIVE = "\033[38;2;128;128;0m"
CORAL = "\033[38;2;255;127;80m"
SKYBLUE = "\033[38;2;135;206;235m"
AQUA = "\033[38;2;0;255;255m"
INDIGO = "\033[38;2;75;0;130m"
BROWN = "\033[38;2;139;69;19m"

# Extended Named Background Colors
BG_ORANGE = "\033[48;2;255;165;0m"
BG_PURPLE = "\033[48;2;128;0;128m"
BG_PINK = "\033[48;2;255;105;180m"
BG_TEAL = "\033[48;2;0;128;128m"
BG_VIOLET = "\033[48;2;148;0;211m"
BG_TURQUOISE = "\033[48;2;64;224;208m"
BG_LIME = "\033[48;2;50;205;50m"
BG_GOLD = "\033[48;2;255;215;0m"
BG_SILVER = "\033[48;2;192;192;192m"
BG_MARRON = "\033[48;2;128;0;0m"
BG_NAVY = "\033[48;2;0;0;128m"
BG_OLIVE = "\033[48;2;128;128;0m"
BG_CORAL = "\033[48;2;255;127;80m"
BG_SKYBLUE = "\033[48;2;135;206;235m"
BG_AQUA = "\033[48;2;0;255;255m"
BG_INDIGO = "\033[48;2;75;0;130m"
BG_BROWN = "\033[48;2;139;69;19m"

# Gradient Colors
LEAF_GREEN = "\033[38;2;34;139;34m"  # Forest green
GRASS_GREEN = "\033[38;2;124;252;0m"  # Lawn green
MOSS_GREEN = "\033[38;2;85;107;47m"  # Moss green
FERN_GREEN = "\033[38;2;79;121;66m"  # Fern green

SOIL_BROWN = "\033[38;2;101;67;33m"
BARK_BROWN = "\033[38;2;139;69;19m"
CLAY_BROWN = "\033[38;2;150;75;0m"

SUNFLOWER = "\033[38;2;255;215;0m"
ROSE_PINK = "\033[38;2;255;99;132m"
LAVENDER = "\033[38;2;181;126;220m"
PETAL_RED = "\033[38;2;220;20;60m"

SKY_BLUE = "\033[38;2;135;206;235m"
CLOUD_WHITE = "\033[38;2;245;245;245m"
RAIN_GRAY = "\033[38;2;176;196;222m"

# =========================
# Preset Palettes
# =========================
PALETTES = {
    "SUCCESS": ["#2ECC71", "#27AE60", "#1E8449"],
    "ERROR": ["#E74C3C", "#C0392B", "#922B21"],
    "WARNING": ["#F1C40F", "#F39C12", "#D68910"],
    "INFO": ["#3498DB", "#2980B9", "#1F618D"],
    "NEON": ["#39FF14", "#FF00FF", "#00FFFF", "#FFFF00"],
    "PASTEL": ["#FFB6C1", "#B0E0E6", "#98FB98", "#E6E6FA"],
    # 🌿 Garden Theme
    "GARDEN": [
        "#228B22",  # Leaf Green
        "#7CFC00",  # Grass
        "#FFDB58",  # Sunflower
        "#FF6384",  # Rose
        "#87CEEB",  # Sky
        "#654321",  # Soil
        "#B57EDC",  # Lavender
    ],
}


# HEX & RGB Helpers
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
        '\\033[38;2;255;255;255m'
        >>> hex_to_ansi("000000")
        '\\033[38;2;0;0;0m'
    """
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return f"\033[38;2;{r};{g};{b}m"


def bg_hex_to_ansi(hex_color: str) -> str:
    """
    Converts a HEX color string to an ANSI escape code for background color.

    Function Name: bg_hex_to_ansi

    Args:
        hex_color (str): The HEX color string (e.g., "#RRGGBB" or "RRGGBB").

    Returns:
        str: The ANSI escape code for the given background HEX color.

    Examples:
        >>> bg_hex_to_ansi("#000000")
        '\\033[48;2;0;0;0m'
        >>> bg_hex_to_ansi("FFFFFF")
        '\\033[48;2;255;255;255m'
    """
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return f"\033[48;2;{r};{g};{b}m"


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
        '\\033[38;2;255;255;255m'
        >>> rgb_to_ansi(0, 0, 0)
        '\\033[38;2;0;0;0m'
    """
    return f"\033[38;2;{r};{g};{b}m"

def bg_rgb_to_ansi(r: int, g: int, b: int) -> str:
    """
    Converts RGB color values to an ANSI escape code for background color.

    Function Name: bg_rgb_to_ansi

    Args:
        r (int): The red component (0-255).
        g (int): The green component (0-255).
        b (int): The blue component (0-255).

    Returns:
        str: The ANSI escape code for the given background RGB color.

    Examples:
        >>> bg_rgb_to_ansi(0, 0, 0)
        '\\033[48;2;0;0;0m'
        >>> bg__to_ansi(255, 255, 255)
        '\\033[48;2;255;255;255m'
    """
    return f"\033[48;2;{r};{g};{b}m"


# Utility Combiners
def colorize(text: str, *style: str) -> str:
    """
    Applies one or more ANSI styles to a text string.

    Function Name: colorize

    Args:
        text (str): The text to be styled.
        *style (str): A variable number of ANSI style codes to apply.

    Returns:
        str: The styled text string, with a reset code at the end.

    Examples:
        >>> from TypeFx.colors import RED, BOLD
        >>> colorize("Hello", RED)
        '\\033[31mHello\\033[0m'
        >>> colorize("World", RED, BOLD)
        '\\033[31m\\033[1mWorld\\033[0m'
    """
    return "".join(style) + text + RESET