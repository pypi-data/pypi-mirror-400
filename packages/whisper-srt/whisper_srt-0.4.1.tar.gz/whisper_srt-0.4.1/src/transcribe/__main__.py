"""Entry point for running as a module.

Usage:
    python -m transcribe input.mp3 -o output.srt
"""

import sys

from transcribe.interface.cli import main

if __name__ == "__main__":
    sys.exit(main())
