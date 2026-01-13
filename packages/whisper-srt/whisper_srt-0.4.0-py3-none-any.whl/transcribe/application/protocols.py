"""Application layer protocols.

This module defines the Protocol interfaces used by the Application layer.
Infrastructure implementations must conform to these protocols.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

__all__ = ["TranscriptionClientProtocol"]


class TranscriptionClientProtocol(Protocol):
    """Protocol for audio transcription implementations.

    This Protocol defines the contract for Whisper-based or other
    speech-to-text transcription services. It enables the Application
    layer to depend on an abstraction rather than concrete implementations,
    supporting dependency injection and facilitating testing.

    Example:
        >>> from transcribe.infrastructure.openai_client import OpenAITranscriptionClient
        >>> from transcribe.application.protocols import TranscriptionClientProtocol
        >>> client: TranscriptionClientProtocol = OpenAITranscriptionClient()
        >>> segment_count = client.transcribe(
        ...     audio_path=Path("audio/source.mp3"),
        ...     output_path=Path("subtitle.srt"),
        ... )
        >>> isinstance(segment_count, int)
        True
    """

    def transcribe(
        self,
        audio_path: Path,
        output_path: Path,
    ) -> int:
        """Transcribe audio file to SRT format.

        Converts an audio file (MP3) to SRT subtitle format using
        speech-to-text transcription with timing information.

        Args:
            audio_path: Path to the input audio file (MP3 format).
                Must be a valid Path object pointing to an existing file.
            output_path: Path where the SRT file will be saved.
                Parent directory must exist.

        Returns:
            Number of subtitle segments generated.

        Raises:
            FileNotFoundError: If audio_path does not exist.
            RuntimeError: If transcription fails due to API errors,
                network issues, or other unexpected conditions.

        Preconditions:
            - audio_path exists and is a valid audio file
            - output_path parent directory exists
            - Valid API credentials are configured (e.g., OPENAI_API_KEY)

        Postconditions:
            - SRT file is created at output_path
            - SRT file contains valid subtitle segments with timestamps
            - Returns positive integer (segment count)
        """
        ...
