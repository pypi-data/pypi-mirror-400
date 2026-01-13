"""Vocabulary file loader.

Loads custom vocabulary from text files for Whisper API prompt.
"""

from __future__ import annotations

from pathlib import Path

DEFAULT_VOCABULARY_PATH = Path.home() / ".config" / "whisper-srt" / "vocabulary.txt"

SAMPLE_VOCABULARY = """\
# Whisper SRT Vocabulary File
# Add technical terms, proper nouns, and domain-specific words (one per line)
# Lines starting with # are comments

Claude Code
OpenAI
Codex
"""


def initialize_vocabulary_file() -> tuple[bool, str]:
    """Initialize vocabulary file with sample content.

    Returns:
        Tuple of (created, message):
        - (True, path_message) if file was created
        - (False, skip_message) if file already exists
    """
    if DEFAULT_VOCABULARY_PATH.exists():
        return (False, f"Vocabulary file already exists: {DEFAULT_VOCABULARY_PATH}")

    DEFAULT_VOCABULARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_VOCABULARY_PATH.write_text(SAMPLE_VOCABULARY, encoding="utf-8")
    return (True, f"Created vocabulary file: {DEFAULT_VOCABULARY_PATH}")


def load_vocabulary_from_file(path: Path) -> tuple[str, ...]:
    """Load vocabulary from a text file.

    Args:
        path: Path to vocabulary file (one word per line)

    Returns:
        Tuple of vocabulary terms

    Raises:
        FileNotFoundError: If file does not exist
    """
    if not path.exists():
        raise FileNotFoundError(f"Vocabulary file not found: {path}")

    terms = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        # Skip empty lines and comments
        if stripped and not stripped.startswith("#"):
            terms.append(stripped)

    return tuple(terms)


def load_default_vocabulary() -> tuple[str, ...]:
    """Load vocabulary from default location if it exists.

    Returns:
        Tuple of vocabulary terms, or empty tuple if file not found
    """
    if DEFAULT_VOCABULARY_PATH.exists():
        return load_vocabulary_from_file(DEFAULT_VOCABULARY_PATH)
    return ()
