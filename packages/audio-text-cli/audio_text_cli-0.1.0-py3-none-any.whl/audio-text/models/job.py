"""Job model for tracking transcription progress."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Self


class JobStatus(Enum):
    """Status of a transcription job."""

    PENDING = "pending"
    DOWNLOADING = "downloading"
    CHUNKING = "chunking"
    TRANSCRIBING = "transcribing"
    MERGING = "merging"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Job:
    """Represents a transcription job."""

    id: str
    url: str
    status: JobStatus = JobStatus.PENDING
    progress: float = 0.0  # 0.0 to 1.0
    current_chunk: int = 0
    total_chunks: int = 0
    error_message: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def update_status(self, status: JobStatus, progress: float | None = None) -> None:
        """Update job status and optionally progress."""
        self.status = status
        if progress is not None:
            self.progress = progress
        self.updated_at = datetime.now()

    def update_chunk_progress(self, current: int, total: int) -> None:
        """Update chunk processing progress."""
        self.current_chunk = current
        self.total_chunks = total
        self.progress = current / total if total > 0 else 0.0
        self.updated_at = datetime.now()

    def mark_failed(self, error: str) -> None:
        """Mark job as failed with error message."""
        self.status = JobStatus.FAILED
        self.error_message = error
        self.updated_at = datetime.now()

    def mark_completed(self) -> None:
        """Mark job as completed."""
        self.status = JobStatus.COMPLETED
        self.progress = 1.0
        self.updated_at = datetime.now()

    @property
    def is_finished(self) -> bool:
        """Check if job is in a terminal state."""
        return self.status in (JobStatus.COMPLETED, JobStatus.FAILED)

    @property
    def progress_percent(self) -> int:
        """Get progress as percentage."""
        return int(self.progress * 100)

    def to_dict(self) -> dict:
        """Convert job to dictionary."""
        return {
            "id": self.id,
            "url": self.url,
            "status": self.status.value,
            "progress": self.progress,
            "current_chunk": self.current_chunk,
            "total_chunks": self.total_chunks,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create job from dictionary."""
        return cls(
            id=data["id"],
            url=data["url"],
            status=JobStatus(data["status"]),
            progress=data["progress"],
            current_chunk=data["current_chunk"],
            total_chunks=data["total_chunks"],
            error_message=data.get("error_message"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
