"""Domain models."""

from video_to_text.models.transcript import Segment, Transcript
from video_to_text.models.job import Job, JobStatus

__all__ = ["Segment", "Transcript", "Job", "JobStatus"]
