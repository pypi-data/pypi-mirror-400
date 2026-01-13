import os
import sys
import time

from PyTypeFx.constant import CURSOR, DELAY, DURATION


def BlinkEffect(
    duration: float = DURATION, cursor: str = CURSOR, delay: float = DELAY
) -> None:
    """
    Displays a blinking cursor effect in the console for a specified duration.

    Function Name: BlinkEffect

    Args:
        duration (float, optional): The total time in seconds for the effect to run.
            Defaults to DURATION.
        cursor (str, optional): The character to use for the cursor.
            Defaults to CURSOR.
        delay (float, optional): The delay between blink states (on/off).
            Defaults to DELAY.

    Returns:
        None

    Examples:
        >>> BlinkEffect(duration=1, cursor="|", delay=0.2)
        # Displays a blinking cursor for 1 second.
    """
    end: float = time.time() + duration
    while time.time() < end:
        sys.stdout.write(cursor)
        sys.stdout.flush()
        time.sleep(delay)
        sys.stdout.write(" ")
        sys.stdout.flush()
        time.sleep(delay)


def SoundEffect(frequency: int, duration: int) -> None:
    """
    Plays a sound effect.

    On Windows, it uses `winsound.Beep`. On other systems (Linux/macOS),
    it prints the terminal bell character ``.

    Function Name: SoundEffect

    Args:
        frequency (int): The frequency of the beep in Hertz (Windows only).
        duration (int): The duration of the beep in milliseconds (Windows only).

    Returns:
        None

    Examples:
        >>> SoundEffect(frequency=800, duration=100)
        # Plays a short beep sound.
    """
    # Windows sound effect
    if os.name == "nt":
        import winsound

        winsound.Beep(frequency, duration)
    else:
        # Terminal bell for Linux/macOS sound effect
        sys.stdout.write("")
        sys.stdout.flush()
