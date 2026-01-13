import functools
import io
import sys
import time

from PyTypeFx.utility import _make_color, _make_delay, _type_out_text


def typefx(hex_colors=None, delay: float = 0.05, loop: int = 1, speed: str = "normal"):
    """
    A decorator that applies a typewriter effect to the output of a function.

    This decorator captures the output of the decorated function (either from `print`
    statements or the return value) and prints it to the console with a
    character-by-character delay, simulating a typewriter. It supports various
    color schemes, speeds, and looping.

    Function Name: typefx

    Args:
        hex_colors (str or list, optional): A single HEX color, a list of HEX colors,
            or a predefined palette name (e.g., "rainbow", "random"). Defaults to None.
        delay (float, optional): The base delay between characters in seconds.
            Defaults to 0.05.
        loop (int, optional): The number of times to repeat the animation.
            Defaults to 1.
        speed (str, optional): The typing speed ("fast", "slow", "normal", "random", "none").
            Defaults to "normal".

    Returns:
        function: A decorator that wraps the original function.

    Examples:
        @typefx(hex_colors=["#FF0000", "#00FF00"], delay=0.05, loop=2, speed="fast")
        def my_function():
            print("Hello, World!")
        my_function()

        @typefx(hex_colors="rainbow", delay=0.03, loop=1)
        def generate_message() -> str:
            return "Hello, World!...."
        print(generate_message())

        # Using as a function wrapper
        print_effect = typefx(hex_colors="random", delay=0.03)
        print_effect(print)("Hello from a wrapped print!")
    """
    delay_fn = _make_delay(delay, speed)
    color_fn = _make_color(hex_colors)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            real_stdout = sys.stdout
            buf = io.StringIO()
            sys.stdout = buf
            try:
                result = func(*args, **kwargs)
            finally:
                sys.stdout = real_stdout
            if isinstance(result, str) and result:
                text_type = result
            else:
                printed = buf.getvalue()
                if printed:
                    text_type = printed
                elif result is None:
                    text_type = str(result)
                else:
                    text_type = ""
            if not text_type:
                return result

            for _ in range(max(1, int(loop))):
                _type_out_text(text_type, delay_fn, color_fn)
                time.sleep(0.12)
            return result

        return wrapper

    return decorator
