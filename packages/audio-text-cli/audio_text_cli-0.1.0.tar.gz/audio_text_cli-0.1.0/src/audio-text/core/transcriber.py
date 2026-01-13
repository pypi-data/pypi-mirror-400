"""Whisper-based audio transcription."""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import whisper

from video_to_text.models import Segment


@dataclass
class TranscriptionResult:
    """Result of transcribing a single audio file or chunk."""

    segments: list[Segment]
    language: str
    text: str


class TranscriberError(Exception):
    """Raised when transcription fails."""

    pass


class Transcriber:
    """Transcribes audio using OpenAI Whisper."""

    SUPPORTED_MODELS = ["tiny", "base", "small", "medium", "large"]

    def __init__(self, model_name: str = "small"):
        """Initialize transcriber.

        Args:
            model_name: Whisper model to use. Default is 'small'.

        Raises:
            TranscriberError: If model name is invalid.
        """
        if model_name not in self.SUPPORTED_MODELS:
            raise TranscriberError(
                f"Invalid model: {model_name}. "
                f"Supported models: {', '.join(self.SUPPORTED_MODELS)}"
            )

        self.model_name = model_name
        self._model: whisper.Whisper | None = None

    @property
    def model(self) -> whisper.Whisper:
        """Lazy load the Whisper model."""
        if self._model is None:
            try:
                self._model = whisper.load_model(self.model_name)
            except Exception as e:
                raise TranscriberError(f"Failed to load model: {e}") from e
        return self._model

    def transcribe(
        self,
        audio_path: Path,
        time_offset: float = 0.0,
        progress_callback: Callable[[float], None] | None = None,
    ) -> TranscriptionResult:
        """Transcribe audio file to text.

        Args:
            audio_path: Path to audio file.
            time_offset: Offset to add to segment timestamps (for chunks).
            progress_callback: Optional callback for progress updates.

        Returns:
            TranscriptionResult with segments and metadata.

        Raises:
            TranscriberError: If transcription fails.
        """
        if not audio_path.exists():
            raise TranscriberError(f"Audio file not found: {audio_path}")

        try:
            # Transcribe with word timestamps for better accuracy
            result = self.model.transcribe(
                str(audio_path),
                language="en",
                task="transcribe",
                verbose=False,
            )
        except Exception as e:
            raise TranscriberError(f"Transcription failed: {e}") from e

        # Convert Whisper segments to our Segment model
        segments = []
        for seg in result.get("segments", []):
            segment = Segment(
                text=seg["text"].strip(),
                start_time=seg["start"] + time_offset,
                end_time=seg["end"] + time_offset,
            )
            segments.append(segment)

        if progress_callback:
            progress_callback(1.0)

        return TranscriptionResult(
            segments=segments,
            language=result.get("language", "en"),
            text=result.get("text", "").strip(),
        )

    def transcribe_with_progress(
        self,
        audio_path: Path,
        time_offset: float = 0.0,
    ) -> TranscriptionResult:
        """Transcribe with default progress handling.

        This is a convenience method for when you don't need custom progress.
        """
        return self.transcribe(audio_path, time_offset)
