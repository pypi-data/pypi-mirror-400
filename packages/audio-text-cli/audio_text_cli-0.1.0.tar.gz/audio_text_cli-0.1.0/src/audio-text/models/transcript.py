"""Transcript and Segment models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
import json


@dataclass
class Segment:
    """A single segment of transcribed text with timing information."""

    text: str
    start_time: float  # seconds
    end_time: float  # seconds

    def to_dict(self) -> dict:
        """Convert segment to dictionary."""
        return {
            "text": self.text,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create segment from dictionary."""
        return cls(
            text=data["text"],
            start_time=data["start_time"],
            end_time=data["end_time"],
        )

    def format_timestamp(self, seconds: float) -> str:
        """Format seconds to HH:MM:SS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"

    def to_display_string(self) -> str:
        """Format segment for CLI display."""
        start = self.format_timestamp(self.start_time)
        end = self.format_timestamp(self.end_time)
        return f"[{start} -> {end}] {self.text}"


@dataclass
class Transcript:
    """Complete transcript of a video."""

    id: str
    url: str
    title: str
    duration: float  # total duration in seconds
    segments: list[Segment] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    model: str = "small"  # Whisper model used

    @property
    def full_text(self) -> str:
        """Get complete transcript as plain text."""
        return " ".join(segment.text for segment in self.segments)

    @property
    def total_segments(self) -> int:
        """Get total number of segments."""
        return len(self.segments)

    def to_dict(self) -> dict:
        """Convert transcript to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "duration": self.duration,
            "segments": [segment.to_dict() for segment in self.segments],
            "created_at": self.created_at.isoformat(),
            "model": self.model,
            "full_text": self.full_text,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create transcript from dictionary."""
        return cls(
            id=data["id"],
            url=data["url"],
            title=data["title"],
            duration=data["duration"],
            segments=[Segment.from_dict(s) for s in data["segments"]],
            created_at=datetime.fromisoformat(data["created_at"]),
            model=data.get("model", "small"),
        )

    def to_json(self, indent: int = 2) -> str:
        """Serialize transcript to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Deserialize transcript from JSON string."""
        return cls.from_dict(json.loads(json_str))

    def to_plain_text(self) -> str:
        """Export transcript as plain text with timestamps."""
        lines = [
            f"Title: {self.title}",
            f"URL: {self.url}",
            f"Duration: {self._format_duration()}",
            f"Transcribed: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "=" * 50,
            "",
        ]
        for segment in self.segments:
            lines.append(segment.to_display_string())
        return "\n".join(lines)

    def _format_duration(self) -> str:
        """Format duration in human readable format."""
        minutes = int(self.duration // 60)
        seconds = int(self.duration % 60)
        return f"{minutes}m {seconds}s"
