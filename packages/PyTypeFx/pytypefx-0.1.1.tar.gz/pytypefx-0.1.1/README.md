# PyTypeFx

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/downloads/)

A Python library for creating captivating terminal typing effects with ease.

PyTypeFx is a versatile and easy-to-use Python library designed to bring your terminal applications to life with a variety of dynamic and customizable typing effects. Whether you're creating a command-line game, a stylish installation script, or just want to add a bit of flair to your program's output, TypeFx provides the tools you need.

## Features

- **Multiple Typing Effects**: A rich collection of writer functions including `TypeWriter`, `RainbowWriter`, `GlitchWriter`, `BounceWriter`, and more.
- **Color and Styling**: Extensive color support, including basic, bright, and extended named colors, as well as HEX and RGB.
- **Gradient Text**: Create beautiful gradient effects on your text.
- **Decorator Support**: A simple `@typefx` decorator to apply effects to function outputs.
- **Sound Effects**: Add auditory feedback to your typing effects (platform-dependent).
- **Command-Line Interface**: A built-in CLI for applying effects directly from your terminal.
- **Customizable**: Easily configure delay, speed, colors, and other parameters.
- **No Dependencies**: Pure Python, with no external libraries required.

## Installation

You can install PyTypeFx using pip:

```bash
pip install PyTypeFx==0.1.1
```

## Usage

### Basic Usage

The core of TypeFx is its writer functions. Here's a simple example using the `TypeWriter`:

```python
from TypeFx import TypeWriter

TypeWriter("Hello, World!", delay=0.05)
```

### Writers

TypeFx comes with a variety of writers, each providing a different effect:

| Writer | Description |
| --- | --- |
| `TypeWriter` | Simulates standard typing. |
| `RainbowWriter` | Types text with a rainbow color effect. |
| `HexWriter` | Types text using a list of HEX colors. |
| `DelWriter` | Types and then deletes text. |
| `LoopWriter` | Repeats the write-and-delete animation. |
| `SoundWriter` | Types text with an accompanying sound. |
| `GameDialog` | Displays text in a game-style dialog box. |
| `RandomWriter` | Types with a randomized, human-like delay. |
| `MarkdownWriter` | Strips Markdown formatting and types the clean text. |
| `HTMLWriter` | Strips HTML tags and types the clean text. |
| `GlitchWriter` | Types with a "glitch" effect. |
| `ThinkWriter` | Simulates a "thinking" animation with trailing dots. |
| `ReverseWriter` | Types text in reverse. |
| `ReverseGlitchWriter` | Types text in reverse with a glitch effect. |
| `BounceWriter` | Types text forwards and then deletes it. |
| `BounceGlitchWriter` | A bouncing animation with a glitch effect. |
| `GradientWriter` | Types text with a smooth color gradient. |

**Example:**

```python
from TypeFx import RainbowWriter, GlitchWriter

RainbowWriter("This is a rainbow effect!", delay=0.03)
GlitchWriter("This is a glitch effect!", delay=0.01)
```

### Decorator

The `@typefx` decorator allows you to easily apply typing effects to the output of any function.

```python
from TypeFx import typefx

@typefx(hex_colors=["#FF0000", "#00FF00", "#0000FF"], delay=0.03)
def my_message():
    print("This message will be typed out with a cool effect!")

my_message()
```

### Command-Line Interface

You can also use TypeFx directly from your terminal.

```bash
typefx --text "Hello from the CLI!" --delay 0.05 --rainbow
```

**CLI Options:**

| Option | Description |
| --- | --- |
| `-t`, `--text` | Text to type. |
| `-d`, `--delay` | Delay between characters. |
| `-l`, `--loops` | Number of loops for effects like `LoopWriter`. |
| `-r`, `--rainbow` | Use the rainbow effect. |
| `-rnd`, `--random` | Use the random writer effect. |
| `-s`, `--sound` | Use the sound effect. |
| `-f`, `--file` | Read text from a file. |

## API Reference

### `writers`

The `writers` module contains all the typing effect functions. See the "Writers" section above for a full list.

### `effects`

- `BlinkEffect(duration: float, cursor: str, delay: float)`: Displays a blinking cursor.
- `SoundEffect(frequency: int, duration: int)`: Plays a sound (platform-dependent).

### `decorator`

- `@typefx(hex_colors=None, delay: float = 0.05, loop: int = 1, speed: str = "normal")`: A decorator to apply typewriter effects to function output.

### `colors`

The `colors` module provides a wide range of color and formatting constants, as well as helper functions:

- `hex_to_ansi(hex_color: str) -> str`: Converts a HEX color to an ANSI escape code.
- `rgb_to_ansi(r: int, g: int, b: int) -> str`: Converts an RGB color to an ANSI escape code.
- `colorize(text: str, *style: str) -> str`: Applies ANSI styles to text.

### `utility`

- `gradient(text: str, start_hex: str, end_hex: str) -> str`: Applies a color gradient to text.
- `supports_ansi() -> bool`: Checks if the terminal supports ANSI escape codes.

## Configuration

The `constant` module contains default values that can be customized:

| Constant | Default Value | Description |
| --- | --- | --- |
| `TEXT` | `"Hello World!"` | Default text for writers. |
| `GLITCH` | `"!@#$%^&*()_+-=[]{}|;':\",./<>?"` | Characters for the glitch effect. |
| `CURSOR` | `_` | Default cursor for `BlinkEffect`. |
| `DELAY` | `0.05` | Default delay between characters. |
| `DURATION` | `2` | Default duration for effects. |
| `HOLD` | `1` | Default hold time for `DelWriter`. |
| `LOOP` | `3` | Default number of loops. |
| `DOTS` | `3` | Default number of dots for `ThinkWriter`. |
| `FREQUENCY` | `800` | Default sound frequency. |
| `SOUND_DURATION` | `30` | Default sound duration. |
| `START_HEX` | `"#E74C3C"` | Default start color for gradients. |
| `END_HEX` | `"#2ECC71"` | Default end color for gradients. |

## Examples

### Gradient Text

```python
from TypeFx import GradientWriter

GradientWriter("This is a beautiful gradient!", start_hex="#FF00FF", end_hex="#00FFFF", delay=0.02)
```

### Game Dialog

```python
from TypeFx import GameDialog

GameDialog(speaker="Hero", text="I must defeat the final boss!", delay=0.04, sound=True)
```

### Chaining Effects

```python
from TypeFx import TypeWriter, DelWriter, BlinkEffect

TypeWriter("Preparing for deletion...")
DelWriter("This message will self-destruct.", hold=2)
BlinkEffect(duration=2)
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
