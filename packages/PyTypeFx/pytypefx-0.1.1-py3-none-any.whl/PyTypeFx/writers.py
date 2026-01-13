import itertools
import random
import re
import sys
import time

from PyTypeFx.constant import (
    DELAY,
    DOTS,
    END_HEX,
    FREQUENCY,
    GLITCH,
    HEX_COLORS,
    HOLD,
    LOOP,
    RESET,
    RGB_COLORS,
    SOUND_DURATION,
    START_HEX,
    TEXT,
)
from PyTypeFx.effects import SoundEffect
from PyTypeFx.utility import gradient, hex_to_ansi, rgb_to_ansi, write


# TypeWriter functions
def TypeWriter(text: str = TEXT, delay: float = DELAY, color: list = HEX_COLORS) -> int:
    """
    Simulates typing text with a specified delay and color cycling.

    Function Name: TypeWriter

    Args:
        text (str, optional): The text to be written. Defaults to TEXT.
        delay (float, optional): The delay between each character in seconds. Defaults to DELAY.
        color (list, optional): A list of HEX color strings to cycle through. Defaults to HEX_COLORS.

    Returns:
        int: The number of characters written.

    Examples:
        >>> TypeWriter("Hello, World!", delay=0.01, color=["#FF0000"])
        13
    """
    ansi_color = [hex_to_ansi(c) for c in color]
    color_cycle = itertools.cycle(ansi_color)

    for char in text:
        sys.stdout.write(f"{next(color_cycle)}{char}{RESET}")
        sys.stdout.flush()
        time.sleep(delay)
    print()
    return len(text)


def RainbowWriter(
    text: str = TEXT, delay: float = DELAY, colors: list = RGB_COLORS
) -> int:
    """
    Simulates typing text with a rainbow color effect.

    Function Name: RainbowWriter

    Args:
        text (str, optional): The text to be written. Defaults to TEXT.
        delay (float, optional): The delay between each character. Defaults to DELAY.
        colors (list, optional): A list of RGB tuples to cycle through. Defaults to RGB_COLORS.

    Returns:
        int: The number of characters written.

    Examples:
        >>> RainbowWriter("Rainbow", delay=0.01)
        7
    """
    color_cycle = itertools.cycle(colors)

    for char in text:
        r, g, b = next(color_cycle)
        sys.stdout.write(f"{rgb_to_ansi(r, g, b)}{char}{RESET}")
        sys.stdout.flush()
        time.sleep(delay)
    print()
    return len(text)


def HexWriter(text: str = TEXT, delay: float = DELAY, color: list = HEX_COLORS) -> int:
    """
    Simulates typing text using a list of HEX colors. (Similar to TypeWriter)

    Function Name: HexWriter

    Args:
        text (str, optional): The text to be written. Defaults to TEXT.
        delay (float, optional): The delay between each character. Defaults to DELAY.
        color (list, optional): A list of HEX color strings. Defaults to HEX_COLORS.

    Returns:
        int: The number of characters written.

    Examples:
        >>> HexWriter("Hex Power", delay=0.01, color=["#FFA500", "#FF4500"])
        9
    """
    ansi_color = [hex_to_ansi(c) for c in color]
    color_cycle = itertools.cycle(ansi_color)

    for char in text:
        sys.stdout.write(f"{next(color_cycle)}{char}{RESET}")
        sys.stdout.flush()
        time.sleep(delay)
    print()
    return len(text)


def DelWriter(
    text: str = TEXT, delay: float = DELAY, hold: int = HOLD, color: list = HEX_COLORS
) -> int:
    """
    Types out text, pauses, and then deletes it character by character.

    Function Name: DelWriter

    Args:
        text (str, optional): The text to write and delete. Defaults to TEXT.
        delay (float, optional): The delay for typing and deleting. Defaults to DELAY.
        hold (int, optional): The time in seconds to hold the text before deleting. Defaults to HOLD.
        color (list, optional): A list of HEX colors. Defaults to HEX_COLORS.

    Returns:
        int: The number of characters processed.

    Examples:
        >>> DelWriter("Temporary", delay=0.01, hold=0.5)
        9
    """
    ansi_color = [hex_to_ansi(c) for c in color]
    color_cycle = itertools.cycle(ansi_color)

    for char in text:
        write(f"{next(color_cycle)}{char}{RESET}")
        time.sleep(delay)
    time.sleep(hold)
    for _ in text:
        write(" ")
        time.sleep(delay)
    print()
    return len(text)


def LoopWriter(
    text: str = TEXT, loops: int = LOOP, delay: float = DELAY, color: list = HEX_COLORS
) -> int:
    """
    Repeats the write-and-delete animation multiple times.

    Function Name: LoopWriter

    Args:
        text (str, optional): The text for the animation. Defaults to TEXT.
        loops (int, optional): The number of times to repeat the animation. Defaults to LOOP.
        delay (float, optional): The typing/deleting delay. Defaults to DELAY.
        color (list, optional): A list of HEX colors. Defaults to HEX_COLORS.

    Returns:
        int: The number of characters in the text.

    Examples:
        >>> LoopWriter("Repeat", loops=2, delay=0.01)
        6
    """
    for _ in range(loops):
        DelWriter(text, delay, color=color)
    return len(text)


def SoundWriter(
    text: str = TEXT,
    delay: float = DELAY,
    sound: bool = True,
    frequency: int = FREQUENCY,
    duration: int = SOUND_DURATION,
    color: list = HEX_COLORS,
) -> int:
    """
    Types text with an accompanying sound effect for each character.

    Function Name: SoundWriter

    Args:
        text (str, optional): The text to write. Defaults to TEXT.
        delay (float, optional): The delay between characters. Defaults to DELAY.
        sound (bool, optional): Whether to play a sound. Defaults to True.
        frequency (int, optional): The sound frequency (Windows only). Defaults to FREQUENCY.
        duration (int, optional): The sound duration (Windows only). Defaults to SOUND_DURATION.
        color (list, optional): A list of HEX colors. Defaults to HEX_COLORS.

    Returns:
        int: The number of characters written.

    Examples:
        >>> SoundWriter("Beep", delay=0.1, sound=False) # sound is platform-dependent
        4
    """
    ansi_color = [hex_to_ansi(c) for c in color]
    color_cycle = itertools.cycle(ansi_color)

    for char in text:
        write(f"{next(color_cycle)}{char}{RESET}")
        if sound:
            SoundEffect(frequency, duration)
        time.sleep(delay)
    print()
    return len(text)


def GameDialog(
    speaker: str = "NPC",
    text: str = TEXT,
    delay: float = DELAY,
    sound: bool = False,
    frequency: int = FREQUENCY,
    duration: int = SOUND_DURATION,
    color: list = HEX_COLORS,
) -> int:
    """
    Displays text in a bordered dialog box, as seen in games.

    Function Name: GameDialog

    Args:
        speaker (str, optional): The name of the speaker. Defaults to "NPC".
        text (str, optional): The dialog text. Defaults to TEXT.
        delay (float, optional): The typing delay. Defaults to DELAY.
        sound (bool, optional): Whether to play a sound. Defaults to False.
        frequency (int, optional): Sound frequency. Defaults to FREQUENCY.
        duration (int, optional): Sound duration. Defaults to SOUND_DURATION.
        color (list, optional): A list of HEX colors. Defaults to HEX_COLORS.

    Returns:
        int: The number of characters in the text.

    Examples:
        >>> GameDialog("Hero", "I must save the world!", delay=0.01)
        22
    """
    border = "─" * (len(text) + 10)
    print(f"┌{border}┐")
    print(f"│ {speaker}: ", end="")
    if sound:
        SoundWriter(text, delay, frequency=frequency, duration=duration, color=color)
    else:
        TypeWriter(text, delay, color=color)
    print(f"└{border}┘")
    return len(text)


def RandomWriter(
    text: str = TEXT, delay: float = DELAY - 0.01, color: list = HEX_COLORS
) -> int:
    """
    Types text with a randomized delay to simulate human-like typing.

    Function Name: RandomWriter

    Args:
        text (str, optional): The text to write. Defaults to TEXT.
        delay (float, optional): The base delay. Defaults to DELAY - 0.01.
        color (list, optional): A list of HEX colors. Defaults to HEX_COLORS.

    Returns:
        int: The number of characters written.

    Examples:
        >>> RandomWriter("This is... unpredictable.", delay=0.02)
        25
    """
    ansi_color = [hex_to_ansi(c) for c in color]
    color_cycle = itertools.cycle(ansi_color)

    for char in text:
        base = delay
        if char in ".!?":
            base *= 6
        elif char in ",":
            base *= 2
        elif char in " ":
            base *= 1.5

        base += random.uniform(0.0, 0.03)
        write(f"{next(color_cycle)}{char}{RESET}")
        time.sleep(base)
    print()
    return len(text)


def MarkdownWriter(
    md_text: str = TEXT, delay: float = DELAY, color: list = HEX_COLORS
) -> int:
    """
    Types out the clean text from a Markdown string, stripping the formatting.

    Function Name: MarkdownWriter

    Args:
        md_text (str, optional): The Markdown-formatted text. Defaults to TEXT.
        delay (float, optional): The typing delay. Defaults to DELAY.
        color (list, optional): A list of HEX colors. Defaults to HEX_COLORS.

    Returns:
        int: The number of characters written (after cleaning).

    Examples:
        >>> MarkdownWriter("**Hello** `World`!", delay=0.01)
        11
    """
    clean = re.sub(r"[*_#>`~-]", "", md_text)
    output: int = TypeWriter(text=clean, delay=delay, color=color)
    return output


def HTMLWriter(
    html_text: str = TEXT, delay: float = DELAY, color: list = HEX_COLORS
) -> int:
    """
    Types out the clean text from an HTML string, stripping the tags.

    Function Name: HTMLWriter

    Args:
        html_text (str, optional): The HTML-formatted text. Defaults to TEXT.
        delay (float, optional): The typing delay. Defaults to DELAY.
        color (list, optional): A list of HEX colors. Defaults to HEX_COLORS.

    Returns:
        int: The number of characters written (after cleaning).

    Examples:
        >>> HTMLWriter("<p>Hello <b>World</b></p>", delay=0.01)
        10
    """
    clean = re.sub(r"<[^>]*>", "", html_text)
    output: int = TypeWriter(text=clean, delay=delay, color=color)
    return output


def GlitchWriter(
    text: str = TEXT,
    glitch: str = GLITCH,
    delay: float = DELAY,
    color: list = HEX_COLORS,
) -> int:
    """
    Types text with a "glitch" effect, where random characters appear first.

    Function Name: GlitchWriter

    Args:
        text (str, optional): The text to write. Defaults to TEXT.
        glitch (str, optional): The set of characters to use for the glitch effect. Defaults to GLITCH.
        delay (float, optional): The delay between characters. Defaults to DELAY.
        color (list, optional): A list of HEX colors. Defaults to HEX_COLORS.

    Returns:
        int: The number of characters written.

    Examples:
        >>> GlitchWriter("System Failure", delay=0.01)
        14
    """
    ansi_color = [hex_to_ansi(c) for c in color]
    color_cycle = itertools.cycle(ansi_color)

    for char in text:
        write(f"{next(color_cycle)}{random.choice(glitch)}{RESET}")
        time.sleep(delay)
        write("" + f"{next(color_cycle)}{char}{RESET}")
    print()
    return len(text)


def ThinkWriter(
    text: str = TEXT,
    dots: int = DOTS,
    loop: int = LOOP,
    delay: float = DELAY,
    color: list = HEX_COLORS,
) -> int:
    """
    Simulates a "thinking" animation with a message and trailing dots.

    Function Name: ThinkWriter

    Args:
        text (str, optional): The thinking message. Defaults to TEXT.
        dots (int, optional): The number of dots to animate. Defaults to DOTS.
        loop (int, optional): The number of times to loop the animation. Defaults to LOOP.
        delay (float, optional): The delay between dots. Defaults to DELAY.
        color (list, optional): A list of HEX colors. Defaults to HEX_COLORS.

    Returns:
        int: The number of characters in the text.

    Examples:
        >>> ThinkWriter("Loading", dots=3, loop=1, delay=0.1)
        7
    """
    ansi_color = [hex_to_ansi(c) for c in color]
    color_cycle = itertools.cycle(ansi_color)

    for _ in range(loop):
        write(f"{next(color_cycle)}{text}{RESET}")
        for _ in range(dots):
            write(".")
            time.sleep(delay)
        write(f"{next(color_cycle)}{'' + ' ' * (len(text) + dots) + ''}{RESET}")
    print()
    return len(text)


def ReverseWriter(
    text: str = TEXT, delay: float = DELAY, color: list = HEX_COLORS
) -> int:
    """
    Types out text in reverse order.

    Function Name: ReverseWriter

    Args:
        text (str, optional): The text to write. Defaults to TEXT.
        delay (float, optional): The delay between characters. Defaults to DELAY.
        color (list, optional): A list of HEX colors. Defaults to HEX_COLORS.

    Returns:
        int: The number of characters written.

    Examples:
        >>> ReverseWriter("esrever", delay=0.01)
        7
    """
    ansi_color = [hex_to_ansi(c) for c in color]
    color_cycle = itertools.cycle(ansi_color)

    for char in reversed(text):
        write(f"{next(color_cycle)}{char}{RESET}")
        time.sleep(delay)
    print()
    return len(text)


def ReverseGlitchWriter(
    text: str = TEXT,
    glitch: str = GLITCH,
    delay: float = DELAY,
    color: list = HEX_COLORS,
) -> int:
    """
    Types text in reverse with a "glitch" effect.

    Function Name: ReverseGlitchWriter

    Args:
        text (str, optional): The text to write. Defaults to TEXT.
        glitch (str, optional): The set of glitch characters. Defaults to GLITCH.
        delay (float, optional): The delay between characters. Defaults to DELAY.
        color (list, optional): A list of HEX colors. Defaults to HEX_COLORS.

    Returns:
        int: The number of characters written.

    Examples:
        >>> ReverseGlitchWriter("hctilg", delay=0.01)
        6
    """
    ansi_color = [hex_to_ansi(c) for c in color]
    color_cycle = itertools.cycle(ansi_color)

    for char in reversed(text):
        write(f"{next(color_cycle)}{random.choice(glitch)}{RESET}")
        time.sleep(delay)
        write(f"{next(color_cycle)}" + char + f"{RESET}")
    print()
    return len(text)


def BounceWriter(
    text: str = TEXT, delay: float = DELAY, loop: int = LOOP, color: list = HEX_COLORS
) -> int:
    """
    Types text forwards and then deletes it in a "bouncing" animation.

    Function Name: BounceWriter

    Args:
        text (str, optional): The text for the animation. Defaults to TEXT.
        delay (float, optional): The delay for typing and deleting. Defaults to DELAY.
        loop (int, optional): The number of times to loop. Defaults to LOOP.
        color (list, optional): A list of HEX colors. Defaults to HEX_COLORS.

    Returns:
        int: The number of characters in the text.

    Examples:
        >>> BounceWriter("Bounce", delay=0.01, loop=1)
        6
    """
    ansi_color = [hex_to_ansi(c) for c in color]
    color_cycle = itertools.cycle(ansi_color)

    for _ in range(loop):
        for char in text:
            write(f"{next(color_cycle)}{char}{RESET}")
            time.sleep(delay)

        for _ in text:
            write(f"{next(color_cycle)} {RESET}")
            time.sleep(delay)
    print()
    return len(text)


def BounceGlitchWriter(
    text: str = TEXT,
    glitch: str = GLITCH,
    delay: float = DELAY,
    loop: int = LOOP,
    glitch_color: list = HEX_COLORS,
    color: list = HEX_COLORS,
) -> int:
    """
    A bouncing animation that includes a glitch effect during typing.

    Function Name: BounceGlitchWriter

    Args:
        text (str, optional): The text for the animation. Defaults to TEXT.
        glitch (str, optional): The set of glitch characters. Defaults to GLITCH.
        delay (float, optional): The animation delay. Defaults to DELAY.
        loop (int, optional): The number of loops. Defaults to LOOP.
        glitch_color (list, optional): HEX colors for the glitch characters. Defaults to HEX_COLORS.
        color (list, optional): HEX colors for the final text. Defaults to HEX_COLORS.

    Returns:
        int: The number of characters in the text.

    Examples:
        >>> BounceGlitchWriter("Glitched Bounce", delay=0.01, loop=1)
        15
    """
    ansi_glitch_color = [hex_to_ansi(c) for c in glitch_color]
    glitch_color_cycle = itertools.cycle(ansi_glitch_color)

    ansi_color = [hex_to_ansi(c) for c in color]
    color_cycle = itertools.cycle(ansi_color)

    for _ in range(loop):
        for char in text:
            write(f"{next(glitch_color_cycle)}{random.choice(glitch)}{RESET}")
            time.sleep(delay)
            write(f"{next(color_cycle)}{char}{RESET}")
            time.sleep(delay)

        for _ in text:
            write(" ")
            time.sleep(delay)
    print()
    return len(text)


def GradientWriter(
    text: str = TEXT,
    start_hex: str = START_HEX,
    end_hex: str = END_HEX,
    delay: float = DELAY,
):
    """
    Types out text with a smooth color gradient from a start to an end color.

    Function Name: GradientWriter

    Args:
        text (str, optional): The text to write. Defaults to TEXT.
        start_hex (str, optional): The starting HEX color of the gradient. Defaults to START_HEX.
        end_hex (str, optional): The ending HEX color of the gradient. Defaults to END_HEX.
        delay (float, optional): The delay between characters. Defaults to DELAY.

    Returns:
        None

    Examples:
        >>> GradientWriter("Gradient", start_hex="#FF0000", end_hex="#0000FF", delay=0.01)
    """
    colored_text = gradient(text=text, start_hex=start_hex, end_hex=end_hex)
    
    # This is a workaround to print character by character with delay.
    # It splits the string by the escape character to handle multi-byte characters and color codes.
    parts = colored_text.split('[')
    
    # The first part might be empty or a character, print it
    if parts[0]:
        write(parts[0])
        time.sleep(delay)

    # Print the rest of the parts, re-adding the escape character
    for part in parts[1:]:
        # Find the end of the color code
        m_pos = part.find('m')
        if m_pos != -1:
            # We have a color code and a character
            color_code = '[' + part[:m_pos+1]
            char = part[m_pos+1:]
            if char:
                write(color_code + char)
                time.sleep(delay)
        else:
            # Should not happen with the gradient function, but as a fallback
            write('[' + part)
            time.sleep(delay)

    if not text.endswith("\n"):
        print()
