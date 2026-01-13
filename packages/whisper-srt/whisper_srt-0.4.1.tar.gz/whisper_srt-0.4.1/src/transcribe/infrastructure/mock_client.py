"""Mock transcription client for testing.

This module provides a mock implementation of TranscriptionClientProtocol
that generates a sample SRT file without performing actual transcription.
Useful for testing and development environments where Whisper models
are not available or would take too long to run.
"""

from pathlib import Path


class MockTranscriptionClient:
    """Mock transcription client that creates sample SRT files.

    This implementation satisfies TranscriptionClientProtocol without
    loading Whisper models or performing actual speech-to-text conversion.
    It generates a minimal valid SRT file for testing purposes.

    Example:
        >>> from pathlib import Path
        >>> import tempfile
        >>> client = MockTranscriptionClient()
        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     audio = Path(tmpdir) / "audio.mp3"
        ...     audio.touch()
        ...     output = Path(tmpdir) / "subtitle.srt"
        ...     count = client.transcribe(audio, output)
        ...     assert count > 0
        ...     assert output.exists()
    """

    # Sample SRT content with Japanese text (matching project context)
    _SAMPLE_SRT_CONTENT = """1
00:00:00,000 --> 00:00:03,500
こんにちは、今日はClaude Codeについて

2
00:00:03,500 --> 00:00:07,000
解説していきたいと思います。

3
00:00:07,000 --> 00:00:11,500
MCPという機能を使うと
とても便利になります。
"""

    def transcribe(
        self,
        audio_path: Path,
        output_path: Path,
    ) -> int:
        """Generate a sample SRT file without actual transcription.

        Creates a minimal valid SRT file for testing purposes.
        This method validates that the audio file exists but does not
        actually process it.

        Args:
            audio_path: Path to the input audio file.
                Must exist (validated even in mock).
            output_path: Path where the SRT file will be saved.

        Returns:
            Number of subtitle segments generated (always 3 for mock).

        Raises:
            FileNotFoundError: If audio_path does not exist.

        Example:
            >>> from pathlib import Path
            >>> import tempfile
            >>> client = MockTranscriptionClient()
            >>> with tempfile.TemporaryDirectory() as tmpdir:
            ...     audio = Path(tmpdir) / "test.mp3"
            ...     audio.touch()
            ...     srt = Path(tmpdir) / "test.srt"
            ...     segment_count = client.transcribe(audio, srt)
            ...     assert segment_count == 3
        """
        # Validate audio file exists (consistent with real implementation)
        if not audio_path.exists():
            msg = f"Audio file not found: {audio_path}"
            raise FileNotFoundError(msg)

        # Create parent directories if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write sample SRT content
        output_path.write_text(self._SAMPLE_SRT_CONTENT, encoding="utf-8")

        # Return segment count (3 segments in sample content)
        return 3
