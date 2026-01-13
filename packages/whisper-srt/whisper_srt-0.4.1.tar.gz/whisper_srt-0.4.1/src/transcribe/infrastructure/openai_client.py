"""OpenAI Whisper API transcription client.

This module provides a transcription implementation using OpenAI's
Whisper API (whisper-1 model) for cloud-based speech-to-text conversion.
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from transcribe.domain.vocabulary import DEFAULT_VOCABULARY

logger = logging.getLogger(__name__)


class OpenAITranscriptionClient:
    """Transcription client using OpenAI Whisper API.

    This implementation uses OpenAI's cloud-based Whisper API (whisper-1),
    which directly outputs SRT format without local model loading.

    Configuration:
        - Model: whisper-1 (OpenAI's hosted Whisper)
        - Language: Japanese (default, configurable)
        - API Key: Read from OPENAI_API_KEY environment variable
        - Vocabulary: Custom terms to improve recognition accuracy

    Example:
        >>> from pathlib import Path
        >>> client = OpenAITranscriptionClient()
        >>> count = client.transcribe(
        ...     audio_path=Path("audio/source.mp3"),
        ...     output_path=Path("subtitle.srt"),
        ... )
        >>> print(f"Generated {count} segments")
    """

    _DEFAULT_LANGUAGE = "ja"

    def __init__(
        self,
        language: str | None = None,
        vocabulary: tuple[str, ...] | None = None,
    ) -> None:
        """Initialize the OpenAI transcription client.

        Loads API key from environment variable OPENAI_API_KEY.
        The .env file is automatically loaded if present.

        Args:
            language: Target language code for transcription (ISO-639-1).
                Default is "ja" for Japanese.
            vocabulary: Custom vocabulary terms to improve recognition.
                Default is built-in AI/MCP technical terms.

        Raises:
            ValueError: If OPENAI_API_KEY environment variable is not set.
        """
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            msg = "OPENAI_API_KEY environment variable is not set"
            raise ValueError(msg)

        self._client = OpenAI(api_key=api_key)
        self._language = language or self._DEFAULT_LANGUAGE
        self._vocabulary = vocabulary or DEFAULT_VOCABULARY

    def transcribe(
        self,
        audio_path: Path,
        output_path: Path,
    ) -> int:
        """Transcribe audio file to SRT format using OpenAI Whisper API.

        Calls OpenAI's Whisper API with response_format="srt" to get
        SRT-formatted subtitles directly.

        Args:
            audio_path: Path to the input audio file (MP3 format).
            output_path: Path where the SRT file will be saved.

        Returns:
            Number of subtitle segments generated.

        Raises:
            FileNotFoundError: If audio_path does not exist.
            RuntimeError: If API call or transcription fails.
        """
        # Validate audio file exists
        if not audio_path.exists():
            msg = f"Audio file not found: {audio_path}"
            raise FileNotFoundError(msg)

        # Create parent directories if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            logger.info("Calling OpenAI Whisper API for %s...", audio_path)

            # Build prompt from vocabulary (token limit: 244 tokens, may be truncated)
            prompt = ", ".join(self._vocabulary)
            logger.debug("Using prompt with %d vocabulary terms", len(self._vocabulary))

            with open(audio_path, "rb") as audio_file:
                transcript = self._client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="srt",
                    language=self._language,
                    prompt=prompt,
                )

        except AuthenticationError as e:
            msg = f"OpenAI authentication failed. Check your OPENAI_API_KEY: {e}"
            logger.error(msg)
            raise RuntimeError(msg) from e
        except RateLimitError as e:
            msg = f"OpenAI rate limit exceeded. Please wait and try again: {e}"
            logger.warning(msg)
            raise RuntimeError(msg) from e
        except APITimeoutError as e:
            msg = f"OpenAI API request timed out. Please try again: {e}"
            logger.warning(msg)
            raise RuntimeError(msg) from e
        except APIConnectionError as e:
            msg = f"Failed to connect to OpenAI API. Check your network: {e}"
            logger.error(msg)
            raise RuntimeError(msg) from e
        except Exception as e:
            msg = f"Transcription API call failed: {e}"
            logger.exception(msg)
            raise RuntimeError(msg) from e

        # Write SRT content to file (separate try block for I/O errors)
        try:
            output_path.write_text(transcript, encoding="utf-8")
        except OSError as e:
            msg = f"Failed to write output file '{output_path}': {e}"
            logger.error(msg)
            raise RuntimeError(msg) from e

        # Log warning for empty transcript
        if not transcript or transcript.strip() == "":
            logger.warning(
                "OpenAI returned empty transcript for %s. "
                "This may indicate silent audio or an unsupported format.",
                audio_path,
            )

        # Count segments (SRT segments start with a number on its own line)
        segment_count = len(re.findall(r"^\d+$", transcript, re.MULTILINE))

        logger.info(
            "Transcription complete: %d segments saved to %s",
            segment_count,
            output_path,
        )

        return segment_count
