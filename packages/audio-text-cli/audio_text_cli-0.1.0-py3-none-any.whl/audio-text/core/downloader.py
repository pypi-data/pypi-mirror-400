"""YouTube audio downloader using yt-dlp."""

import hashlib
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import yt_dlp


@dataclass
class DownloadResult:
    """Result of a download operation."""

    audio_path: Path
    title: str
    duration: float  # seconds
    video_id: str


class DownloadError(Exception):
    """Raised when download fails."""

    pass


class Downloader:
    """Downloads audio from YouTube videos."""

    MAX_DURATION_SECONDS = 30 * 60  # 30 minutes

    def __init__(self, temp_dir: Path | None = None):
        """Initialize downloader.

        Args:
            temp_dir: Directory for temporary audio files.
                     Uses system temp if not specified.
        """
        self.temp_dir = temp_dir or Path(tempfile.gettempdir()) / "audio-text"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def download(
        self,
        url: str,
        progress_callback: Callable[[float], None] | None = None,
    ) -> DownloadResult:
        """Download audio from YouTube URL.

        Args:
            url: YouTube video URL.
            progress_callback: Optional callback for progress updates (0.0 to 1.0).

        Returns:
            DownloadResult with path to audio file and metadata.

        Raises:
            DownloadError: If download fails or video exceeds duration limit.
        """
        video_id = self._extract_video_id(url)
        output_path = self.temp_dir / f"{video_id}.wav"

        # First, get video info to check duration
        info = self._get_video_info(url)
        duration = info.get("duration", 0)

        if duration > self.MAX_DURATION_SECONDS:
            raise DownloadError(
                f"Video duration ({duration // 60}m) exceeds maximum "
                f"allowed ({self.MAX_DURATION_SECONDS // 60}m)"
            )

        # Download audio
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": str(self.temp_dir / f"{video_id}.%(ext)s"),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "192",
                }
            ],
            "quiet": True,
            "no_warnings": True,
            "progress_hooks": [self._make_progress_hook(progress_callback)]
            if progress_callback
            else [],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except yt_dlp.utils.DownloadError as e:
            raise DownloadError(f"Failed to download: {e}") from e

        if not output_path.exists():
            raise DownloadError(f"Download completed but audio file not found: {output_path}")

        return DownloadResult(
            audio_path=output_path,
            title=info.get("title", "Unknown"),
            duration=duration,
            video_id=video_id,
        )

    def _get_video_info(self, url: str) -> dict:
        """Get video metadata without downloading."""
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)
        except Exception as e:
            raise DownloadError(f"Failed to get video info: {e}") from e

    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from URL or generate hash."""
        # Try to extract from URL patterns
        ydl_opts = {"quiet": True, "no_warnings": True}

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get("id", self._hash_url(url))
        except Exception:
            return self._hash_url(url)

    def _hash_url(self, url: str) -> str:
        """Generate short hash from URL."""
        return hashlib.sha256(url.encode()).hexdigest()[:12]

    def _make_progress_hook(
        self, callback: Callable[[float], None]
    ) -> Callable[[dict], None]:
        """Create yt-dlp progress hook."""

        def hook(d: dict) -> None:
            if d["status"] == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                downloaded = d.get("downloaded_bytes", 0)
                if total > 0:
                    callback(downloaded / total)
            elif d["status"] == "finished":
                callback(1.0)

        return hook

    def cleanup(self, video_id: str) -> None:
        """Remove temporary audio file."""
        audio_path = self.temp_dir / f"{video_id}.wav"
        if audio_path.exists():
            audio_path.unlink()
