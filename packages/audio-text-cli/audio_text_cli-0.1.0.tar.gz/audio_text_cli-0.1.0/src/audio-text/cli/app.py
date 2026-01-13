"""CLI application using Click with interactive menu."""

import re
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

from video_to_text import __version__
from video_to_text.cli.formatters import (
    console,
    format_job_progress,
    format_transcript_display,
    format_transcript_list,
    print_error,
    print_info,
    print_success,
    print_warning,
)
from video_to_text.models import Job
from video_to_text.services.transcription import TranscriptionService, TranscriptionServiceError
from video_to_text.utils.validators import validate_youtube_url, ValidationError


DEFAULT_OUTPUT_DIR = Path.home() / ".audio-text" / "transcripts"


def slugify(text: str, max_length: int = 50) -> str:
    """Convert text to a safe filename slug."""
    # Remove special characters, keep alphanumeric and spaces
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace spaces with underscores
    text = re.sub(r'[\s]+', '_', text)
    # Remove consecutive underscores
    text = re.sub(r'_+', '_', text)
    # Trim and lowercase
    text = text.strip('_').lower()
    # Limit length
    return text[:max_length]


def show_welcome() -> None:
    """Display welcome banner."""
    banner = """
 ╔═╗┬ ┬┌┬┐┬┌─┐  ╔╦╗┌─┐─┐ ┬┌┬┐
 ╠═╣│ │ ││││ │   ║ ├┤ ┌┴┬┘ │
 ╩ ╩└─┘─┴┘┴└─┘   ╩ └─┘┴ └─ ┴
    """
    console.print(Panel(
        f"[bold cyan]{banner}[/bold cyan]\n"
        f"[dim]YouTube Video Transcription for IELTS Practice[/dim]\n"
        f"[dim]Version {__version__}[/dim]",
        border_style="blue",
    ))


def show_menu() -> str:
    """Display main menu and get user choice."""
    console.print()
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Option", style="bold cyan")
    table.add_column("Description")

    table.add_row("[1]", "Transcribe a YouTube video")
    table.add_row("[2]", "List saved transcripts")
    table.add_row("[3]", "View a transcript")
    table.add_row("[4]", "Export transcript to file")
    table.add_row("[5]", "Delete a transcript")
    table.add_row("[q]", "Quit")

    console.print(table)
    console.print()

    return Prompt.ask(
        "[bold]Select an option[/bold]",
        choices=["1", "2", "3", "4", "5", "q"],
        default="1"
    )


def interactive_transcribe() -> None:
    """Interactive transcription workflow."""
    console.print()
    console.print("[bold]Transcribe YouTube Video[/bold]", style="cyan")
    console.print()

    # Get URL
    url = Prompt.ask("Enter YouTube URL")

    # Validate URL
    try:
        validated_url = validate_youtube_url(url)
    except ValidationError as e:
        print_error(f"Invalid URL: {e}")
        return

    # Get output directory
    use_default = Confirm.ask(
        f"Save to default location? ({DEFAULT_OUTPUT_DIR})",
        default=True
    )

    if use_default:
        output_dir = DEFAULT_OUTPUT_DIR
    else:
        output_path = Prompt.ask("Enter output directory")
        output_dir = Path(output_path)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Create service
    service = TranscriptionService(storage_dir=output_dir)

    # Check for cached transcript
    force = False
    if service.transcript_exists(validated_url):
        print_info("Found cached transcript.")
        force = Confirm.ask("Re-transcribe anyway?", default=False)
        if not force:
            # Load and display cached transcript
            cached = service.storage.find_by_url(validated_url)
            if cached:
                console.print()
                format_transcript_display(cached)

                # Offer to export
                if Confirm.ask("Export to text file?", default=False):
                    _export_transcript(service, cached, output_dir)
                return

    # Progress callback
    last_status = [None]

    def progress_callback(job: Job) -> None:
        if job.status != last_status[0]:
            console.print(format_job_progress(job))
            last_status[0] = job.status

    # Transcribe
    console.print()
    print_info(f"Starting transcription: {validated_url}")
    console.print()

    try:
        transcript = service.transcribe(
            url=validated_url,
            progress_callback=progress_callback,
            force=force,
        )
    except TranscriptionServiceError as e:
        print_error(str(e))
        return

    console.print()
    print_success(f"Transcription complete!")
    print_info(f"Saved to: {output_dir / f'{transcript.id}.json'}")
    console.print()

    # Display transcript
    format_transcript_display(transcript)

    # Offer to export
    console.print()
    if Confirm.ask("Export to text file?", default=True):
        _export_transcript(service, transcript, output_dir)


def _export_transcript(service: TranscriptionService, transcript, output_dir: Path) -> None:
    """Export transcript to file with title-based filename."""
    # Generate filename from title
    filename_base = slugify(transcript.title)
    if not filename_base:
        filename_base = transcript.id

    # Ask for format
    export_format = Prompt.ask(
        "Export format",
        choices=["txt", "json"],
        default="txt"
    )

    # Generate full path
    export_path = output_dir / f"{filename_base}.{export_format}"

    # Check if file exists
    counter = 1
    while export_path.exists():
        export_path = output_dir / f"{filename_base}_{counter}.{export_format}"
        counter += 1

    try:
        service.export_transcript(transcript.id, export_path, export_format)
        print_success(f"Exported to: {export_path}")
    except Exception as e:
        print_error(f"Failed to export: {e}")


def interactive_list() -> None:
    """Interactive list transcripts."""
    console.print()
    console.print("[bold]Saved Transcripts[/bold]", style="cyan")
    console.print()

    # Get output directory
    use_default = Confirm.ask(
        f"Use default location? ({DEFAULT_OUTPUT_DIR})",
        default=True
    )

    if use_default:
        output_dir = DEFAULT_OUTPUT_DIR
    else:
        output_path = Prompt.ask("Enter transcripts directory")
        output_dir = Path(output_path)

    if not output_dir.exists():
        print_warning("No transcripts directory found.")
        return

    service = TranscriptionService(storage_dir=output_dir)
    transcripts = service.list_transcripts()

    format_transcript_list(transcripts)


def interactive_view() -> None:
    """Interactive view transcript."""
    console.print()
    console.print("[bold]View Transcript[/bold]", style="cyan")
    console.print()

    output_dir = DEFAULT_OUTPUT_DIR

    if not output_dir.exists():
        print_warning("No transcripts found. Transcribe a video first.")
        return

    service = TranscriptionService(storage_dir=output_dir)
    transcripts = service.list_transcripts()

    if not transcripts:
        print_warning("No transcripts found.")
        return

    # Show available transcripts
    format_transcript_list(transcripts)
    console.print()

    # Get transcript ID
    transcript_id = Prompt.ask("Enter transcript ID to view")

    try:
        transcript = service.get_transcript(transcript_id)
    except Exception as e:
        print_error(f"Failed to load transcript: {e}")
        return

    console.print()

    # Ask for timestamp preference
    show_timestamps = Confirm.ask("Show timestamps?", default=True)

    format_transcript_display(transcript, show_timestamps=show_timestamps)


def interactive_export() -> None:
    """Interactive export transcript."""
    console.print()
    console.print("[bold]Export Transcript[/bold]", style="cyan")
    console.print()

    output_dir = DEFAULT_OUTPUT_DIR

    if not output_dir.exists():
        print_warning("No transcripts found. Transcribe a video first.")
        return

    service = TranscriptionService(storage_dir=output_dir)
    transcripts = service.list_transcripts()

    if not transcripts:
        print_warning("No transcripts found.")
        return

    # Show available transcripts
    format_transcript_list(transcripts)
    console.print()

    # Get transcript ID
    transcript_id = Prompt.ask("Enter transcript ID to export")

    try:
        transcript = service.get_transcript(transcript_id)
    except Exception as e:
        print_error(f"Failed to load transcript: {e}")
        return

    _export_transcript(service, transcript, output_dir)


def interactive_delete() -> None:
    """Interactive delete transcript."""
    console.print()
    console.print("[bold]Delete Transcript[/bold]", style="cyan")
    console.print()

    output_dir = DEFAULT_OUTPUT_DIR

    if not output_dir.exists():
        print_warning("No transcripts found.")
        return

    service = TranscriptionService(storage_dir=output_dir)
    transcripts = service.list_transcripts()

    if not transcripts:
        print_warning("No transcripts found.")
        return

    # Show available transcripts
    format_transcript_list(transcripts)
    console.print()

    # Get transcript ID
    transcript_id = Prompt.ask("Enter transcript ID to delete")

    # Confirm deletion
    if not Confirm.ask(f"Are you sure you want to delete '{transcript_id}'?", default=False):
        print_info("Cancelled.")
        return

    try:
        service.delete_transcript(transcript_id)
        print_success(f"Deleted transcript: {transcript_id}")
    except Exception as e:
        print_error(f"Failed to delete: {e}")


def run_interactive() -> None:
    """Run interactive mode."""
    show_welcome()

    while True:
        choice = show_menu()

        if choice == "1":
            interactive_transcribe()
        elif choice == "2":
            interactive_list()
        elif choice == "3":
            interactive_view()
        elif choice == "4":
            interactive_export()
        elif choice == "5":
            interactive_delete()
        elif choice == "q":
            console.print()
            console.print("[dim]Goodbye![/dim]")
            break

        console.print()
        if choice != "q":
            if not Confirm.ask("Continue?", default=True):
                console.print("[dim]Goodbye![/dim]")
                break


# Click CLI for direct command usage
@click.group(invoke_without_command=True)
@click.version_option(version=__version__, package_name="audio-text")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Audio Text - Transcribe YouTube videos for IELTS practice.

    Run without arguments for interactive mode, or use commands directly.
    """
    if ctx.invoked_subcommand is None:
        run_interactive()


@cli.command()
@click.argument("url")
@click.option(
    "--output", "-o",
    type=click.Path(),
    default=None,
    help="Output directory for transcripts.",
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Force re-transcription even if cached.",
)
@click.option(
    "--no-timestamps",
    is_flag=True,
    default=False,
    help="Display transcript without timestamps.",
)
def transcribe(
    url: str,
    output: Optional[str],
    force: bool,
    no_timestamps: bool,
) -> None:
    """Transcribe a YouTube video.

    URL: YouTube video URL to transcribe.
    """
    # Validate URL
    try:
        validated_url = validate_youtube_url(url)
    except ValidationError as e:
        print_error(f"Invalid URL: {e}")
        raise SystemExit(1)

    # Setup output directory
    output_dir = Path(output) if output else DEFAULT_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create service
    service = TranscriptionService(storage_dir=output_dir)

    # Check for cached transcript
    if not force and service.transcript_exists(validated_url):
        print_info("Found cached transcript. Use --force to re-transcribe.")

    # Progress callback
    last_status = [None]

    def progress_callback(job: Job) -> None:
        if job.status != last_status[0]:
            console.print(format_job_progress(job))
            last_status[0] = job.status

    # Transcribe
    print_info(f"Starting transcription: {validated_url}")
    console.print()

    try:
        transcript = service.transcribe(
            url=validated_url,
            progress_callback=progress_callback,
            force=force,
        )
    except TranscriptionServiceError as e:
        print_error(str(e))
        raise SystemExit(1)

    console.print()
    print_success(f"Transcription complete! Saved to: {output_dir / f'{transcript.id}.json'}")
    console.print()

    # Display transcript
    format_transcript_display(transcript, show_timestamps=not no_timestamps)


@cli.command("list")
@click.option(
    "--output", "-o",
    type=click.Path(),
    default=None,
    help="Directory containing transcripts.",
)
def list_transcripts(output: Optional[str]) -> None:
    """List all saved transcripts."""
    output_dir = Path(output) if output else DEFAULT_OUTPUT_DIR

    if not output_dir.exists():
        print_warning("No transcripts directory found.")
        return

    service = TranscriptionService(storage_dir=output_dir)
    transcripts = service.list_transcripts()

    format_transcript_list(transcripts)


@cli.command()
@click.argument("transcript_id")
@click.option(
    "--output", "-o",
    type=click.Path(),
    default=None,
    help="Directory containing transcripts.",
)
@click.option(
    "--no-timestamps",
    is_flag=True,
    default=False,
    help="Display without timestamps.",
)
def view(transcript_id: str, output: Optional[str], no_timestamps: bool) -> None:
    """View a saved transcript.

    TRANSCRIPT_ID: ID of the transcript to view.
    """
    output_dir = Path(output) if output else DEFAULT_OUTPUT_DIR

    if not output_dir.exists():
        print_error("Transcripts directory not found.")
        raise SystemExit(1)

    service = TranscriptionService(storage_dir=output_dir)

    try:
        transcript = service.get_transcript(transcript_id)
    except Exception as e:
        print_error(f"Failed to load transcript: {e}")
        raise SystemExit(1)

    format_transcript_display(transcript, show_timestamps=not no_timestamps)


@cli.command()
@click.argument("transcript_id")
@click.argument("destination", type=click.Path(), required=False)
@click.option(
    "--output", "-o",
    type=click.Path(),
    default=None,
    help="Directory containing transcripts.",
)
@click.option(
    "--format", "-f",
    type=click.Choice(["json", "txt"]),
    default="txt",
    help="Export format (default: txt).",
)
def export(
    transcript_id: str,
    destination: Optional[str],
    output: Optional[str],
    format: str,
) -> None:
    """Export a transcript to file.

    TRANSCRIPT_ID: ID of the transcript to export.
    DESTINATION: Output file path (optional, auto-generated from title if not provided).
    """
    output_dir = Path(output) if output else DEFAULT_OUTPUT_DIR

    if not output_dir.exists():
        print_error("Transcripts directory not found.")
        raise SystemExit(1)

    service = TranscriptionService(storage_dir=output_dir)

    try:
        transcript = service.get_transcript(transcript_id)
    except Exception as e:
        print_error(f"Failed to load transcript: {e}")
        raise SystemExit(1)

    # Generate filename from title if not provided
    if destination:
        dest_path = Path(destination)
        if not dest_path.suffix:
            dest_path = dest_path.with_suffix(f".{format}")
    else:
        filename_base = slugify(transcript.title)
        if not filename_base:
            filename_base = transcript_id
        dest_path = output_dir / f"{filename_base}.{format}"

        # Avoid overwriting
        counter = 1
        while dest_path.exists():
            dest_path = output_dir / f"{filename_base}_{counter}.{format}"
            counter += 1

    try:
        exported_path = service.export_transcript(transcript_id, dest_path, format)
        print_success(f"Exported to: {exported_path}")
    except Exception as e:
        print_error(f"Failed to export: {e}")
        raise SystemExit(1)


@cli.command()
@click.argument("transcript_id")
@click.option(
    "--output", "-o",
    type=click.Path(),
    default=None,
    help="Directory containing transcripts.",
)
@click.confirmation_option(prompt="Are you sure you want to delete this transcript?")
def delete(transcript_id: str, output: Optional[str]) -> None:
    """Delete a saved transcript.

    TRANSCRIPT_ID: ID of the transcript to delete.
    """
    output_dir = Path(output) if output else DEFAULT_OUTPUT_DIR

    if not output_dir.exists():
        print_error("Transcripts directory not found.")
        raise SystemExit(1)

    service = TranscriptionService(storage_dir=output_dir)

    try:
        service.delete_transcript(transcript_id)
        print_success(f"Deleted transcript: {transcript_id}")
    except Exception as e:
        print_error(f"Failed to delete: {e}")
        raise SystemExit(1)


def main() -> None:
    """Main entry point."""
    cli()
