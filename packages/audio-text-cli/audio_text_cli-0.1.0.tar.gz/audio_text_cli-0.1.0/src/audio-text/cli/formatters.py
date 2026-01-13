"""CLI output formatters."""

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.text import Text

from video_to_text.models import Job, JobStatus, Transcript


console = Console()


def format_transcript_display(transcript: Transcript, show_timestamps: bool = True) -> None:
    """Display transcript in CLI with rich formatting.

    Args:
        transcript: Transcript to display.
        show_timestamps: Whether to show timestamps for each segment.
    """
    # Header
    header = Table.grid(padding=1)
    header.add_column(style="bold cyan", justify="right")
    header.add_column(style="white")

    header.add_row("Title:", transcript.title)
    header.add_row("URL:", transcript.url)
    header.add_row("Duration:", _format_duration(transcript.duration))
    header.add_row("Segments:", str(transcript.total_segments))
    header.add_row("Model:", transcript.model)

    console.print(Panel(header, title="[bold]Transcript Info", border_style="blue"))
    console.print()

    # Segments
    if show_timestamps:
        for segment in transcript.segments:
            timestamp = Text(
                f"[{_format_time(segment.start_time)} → {_format_time(segment.end_time)}]",
                style="dim cyan",
            )
            console.print(timestamp, end=" ")
            console.print(segment.text)
    else:
        console.print(transcript.full_text)


def format_transcript_list(transcripts: list[dict]) -> None:
    """Display list of transcripts as a table.

    Args:
        transcripts: List of transcript metadata dictionaries.
    """
    if not transcripts:
        console.print("[yellow]No transcripts found.[/yellow]")
        return

    table = Table(title="Saved Transcripts", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="white", max_width=40)
    table.add_column("Duration", style="green", justify="right")
    table.add_column("Created", style="dim")

    for t in transcripts:
        duration = _format_duration(t.get("duration", 0))
        created = t.get("created_at", "")[:10]  # Just date part
        title = t.get("title", "Unknown")
        if len(title) > 37:
            title = title[:37] + "..."

        table.add_row(
            t.get("id", ""),
            title,
            duration,
            created,
        )

    console.print(table)


def format_job_progress(job: Job) -> str:
    """Format job progress for display.

    Args:
        job: Job to format.

    Returns:
        Formatted progress string.
    """
    status_icons = {
        JobStatus.PENDING: "⏳",
        JobStatus.DOWNLOADING: "⬇️ ",
        JobStatus.CHUNKING: "✂️ ",
        JobStatus.TRANSCRIBING: "🎤",
        JobStatus.MERGING: "🔗",
        JobStatus.COMPLETED: "✅",
        JobStatus.FAILED: "❌",
    }

    status_text = {
        JobStatus.PENDING: "Pending",
        JobStatus.DOWNLOADING: "Downloading audio",
        JobStatus.CHUNKING: "Splitting audio",
        JobStatus.TRANSCRIBING: f"Transcribing ({job.current_chunk}/{job.total_chunks})",
        JobStatus.MERGING: "Merging results",
        JobStatus.COMPLETED: "Completed",
        JobStatus.FAILED: f"Failed: {job.error_message}",
    }

    icon = status_icons.get(job.status, "")
    text = status_text.get(job.status, job.status.value)

    return f"{icon} {text}"


def create_progress_display() -> Progress:
    """Create a rich progress display for transcription."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    )


def print_success(message: str) -> None:
    """Print success message."""
    console.print(f"[bold green]✓[/bold green] {message}")


def print_error(message: str) -> None:
    """Print error message."""
    console.print(f"[bold red]✗[/bold red] {message}")


def print_warning(message: str) -> None:
    """Print warning message."""
    console.print(f"[bold yellow]![/bold yellow] {message}")


def print_info(message: str) -> None:
    """Print info message."""
    console.print(f"[bold blue]ℹ[/bold blue] {message}")


def _format_duration(seconds: float) -> str:
    """Format duration in human readable format."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    if minutes >= 60:
        hours = minutes // 60
        minutes = minutes % 60
        return f"{hours}h {minutes}m {secs}s"
    return f"{minutes}m {secs}s"


def _format_time(seconds: float) -> str:
    """Format time as MM:SS or HH:MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"
