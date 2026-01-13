#!/usr/bin/env python3
"""CLI for Research Video Dataset Scraper.

Commands:
    video     - Process a single video
    playlist  - Process videos from a playlist
    channel   - Process videos from a channel
    stats     - Show dataset statistics
    list      - List processed videos
"""

from __future__ import annotations

# SSL workaround for Fedora and other distros with strict OpenSSL 3.x configuration
# This MUST be done before importing ssl or any module that uses ssl (like urllib3, yt-dlp)
# See: https://github.com/yt-dlp/yt-dlp/issues/10128
import os
from pathlib import Path as _Path

def _apply_fedora_ssl_workaround() -> None:
    """Apply SSL workaround for Fedora's strict OpenSSL configuration.

    On Fedora 37+ (and other distributions with OpenSSL 3.x and strict
    crypto-policies), the system OpenSSL configuration can cause SSL errors
    like 'SSLError: unknown error (_ssl.c:3123)' when connecting to some
    HTTPS servers.

    This workaround sets OPENSSL_CONF=/dev/null to bypass the system's
    crypto-policies. This is safe because:
    1. It only affects this process, not the system
    2. SSL still works, just without the extra restrictions
    3. Certificate verification is still enabled by default
    """
    # Detect if we're on Fedora or similar
    is_fedora = False
    try:
        if _Path("/etc/fedora-release").exists():
            is_fedora = True
        else:
            os_release = _Path("/etc/os-release")
            if os_release.exists() and "Fedora" in os_release.read_text():
                is_fedora = True
    except (OSError, PermissionError):
        pass

    if is_fedora:
        # Only set if not already explicitly configured
        if os.environ.get("OPENSSL_CONF") in (None, ""):
            os.environ["OPENSSL_CONF"] = "/dev/null"

# Apply before any ssl-related imports
_apply_fedora_ssl_workaround()

import asyncio
import logging
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from scrappah.downloader import DownloadOptions
from scrappah.pipeline import DatasetPipeline, PipelineOptions

app = typer.Typer(
    name="scrappah",
    help="Video dataset toolkit - download, extract frames, and transcribe.",
    add_completion=False,
)
console = Console()


def setup_logging(verbose: bool = False) -> None:
    """Configure logging with rich handler."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )


OutputDir = Annotated[
    Path,
    typer.Option(
        "--output-dir", "-o",
        help="Output directory for dataset",
        file_okay=False,
        resolve_path=True,
    ),
]

FPS = Annotated[
    float,
    typer.Option(
        "--fps", "-f",
        help="Frames per second to extract",
        min=0.1,
        max=60.0,
    ),
]

NoFrames = Annotated[
    bool,
    typer.Option(
        "--no-frames",
        help="Skip frame extraction",
    ),
]

NoTranscribe = Annotated[
    bool,
    typer.Option(
        "--no-transcribe",
        help="Skip transcription",
    ),
]

WhisperModel = Annotated[
    str,
    typer.Option(
        "--whisper-model", "-w",
        help="Whisper model size (tiny, base, small, medium, large)",
    ),
]

MaxVideos = Annotated[
    Optional[int],
    typer.Option(
        "--max-videos", "-m",
        help="Maximum number of videos to process",
        min=1,
    ),
]

MaxConcurrent = Annotated[
    int,
    typer.Option(
        "--concurrent", "-c",
        help="Maximum concurrent downloads",
        min=1,
        max=10,
    ),
]

Verbose = Annotated[
    bool,
    typer.Option(
        "--verbose", "-v",
        help="Enable verbose output",
    ),
]

SkipExisting = Annotated[
    bool,
    typer.Option(
        "--skip-existing/--no-skip-existing",
        help="Skip already processed videos",
    ),
]

MaxHeight = Annotated[
    Optional[int],
    typer.Option(
        "--max-height",
        help="Maximum video height (e.g., 720, 1080)",
    ),
]

NoCheckCertificate = Annotated[
    bool,
    typer.Option(
        "--no-check-certificate",
        help="Disable SSL certificate verification (use only if experiencing SSL errors)",
    ),
]


def create_pipeline_options(
    output_dir: Path,
    fps: float,
    no_frames: bool,
    no_transcribe: bool,
    whisper_model: str,
    max_concurrent: int,
    max_height: Optional[int] = None,
    no_check_certificate: bool = False,
) -> PipelineOptions:
    """Create pipeline options from CLI arguments."""
    download_opts = DownloadOptions()
    if max_height:
        download_opts.max_height = max_height
    if no_check_certificate:
        download_opts.no_check_certificate = True

    return PipelineOptions(
        output_dir=output_dir,
        fps=fps,
        extract_frames=not no_frames,
        transcribe=not no_transcribe,
        whisper_model=whisper_model,
        max_concurrent=max_concurrent,
        download_options=download_opts,
    )


@app.command()
def video(
    url: Annotated[str, typer.Argument(help="Video URL to process")],
    output_dir: OutputDir = Path("dataset"),
    fps: FPS = 1.0,
    no_frames: NoFrames = False,
    no_transcribe: NoTranscribe = False,
    whisper_model: WhisperModel = "base",
    max_height: MaxHeight = None,
    verbose: Verbose = False,
    skip_existing: SkipExisting = True,
    no_check_certificate: NoCheckCertificate = False,
) -> None:
    """Process a single video: download, extract frames, and transcribe."""
    setup_logging(verbose)

    options = create_pipeline_options(
        output_dir, fps, no_frames, no_transcribe, whisper_model, 1, max_height,
        no_check_certificate,
    )

    async def run():
        async with DatasetPipeline(options) as pipeline:
            result = await pipeline.process_video(url, skip_existing=skip_existing)

            if result.success:
                console.print(f"\n[green]Successfully processed:[/] {result.title}")
                console.print(f"  Video ID: {result.video_id}")
                if result.video_path:
                    console.print(f"  Video: {result.video_path}")
                if result.frames_dir:
                    console.print(f"  Frames: {result.frames_dir} ({result.frame_count} frames)")
                if result.transcript_path:
                    console.print(f"  Transcript: {result.transcript_path}")
                console.print(f"  Processing time: {result.processing_time:.1f}s")
            else:
                console.print(f"\n[red]Failed to process video:[/] {result.error}")
                raise typer.Exit(1)

    asyncio.run(run())


@app.command()
def playlist(
    url: Annotated[str, typer.Argument(help="Playlist URL to process")],
    output_dir: OutputDir = Path("dataset"),
    fps: FPS = 1.0,
    no_frames: NoFrames = False,
    no_transcribe: NoTranscribe = False,
    whisper_model: WhisperModel = "base",
    max_videos: MaxVideos = None,
    max_concurrent: MaxConcurrent = 2,
    max_height: MaxHeight = None,
    verbose: Verbose = False,
    skip_existing: SkipExisting = True,
    no_check_certificate: NoCheckCertificate = False,
) -> None:
    """Process videos from a playlist."""
    setup_logging(verbose)

    options = create_pipeline_options(
        output_dir, fps, no_frames, no_transcribe, whisper_model, max_concurrent, max_height,
        no_check_certificate,
    )

    async def run():
        async with DatasetPipeline(options) as pipeline:
            results = await pipeline.process_playlist(
                url, max_videos=max_videos, skip_existing=skip_existing
            )

            successful = [r for r in results if r.success]
            failed = [r for r in results if not r.success]

            console.print(f"\n[bold]Processing complete[/]")
            console.print(f"  [green]Successful:[/] {len(successful)}")
            console.print(f"  [red]Failed:[/] {len(failed)}")

            if failed:
                console.print("\n[yellow]Failed videos:[/]")
                for r in failed:
                    console.print(f"  - {r.video_id}: {r.error}")

    asyncio.run(run())


@app.command()
def channel(
    url: Annotated[str, typer.Argument(help="Channel URL to process")],
    output_dir: OutputDir = Path("dataset"),
    fps: FPS = 1.0,
    no_frames: NoFrames = False,
    no_transcribe: NoTranscribe = False,
    whisper_model: WhisperModel = "base",
    max_videos: MaxVideos = None,
    max_concurrent: MaxConcurrent = 2,
    max_height: MaxHeight = None,
    verbose: Verbose = False,
    skip_existing: SkipExisting = True,
    no_check_certificate: NoCheckCertificate = False,
) -> None:
    """Process videos from a channel."""
    setup_logging(verbose)

    options = create_pipeline_options(
        output_dir, fps, no_frames, no_transcribe, whisper_model, max_concurrent, max_height,
        no_check_certificate,
    )

    async def run():
        async with DatasetPipeline(options) as pipeline:
            results = await pipeline.process_channel(
                url, max_videos=max_videos, skip_existing=skip_existing
            )

            successful = [r for r in results if r.success]
            failed = [r for r in results if not r.success]

            console.print(f"\n[bold]Processing complete[/]")
            console.print(f"  [green]Successful:[/] {len(successful)}")
            console.print(f"  [red]Failed:[/] {len(failed)}")

    asyncio.run(run())


@app.command()
def stats(
    output_dir: OutputDir = Path("dataset"),
) -> None:
    """Show dataset statistics."""
    async def run():
        async with DatasetPipeline(PipelineOptions(output_dir=output_dir)) as pipeline:
            stats_data = await pipeline.get_stats()

            table = Table(title="Dataset Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Total Videos", str(stats_data["total_videos"]))
            table.add_row("Total Frames", str(stats_data["total_frames"]))

            duration = stats_data["total_duration_seconds"]
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            seconds = int(duration % 60)
            table.add_row("Total Duration", f"{hours}h {minutes}m {seconds}s")

            avg_duration = stats_data["avg_duration_seconds"]
            table.add_row("Avg Duration", f"{avg_duration:.1f}s")

            table.add_row("Storage Used", stats_data["storage_human"])

            if stats_data["first_download"]:
                table.add_row("First Download", stats_data["first_download"][:19])
            if stats_data["last_download"]:
                table.add_row("Last Download", stats_data["last_download"][:19])

            console.print(table)

    asyncio.run(run())


@app.command("list")
def list_videos(
    output_dir: OutputDir = Path("dataset"),
    limit: Annotated[int, typer.Option("--limit", "-n", help="Number of videos to show")] = 20,
) -> None:
    """List processed videos in the dataset."""
    async def run():
        async with DatasetPipeline(PipelineOptions(output_dir=output_dir)) as pipeline:
            videos = await pipeline.storage.list_videos(limit=limit)

            if not videos:
                console.print("[yellow]No videos in dataset[/]")
                return

            table = Table(title=f"Videos (showing {len(videos)})")
            table.add_column("ID", style="cyan", max_width=15)
            table.add_column("Title", style="white", max_width=40)
            table.add_column("Duration", style="green")
            table.add_column("Frames", style="yellow")
            table.add_column("Downloaded", style="dim")

            for video in videos:
                duration = f"{video.duration:.0f}s" if video.duration else "N/A"
                downloaded = video.downloaded_at.strftime("%Y-%m-%d %H:%M")
                table.add_row(
                    video.id[:15],
                    video.title[:40] + ("..." if len(video.title) > 40 else ""),
                    duration,
                    str(video.frame_count),
                    downloaded,
                )

            console.print(table)

    asyncio.run(run())


@app.command()
def search(
    query: Annotated[str, typer.Argument(help="Search query")],
    output_dir: OutputDir = Path("dataset"),
    limit: Annotated[int, typer.Option("--limit", "-n")] = 20,
) -> None:
    """Search videos by title."""
    async def run():
        async with DatasetPipeline(PipelineOptions(output_dir=output_dir)) as pipeline:
            videos = await pipeline.storage.search_videos(query, limit=limit)

            if not videos:
                console.print(f"[yellow]No videos matching '{query}'[/]")
                return

            table = Table(title=f"Search results for '{query}'")
            table.add_column("ID", style="cyan", max_width=15)
            table.add_column("Title", style="white", max_width=50)
            table.add_column("Duration", style="green")

            for video in videos:
                duration = f"{video.duration:.0f}s" if video.duration else "N/A"
                table.add_row(video.id[:15], video.title[:50], duration)

            console.print(table)

    asyncio.run(run())


@app.command()
def delete(
    video_id: Annotated[str, typer.Argument(help="Video ID to delete")],
    output_dir: OutputDir = Path("dataset"),
    keep_files: Annotated[bool, typer.Option("--keep-files", help="Keep video files")] = False,
) -> None:
    """Delete a video from the dataset."""
    async def run():
        async with DatasetPipeline(PipelineOptions(output_dir=output_dir)) as pipeline:
            deleted = await pipeline.storage.delete_video(video_id, delete_files=not keep_files)

            if deleted:
                console.print(f"[green]Deleted video:[/] {video_id}")
            else:
                console.print(f"[red]Video not found:[/] {video_id}")
                raise typer.Exit(1)

    asyncio.run(run())


@app.command()
def batch(
    urls_file: Annotated[
        Path,
        typer.Argument(help="File containing URLs (one per line)"),
    ],
    output_dir: OutputDir = Path("dataset"),
    fps: FPS = 1.0,
    no_frames: NoFrames = False,
    no_transcribe: NoTranscribe = False,
    whisper_model: WhisperModel = "base",
    max_concurrent: MaxConcurrent = 2,
    max_height: MaxHeight = None,
    verbose: Verbose = False,
    skip_existing: SkipExisting = True,
    resume: Annotated[bool, typer.Option("--resume", "-r", help="Resume interrupted batch")] = False,
    no_check_certificate: NoCheckCertificate = False,
) -> None:
    """Process videos from a file containing URLs."""
    setup_logging(verbose)

    if not urls_file.exists():
        console.print(f"[red]File not found:[/] {urls_file}")
        raise typer.Exit(1)

    # Read URLs from file
    urls = []
    with open(urls_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)

    if not urls:
        console.print("[yellow]No URLs found in file[/]")
        return

    console.print(f"[cyan]Found {len(urls)} URLs in file[/]")

    options = create_pipeline_options(
        output_dir, fps, no_frames, no_transcribe, whisper_model, max_concurrent, max_height,
        no_check_certificate,
    )

    async def run():
        async with DatasetPipeline(options) as pipeline:
            if resume:
                results = await pipeline.resume_batch(urls)
            else:
                results = await pipeline.process_batch(urls, skip_existing=skip_existing)

            successful = [r for r in results if r.success]
            failed = [r for r in results if not r.success]

            console.print(f"\n[bold]Batch processing complete[/]")
            console.print(f"  [green]Successful:[/] {len(successful)}")
            console.print(f"  [red]Failed:[/] {len(failed)}")

            if failed:
                console.print("\n[yellow]Failed videos:[/]")
                for r in failed:
                    console.print(f"  - {r.video_id}: {r.error}")

    asyncio.run(run())


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
