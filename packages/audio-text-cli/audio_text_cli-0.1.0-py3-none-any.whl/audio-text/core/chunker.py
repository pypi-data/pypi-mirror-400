"""Audio chunking for processing long files."""

from dataclasses import dataclass
from pathlib import Path

from pydub import AudioSegment


@dataclass
class AudioChunk:
    """Represents a chunk of audio."""

    path: Path
    index: int
    start_time: float  # seconds from original
    end_time: float  # seconds from original
    duration: float  # chunk duration in seconds


class ChunkerError(Exception):
    """Raised when chunking fails."""

    pass


class Chunker:
    """Splits audio files into manageable chunks."""

    def __init__(
        self,
        chunk_duration_minutes: int = 5,
        overlap_seconds: int = 2,
    ):
        """Initialize chunker.

        Args:
            chunk_duration_minutes: Duration of each chunk in minutes.
            overlap_seconds: Overlap between chunks to avoid cutting words.
        """
        self.chunk_duration_ms = chunk_duration_minutes * 60 * 1000
        self.overlap_ms = overlap_seconds * 1000

    def chunk(self, audio_path: Path) -> list[AudioChunk]:
        """Split audio file into chunks.

        Args:
            audio_path: Path to the audio file.

        Returns:
            List of AudioChunk objects.

        Raises:
            ChunkerError: If chunking fails.
        """
        try:
            audio = AudioSegment.from_file(audio_path)
        except Exception as e:
            raise ChunkerError(f"Failed to load audio file: {e}") from e

        total_duration_ms = len(audio)
        chunks: list[AudioChunk] = []
        chunk_dir = audio_path.parent / "chunks"
        chunk_dir.mkdir(exist_ok=True)

        # If audio is shorter than one chunk, return as single chunk
        if total_duration_ms <= self.chunk_duration_ms:
            return [
                AudioChunk(
                    path=audio_path,
                    index=0,
                    start_time=0,
                    end_time=total_duration_ms / 1000,
                    duration=total_duration_ms / 1000,
                )
            ]

        # Split into chunks with overlap
        start_ms = 0
        index = 0

        while start_ms < total_duration_ms:
            # Calculate end position
            end_ms = min(start_ms + self.chunk_duration_ms, total_duration_ms)

            # Extract chunk
            chunk_audio = audio[start_ms:end_ms]

            # Save chunk
            chunk_path = chunk_dir / f"chunk_{index:03d}.wav"
            chunk_audio.export(chunk_path, format="wav")

            chunks.append(
                AudioChunk(
                    path=chunk_path,
                    index=index,
                    start_time=start_ms / 1000,
                    end_time=end_ms / 1000,
                    duration=(end_ms - start_ms) / 1000,
                )
            )

            # Move start position (subtract overlap for next chunk)
            start_ms = end_ms - self.overlap_ms
            index += 1

            # Prevent infinite loop if we're at the end
            if end_ms >= total_duration_ms:
                break

        return chunks

    def cleanup(self, chunks: list[AudioChunk]) -> None:
        """Remove temporary chunk files."""
        for chunk in chunks:
            if chunk.path.exists() and "chunk_" in chunk.path.name:
                chunk.path.unlink()

        # Try to remove chunks directory if empty
        if chunks and chunks[0].path.parent.name == "chunks":
            chunk_dir = chunks[0].path.parent
            try:
                chunk_dir.rmdir()
            except OSError:
                pass  # Directory not empty or doesn't exist
