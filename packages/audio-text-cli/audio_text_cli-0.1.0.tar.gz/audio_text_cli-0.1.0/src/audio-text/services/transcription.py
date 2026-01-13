"""Transcription service - orchestrates the full transcription pipeline."""

from pathlib import Path
from typing import Callable

from video_to_text.core.chunker import AudioChunk, Chunker
from video_to_text.core.downloader import Downloader, DownloadResult
from video_to_text.core.merger import Merger
from video_to_text.core.storage import Storage
from video_to_text.core.transcriber import Transcriber, TranscriptionResult
from video_to_text.models import Job, JobStatus, Transcript


class TranscriptionServiceError(Exception):
    """Raised when transcription service fails."""

    pass


class TranscriptionService:
    """Orchestrates the complete transcription workflow."""

    def __init__(
        self,
        storage_dir: Path,
        model_name: str = "small",
        chunk_duration_minutes: int = 5,
    ):
        """Initialize transcription service.

        Args:
            storage_dir: Directory for storing transcripts.
            model_name: Whisper model to use.
            chunk_duration_minutes: Duration of audio chunks.
        """
        self.storage = Storage(storage_dir)
        self.downloader = Downloader()
        self.chunker = Chunker(chunk_duration_minutes=chunk_duration_minutes)
        self.transcriber = Transcriber(model_name=model_name)
        self.merger = Merger()
        self.model_name = model_name

    def transcribe(
        self,
        url: str,
        progress_callback: Callable[[Job], None] | None = None,
        force: bool = False,
    ) -> Transcript:
        """Transcribe a YouTube video.

        Args:
            url: YouTube video URL.
            progress_callback: Optional callback for progress updates.
            force: If True, re-transcribe even if cached.

        Returns:
            Transcript object.

        Raises:
            TranscriptionServiceError: If transcription fails.
        """
        # Check cache first (unless force is True)
        if not force:
            cached = self.storage.find_by_url(url)
            if cached:
                return cached

        # Create job for tracking
        job = Job(id="", url=url)

        try:
            # Step 1: Download audio
            job.update_status(JobStatus.DOWNLOADING)
            self._notify(progress_callback, job)

            download_result = self.downloader.download(url)
            job.id = download_result.video_id

            # Step 2: Chunk audio
            job.update_status(JobStatus.CHUNKING)
            self._notify(progress_callback, job)

            chunks = self.chunker.chunk(download_result.audio_path)
            job.total_chunks = len(chunks)

            # Step 3: Transcribe each chunk
            job.update_status(JobStatus.TRANSCRIBING)
            self._notify(progress_callback, job)

            chunk_results = self._transcribe_chunks(chunks, job, progress_callback)

            # Step 4: Merge results
            job.update_status(JobStatus.MERGING)
            self._notify(progress_callback, job)

            merged_segments = self.merger.merge(chunks, chunk_results)

            # Create transcript
            transcript = Transcript(
                id=download_result.video_id,
                url=url,
                title=download_result.title,
                duration=download_result.duration,
                segments=merged_segments,
                model=self.model_name,
            )

            # Step 5: Save transcript
            self.storage.save(transcript)

            # Cleanup temp files
            self._cleanup(download_result, chunks)

            job.mark_completed()
            self._notify(progress_callback, job)

            return transcript

        except Exception as e:
            job.mark_failed(str(e))
            self._notify(progress_callback, job)
            raise TranscriptionServiceError(f"Transcription failed: {e}") from e

    def _transcribe_chunks(
        self,
        chunks: list[AudioChunk],
        job: Job,
        progress_callback: Callable[[Job], None] | None,
    ) -> list[TranscriptionResult]:
        """Transcribe all chunks sequentially."""
        results: list[TranscriptionResult] = []

        for i, chunk in enumerate(chunks):
            job.update_chunk_progress(i + 1, len(chunks))
            self._notify(progress_callback, job)

            result = self.transcriber.transcribe(
                audio_path=chunk.path,
                time_offset=chunk.start_time,
            )
            results.append(result)

        return results

    def _cleanup(
        self,
        download_result: DownloadResult,
        chunks: list[AudioChunk],
    ) -> None:
        """Clean up temporary files."""
        self.downloader.cleanup(download_result.video_id)
        self.chunker.cleanup(chunks)

    def _notify(
        self,
        callback: Callable[[Job], None] | None,
        job: Job,
    ) -> None:
        """Notify progress callback if provided."""
        if callback:
            callback(job)

    def get_transcript(self, transcript_id: str) -> Transcript:
        """Get a saved transcript by ID."""
        return self.storage.load(transcript_id)

    def list_transcripts(self) -> list[dict]:
        """List all saved transcripts."""
        return self.storage.list_all()

    def delete_transcript(self, transcript_id: str) -> None:
        """Delete a saved transcript."""
        self.storage.delete(transcript_id)

    def export_transcript(
        self,
        transcript_id: str,
        output_path: Path,
        format: str = "json",
    ) -> Path:
        """Export transcript to file.

        Args:
            transcript_id: ID of transcript to export.
            output_path: Path for output file.
            format: Export format ('json' or 'txt').

        Returns:
            Path to exported file.
        """
        if format == "txt":
            return self.storage.export_to_txt(transcript_id, output_path)
        return self.storage.export_to_json(transcript_id, output_path)

    def transcript_exists(self, url: str) -> bool:
        """Check if a transcript exists for URL."""
        return self.storage.find_by_url(url) is not None
