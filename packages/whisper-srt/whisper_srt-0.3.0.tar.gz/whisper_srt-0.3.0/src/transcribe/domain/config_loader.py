"""Configuration file loader.

Manages language settings stored in config file.
"""

from __future__ import annotations

from pathlib import Path

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "whisper-srt"
DEFAULT_LANGUAGE_PATH = DEFAULT_CONFIG_DIR / "language.txt"
DEFAULT_LANGUAGE = "en"

SUPPORTED_LANGUAGES = (
    ("en", "English"),
    ("ja", "Japanese"),
    ("zh", "Chinese"),
    ("ko", "Korean"),
    ("es", "Spanish"),
    ("fr", "French"),
    ("de", "German"),
    ("pt", "Portuguese"),
    ("it", "Italian"),
    ("ru", "Russian"),
)


def load_default_language() -> str:
    """Load default language from config file.

    Returns:
        Language code from config file, or DEFAULT_LANGUAGE if file not found
    """
    if DEFAULT_LANGUAGE_PATH.exists():
        content = DEFAULT_LANGUAGE_PATH.read_text(encoding="utf-8").strip()
        if content:
            return content
    return DEFAULT_LANGUAGE


def save_language(language_code: str) -> None:
    """Save language code to config file.

    Args:
        language_code: ISO-639-1 language code to save
    """
    DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    DEFAULT_LANGUAGE_PATH.write_text(language_code + "\n", encoding="utf-8")


def prompt_language_selection() -> str:
    """Prompt user to select a language interactively.

    Returns:
        Selected language code
    """
    print("\nSelect default language for transcription:")
    print("-" * 40)
    for i, (code, name) in enumerate(SUPPORTED_LANGUAGES, start=1):
        print(f"  {i:2}. {name} ({code})")
    print("-" * 40)

    while True:
        try:
            user_input = input("\nEnter number (1-10) or language code: ").strip()

            if not user_input:
                print("Using default: English (en)")
                return "en"

            if user_input.isdigit():
                index = int(user_input) - 1
                if 0 <= index < len(SUPPORTED_LANGUAGES):
                    code, name = SUPPORTED_LANGUAGES[index]
                    print(f"Selected: {name} ({code})")
                    return code
                print(f"Invalid number. Please enter 1-{len(SUPPORTED_LANGUAGES)}.")
            else:
                code_lower = user_input.lower()
                for code, name in SUPPORTED_LANGUAGES:
                    if code == code_lower:
                        print(f"Selected: {name} ({code})")
                        return code
                print(f"Using custom language code: {user_input}")
                return user_input

        except EOFError:
            print("\nUsing default: English (en)")
            return "en"
