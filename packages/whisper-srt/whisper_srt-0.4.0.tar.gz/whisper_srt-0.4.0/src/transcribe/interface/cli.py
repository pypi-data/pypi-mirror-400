"""Command-line interface for transcription.

This module provides the CLI entry point for transcribing
MP3 audio files to SRT subtitle format using OpenAI Whisper API.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from transcribe import __version__
from transcribe.application.protocols import TranscriptionClientProtocol
from transcribe.domain.config_loader import (
    load_default_language,
    prompt_language_selection,
    save_language,
)
from transcribe.domain.vocabulary_loader import (
    initialize_vocabulary_file,
    load_default_vocabulary,
    load_vocabulary_from_file,
)
from transcribe.infrastructure.openai_client import OpenAITranscriptionClient

logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="whisper-srt",
        description="Transcribe MP3 audio to SRT subtitle format using OpenAI Whisper API.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  whisper-srt input.mp3                       # Output: input.srt
  whisper-srt input.mp3 -o output.srt         # Specify output file
  whisper-srt input.mp3 --language en         # English transcription
        """,
    )

    parser.add_argument(
        "input",
        type=Path,
        nargs="?",
        default=None,
        help="Input MP3 file path",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output SRT file path (default: {input_stem}.srt)",
    )

    parser.add_argument(
        "--language",
        type=str,
        default=None,
        help="Target language code for transcription (ISO-639-1, default: from config or en)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize vocabulary file at ~/.config/whisper-srt/vocabulary.txt",
    )

    vocab_group = parser.add_mutually_exclusive_group()
    vocab_group.add_argument(
        "--vocabulary",
        type=Path,
        default=None,
        help="Path to vocabulary file (one word per line)",
    )
    vocab_group.add_argument(
        "--no-vocabulary",
        action="store_true",
        help="Disable vocabulary loading",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI.

    Args:
        argv: Command-line arguments (default: sys.argv[1:]).

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(levelname)s: %(message)s",
    )

    # Handle --init option
    if args.init:
        created, message = initialize_vocabulary_file()
        print(message)

        language = prompt_language_selection()
        save_language(language)
        print(f"\nLanguage setting saved: {language}")
        return 0

    # Validate input argument
    if args.input is None:
        parser.error("the following arguments are required: input")

    # Validate input file
    input_path: Path = args.input
    if not input_path.exists():
        logger.error("Input file not found: %s", input_path)
        return 1

    if input_path.suffix.lower() != ".mp3":
        logger.warning("Input file does not have .mp3 extension: %s", input_path)

    # Determine output path
    output_path: Path | None = args.output
    if output_path is None:
        output_path = input_path.with_suffix(".srt")

    # Load vocabulary
    if args.no_vocabulary:
        vocabulary: tuple[str, ...] = ()
    elif args.vocabulary:
        try:
            vocabulary = load_vocabulary_from_file(args.vocabulary)
        except FileNotFoundError:
            logger.error("Vocabulary file not found: %s", args.vocabulary)
            return 1
    else:
        vocabulary = load_default_vocabulary()

    if vocabulary:
        logger.debug("Loaded %d vocabulary terms", len(vocabulary))

    # Determine language
    language = args.language if args.language else load_default_language()
    logger.debug("Using language: %s", language)

    # Create client and transcribe
    try:
        client: TranscriptionClientProtocol = OpenAITranscriptionClient(
            language=language, vocabulary=vocabulary
        )
    except ValueError as e:
        logger.error(str(e))
        return 1

    try:
        logger.info("Transcribing %s...", input_path)
        segment_count = client.transcribe(input_path, output_path)
        logger.info("Generated %d segments: %s", segment_count, output_path)
        print(f"Transcription complete: {segment_count} segments saved to {output_path}")
        return 0

    except (FileNotFoundError, RuntimeError) as e:
        logger.error("%s", e)
        return 1

    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        return 130


if __name__ == "__main__":
    sys.exit(main())
