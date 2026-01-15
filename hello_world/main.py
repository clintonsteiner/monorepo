#!/usr/bin/env python3
"""Hello World application."""

import argparse
import sys


def hello(name: str) -> None:
    """Print a greeting."""
    print(f"Hello, {name}!")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="A simple hello world application")
    parser.add_argument(
        "--name",
        default="World",
        help="Name to greet (default: World)",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="Number of times to repeat (default: 1)",
    )

    args = parser.parse_args()

    for _ in range(args.repeat):
        hello(args.name)

    return 0


if __name__ == "__main__":
    sys.exit(main())
