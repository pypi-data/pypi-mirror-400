"""Default vocabulary for transcription.

The built-in vocabulary is empty. Users can provide custom vocabulary
via ~/.config/whisper-srt/vocabulary.txt or --vocabulary option.
"""

# Empty by default - users provide their own vocabulary
DEFAULT_VOCABULARY: tuple[str, ...] = ()
