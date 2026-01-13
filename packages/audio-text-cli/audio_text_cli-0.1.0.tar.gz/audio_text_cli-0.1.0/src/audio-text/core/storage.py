"""JSON file storage for transcripts."""

import json
from pathlib import Path

from video_to_text.models import Transcript


class StorageError(Exception):
    """Raised when storage operation fails."""

    pass


class Storage:
    """Handles saving and loading transcripts as JSON files."""

    INDEX_FILE = "index.json"

    def __init__(self, base_dir: Path):
        """Initialize storage.

        Args:
            base_dir: Base directory for storing transcripts.
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_index()

    def _ensure_index(self) -> None:
        """Ensure index file exists."""
        index_path = self.base_dir / self.INDEX_FILE
        if not index_path.exists():
            self._write_index({})

    def _read_index(self) -> dict:
        """Read the index file."""
        index_path = self.base_dir / self.INDEX_FILE
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _write_index(self, index: dict) -> None:
        """Write the index file."""
        index_path = self.base_dir / self.INDEX_FILE
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2, ensure_ascii=False)

    def save(self, transcript: Transcript) -> Path:
        """Save transcript to JSON file.

        Args:
            transcript: Transcript to save.

        Returns:
            Path to the saved file.

        Raises:
            StorageError: If saving fails.
        """
        file_path = self.base_dir / f"{transcript.id}.json"

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(transcript.to_json())
        except Exception as e:
            raise StorageError(f"Failed to save transcript: {e}") from e

        # Update index
        index = self._read_index()
        index[transcript.id] = {
            "id": transcript.id,
            "url": transcript.url,
            "title": transcript.title,
            "duration": transcript.duration,
            "created_at": transcript.created_at.isoformat(),
            "file": file_path.name,
        }
        self._write_index(index)

        return file_path

    def load(self, transcript_id: str) -> Transcript:
        """Load transcript by ID.

        Args:
            transcript_id: Transcript ID to load.

        Returns:
            Loaded Transcript.

        Raises:
            StorageError: If loading fails or transcript not found.
        """
        file_path = self.base_dir / f"{transcript_id}.json"

        if not file_path.exists():
            raise StorageError(f"Transcript not found: {transcript_id}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return Transcript.from_json(f.read())
        except Exception as e:
            raise StorageError(f"Failed to load transcript: {e}") from e

    def exists(self, transcript_id: str) -> bool:
        """Check if transcript exists.

        Args:
            transcript_id: Transcript ID to check.

        Returns:
            True if transcript exists.
        """
        file_path = self.base_dir / f"{transcript_id}.json"
        return file_path.exists()

    def find_by_url(self, url: str) -> Transcript | None:
        """Find transcript by URL.

        Args:
            url: YouTube URL to search for.

        Returns:
            Transcript if found, None otherwise.
        """
        index = self._read_index()
        for entry in index.values():
            if entry.get("url") == url:
                return self.load(entry["id"])
        return None

    def list_all(self) -> list[dict]:
        """List all saved transcripts.

        Returns:
            List of transcript metadata from index.
        """
        index = self._read_index()
        return sorted(
            index.values(),
            key=lambda x: x.get("created_at", ""),
            reverse=True,
        )

    def delete(self, transcript_id: str) -> None:
        """Delete transcript.

        Args:
            transcript_id: Transcript ID to delete.

        Raises:
            StorageError: If deletion fails.
        """
        file_path = self.base_dir / f"{transcript_id}.json"

        if file_path.exists():
            file_path.unlink()

        # Update index
        index = self._read_index()
        if transcript_id in index:
            del index[transcript_id]
            self._write_index(index)

    def export_to_txt(self, transcript_id: str, output_path: Path) -> Path:
        """Export transcript to plain text file.

        Args:
            transcript_id: Transcript ID to export.
            output_path: Path for output file.

        Returns:
            Path to exported file.
        """
        transcript = self.load(transcript_id)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(transcript.to_plain_text())

        return output_path

    def export_to_json(self, transcript_id: str, output_path: Path) -> Path:
        """Export transcript to JSON file.

        Args:
            transcript_id: Transcript ID to export.
            output_path: Path for output file.

        Returns:
            Path to exported file.
        """
        transcript = self.load(transcript_id)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(transcript.to_json())

        return output_path
