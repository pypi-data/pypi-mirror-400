import argparse

from PyTypeFx.writers import (
    LoopWriter,
    RainbowWriter,
    RandomWriter,
    SoundWriter,
    TypeWriter,
)


def main():
    parser = argparse.ArgumentParser(description="TypeFx CLI")
    parser.add_argument(
        "-t", "--text", type=str, default="Hello, World!", help="Text to type"
    )
    parser.add_argument(
        "-d", "--delay", type=float, default=0.05, help="Delay between characters"
    )
    parser.add_argument("-l", "--loops", type=int, default=3, help="Number of loops")
    parser.add_argument("-r", "--rainbow", action="store_true", help="Rainbow effect")
    parser.add_argument("-rnd", "--random", action="store_true", help="Sound effect")
    parser.add_argument("-s", "--sound", action="store_true", help="Sound effect")
    parser.add_argument("-f", "--file", type=str, help="File to read text from")
    args = parser.parse_args()

    if args.file:
        with open(args.file, "r") as f:
            text = f.read()
            TypeWriter(text, args.delay)
    else:
        text = args.text
        TypeWriter(text, args.delay)

    if args.rainbow:
        RainbowWriter(text, args.delay)
    elif args.sound:
        SoundWriter(text, args.delay)
    elif args.random:
        RandomWriter(text, args.delay)
    else:
        TypeWriter(text, args.delay)

    if args.loops > 1:
        LoopWriter(text, args.loops, args.delay)


if __name__ == "__main__":
    main()
