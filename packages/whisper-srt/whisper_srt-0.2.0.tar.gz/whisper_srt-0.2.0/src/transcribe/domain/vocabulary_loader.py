"""Vocabulary file loader.

Loads custom vocabulary from text files for Whisper API prompt.
"""

from __future__ import annotations

from pathlib import Path

DEFAULT_VOCABULARY_PATH = Path.home() / ".config" / "whisper-srt" / "vocabulary.txt"


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
