"""Main orchestration pipeline for video dataset processing."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from scrappah.downloader import DownloadError, DownloadOptions, VideoDownloader, VideoMetadata
from scrappah.storage import DatasetStorage, VideoRecord

logger = logging.getLogger(__name__)
console = Console()


@dataclass
class PipelineOptions:
    """Configuration options for the processing pipeline."""

    output_dir: str | Path = "dataset"
    fps: float = 1.0  # Frames per second to extract
    extract_frames: bool = True
    transcribe: bool = True
    whisper_model: str = "base"
    max_concurrent: int = 2
    download_options: DownloadOptions = field(default_factory=DownloadOptions)


@dataclass
class ProcessedVideo:
    """Result of processing a single video."""

    video_id: str
    title: str
    success: bool
    video_path: Path | None = None
    frames_dir: Path | None = None
    transcript_path: Path | None = None
    frame_count: int = 0
    duration: float | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0


ProgressCallback = Callable[[str, str, float], None]


class DatasetPipeline:
    """Orchestrates video downloading, frame extraction, and transcription.

    Features:
    - Async processing with configurable concurrency
    - Progress reporting with rich
    - Resume support for interrupted batches
    - Comprehensive error handling
    - Storage integration for tracking processed videos
    """

    def __init__(self, options: PipelineOptions | None = None):
        """Initialize pipeline with options.

        Args:
            options: Pipeline configuration
        """
        self.options = options or PipelineOptions()
        self.storage = DatasetStorage(self.options.output_dir)
        self.downloader = VideoDownloader(self.options.download_options)
        self._semaphore: asyncio.Semaphore | None = None
        self._whisper_model: Any = None
        self._progress: Progress | None = None
        self._task_ids: dict[str, TaskID] = {}

    async def initialize(self) -> None:
        """Initialize storage and load models."""
        await self.storage.init_db()
        self._semaphore = asyncio.Semaphore(self.options.max_concurrent)

        if self.options.transcribe:
            await self._load_whisper_model()

    async def close(self) -> None:
        """Clean up resources."""
        await self.storage.close()

    async def _load_whisper_model(self) -> None:
        """Load Whisper model for transcription."""
        import whisper

        loop = asyncio.get_event_loop()
        logger.info(f"Loading Whisper model: {self.options.whisper_model}")
        self._whisper_model = await loop.run_in_executor(
            None, whisper.load_model, self.options.whisper_model
        )
        logger.info("Whisper model loaded successfully")

    async def process_video(
        self,
        url: str,
        skip_existing: bool = True,
        progress_callback: ProgressCallback | None = None,
    ) -> ProcessedVideo:
        """Process a single video: download, extract frames, transcribe.

        Args:
            url: Video URL to process
            skip_existing: Skip if already processed
            progress_callback: Optional callback for progress updates

        Returns:
            ProcessedVideo with results
        """
        start_time = asyncio.get_event_loop().time()
        video_id = self.downloader.extract_video_id(url)

        try:
            # Check if already processed
            if skip_existing and video_id:
                existing = await self.storage.get_video(video_id)
                if existing and existing.video_path:
                    logger.info(f"Skipping already processed video: {video_id}")
                    return ProcessedVideo(
                        video_id=existing.id,
                        title=existing.title,
                        success=True,
                        video_path=Path(existing.video_path) if existing.video_path else None,
                        frames_dir=Path(existing.frames_dir) if existing.frames_dir else None,
                        transcript_path=Path(existing.transcript_path) if existing.transcript_path else None,
                        frame_count=existing.frame_count,
                        duration=existing.duration,
                        metadata=existing.metadata,
                    )

            # Download video
            if progress_callback:
                progress_callback(video_id or url, "Downloading", 0.0)

            metadata = await self.downloader.download_video(
                url, self.storage.videos_dir, skip_existing=skip_existing
            )

            video_id = metadata.id
            video_path = metadata.file_path

            if not video_path or not video_path.exists():
                raise DownloadError(f"Video file not found after download: {video_id}")

            result = ProcessedVideo(
                video_id=video_id,
                title=metadata.title,
                success=True,
                video_path=video_path,
                duration=metadata.duration,
                metadata=metadata.to_dict(),
            )

            # Extract frames
            if self.options.extract_frames:
                if progress_callback:
                    progress_callback(video_id, "Extracting frames", 33.0)

                frames_dir, frame_count = await self._extract_frames(video_path, video_id)
                result.frames_dir = frames_dir
                result.frame_count = frame_count

            # Transcribe
            if self.options.transcribe:
                if progress_callback:
                    progress_callback(video_id, "Transcribing", 66.0)

                transcript_path = await self._transcribe_video(video_path, video_id)
                result.transcript_path = transcript_path

            # Save to database
            record = VideoRecord(
                id=video_id,
                title=metadata.title,
                duration=metadata.duration,
                video_path=str(video_path) if video_path else None,
                frames_dir=str(result.frames_dir) if result.frames_dir else None,
                transcript_path=str(result.transcript_path) if result.transcript_path else None,
                frame_count=result.frame_count,
                metadata=result.metadata,
                downloaded_at=datetime.utcnow(),
            )
            await self.storage.add_video(record)

            if progress_callback:
                progress_callback(video_id, "Complete", 100.0)

            end_time = asyncio.get_event_loop().time()
            result.processing_time = end_time - start_time

            logger.info(f"Successfully processed video: {video_id} - {metadata.title}")
            return result

        except Exception as e:
            logger.error(f"Failed to process video {url}: {e}")
            end_time = asyncio.get_event_loop().time()
            return ProcessedVideo(
                video_id=video_id or url,
                title="Unknown",
                success=False,
                error=str(e),
                processing_time=end_time - start_time,
            )

    async def _extract_frames(self, video_path: Path, video_id: str) -> tuple[Path, int]:
        """Extract frames from video at specified FPS.

        Args:
            video_path: Path to video file
            video_id: Video identifier

        Returns:
            Tuple of (frames directory, frame count)
        """
        frames_dir = self.storage.get_frames_path(video_id)
        frames_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Try decord first (faster, GPU-accelerated)
            frame_count = await self._extract_frames_decord(video_path, frames_dir)
            logger.info(f"Extracted {frame_count} frames using Decord to {frames_dir}")
        except ImportError:
            # Fall back to OpenCV (always available)
            logger.debug("Decord not available, using OpenCV for frame extraction")
            frame_count = await self._extract_frames_opencv(video_path, frames_dir)
            logger.info(f"Extracted {frame_count} frames using OpenCV to {frames_dir}")

        return frames_dir, frame_count

    async def _extract_frames_decord(self, video_path: Path, frames_dir: Path) -> int:
        """Extract frames using decord (GPU-accelerated when available)."""
        import decord
        from decord import VideoReader, cpu

        decord.bridge.set_bridge("native")

        loop = asyncio.get_event_loop()

        def extract():
            vr = VideoReader(str(video_path), ctx=cpu(0))
            total_frames = len(vr)
            video_fps = vr.get_avg_fps()

            # Calculate frame indices based on target FPS
            frame_interval = int(video_fps / self.options.fps)
            if frame_interval < 1:
                frame_interval = 1

            indices = list(range(0, total_frames, frame_interval))
            frames = vr.get_batch(indices).asnumpy()

            from PIL import Image

            for i, frame in enumerate(frames):
                # Save frame using PIL (frame is already RGB from decord)
                img = Image.fromarray(frame)
                frame_path = frames_dir / f"frame_{i:06d}.jpg"
                img.save(str(frame_path), quality=85)

            return len(indices)

        return await loop.run_in_executor(None, extract)

    async def _extract_frames_opencv(self, video_path: Path, frames_dir: Path) -> int:
        """Extract frames using OpenCV."""
        import cv2

        loop = asyncio.get_event_loop()

        def extract():
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                raise RuntimeError(f"Cannot open video: {video_path}")

            video_fps = cap.get(cv2.CAP_PROP_FPS)
            frame_interval = int(video_fps / self.options.fps)
            if frame_interval < 1:
                frame_interval = 1

            frame_count = 0
            saved_count = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % frame_interval == 0:
                    frame_path = frames_dir / f"frame_{saved_count:06d}.jpg"
                    cv2.imwrite(str(frame_path), frame)
                    saved_count += 1

                frame_count += 1

            cap.release()
            return saved_count

        return await loop.run_in_executor(None, extract)

    async def _transcribe_video(self, video_path: Path, video_id: str) -> Path | None:
        """Transcribe video audio using Whisper.

        Args:
            video_path: Path to video file
            video_id: Video identifier

        Returns:
            Path to transcript JSON file
        """
        if self._whisper_model is None:
            return None

        transcript_path = self.storage.get_transcript_path(video_id)

        try:
            import json

            loop = asyncio.get_event_loop()

            def transcribe():
                result = self._whisper_model.transcribe(str(video_path))
                return result

            result = await loop.run_in_executor(None, transcribe)

            # Save transcript
            transcript_data = {
                "text": result["text"],
                "segments": [
                    {
                        "id": seg["id"],
                        "start": seg["start"],
                        "end": seg["end"],
                        "text": seg["text"],
                    }
                    for seg in result.get("segments", [])
                ],
                "language": result.get("language", "unknown"),
            }

            with open(transcript_path, "w", encoding="utf-8") as f:
                json.dump(transcript_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Saved transcript to {transcript_path}")
            return transcript_path

        except Exception as e:
            logger.error(f"Transcription failed for {video_id}: {e}")
            return None

    async def process_batch(
        self,
        urls: list[str],
        skip_existing: bool = True,
        show_progress: bool = True,
    ) -> list[ProcessedVideo]:
        """Process multiple videos concurrently.

        Args:
            urls: List of video URLs
            skip_existing: Skip already processed videos
            show_progress: Show rich progress bar

        Returns:
            List of ProcessedVideo results
        """
        if not self._semaphore:
            await self.initialize()

        results: list[ProcessedVideo] = []

        async def process_with_semaphore(url: str, task_id: TaskID | None = None) -> ProcessedVideo:
            async with self._semaphore:  # type: ignore
                def progress_callback(vid: str, status: str, progress: float) -> None:
                    if self._progress and task_id is not None:
                        self._progress.update(task_id, description=f"[cyan]{vid[:20]}[/]: {status}")

                result = await self.process_video(
                    url,
                    skip_existing=skip_existing,
                    progress_callback=progress_callback if show_progress else None,
                )

                if self._progress and task_id is not None:
                    status = "[green]Done[/]" if result.success else "[red]Failed[/]"
                    self._progress.update(task_id, description=f"[cyan]{result.video_id[:20]}[/]: {status}", advance=1)

                return result

        if show_progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                MofNCompleteColumn(),
                TimeElapsedColumn(),
                TimeRemainingColumn(),
                console=console,
            ) as progress:
                self._progress = progress
                main_task = progress.add_task("[yellow]Processing videos...", total=len(urls))

                # Create tasks with their own progress tracking
                tasks = []
                for url in urls:
                    task_id = progress.add_task(f"[dim]Queued: {url[:30]}...[/]", total=1, visible=False)
                    tasks.append(process_with_semaphore(url, task_id))

                results = await asyncio.gather(*tasks, return_exceptions=False)
                self._progress = None
        else:
            tasks = [process_with_semaphore(url, None) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=False)

        # Summary
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        console.print(f"\n[green]Completed:[/] {successful} videos")
        if failed > 0:
            console.print(f"[red]Failed:[/] {failed} videos")

        return results

    async def process_playlist(
        self,
        playlist_url: str,
        max_videos: int | None = None,
        skip_existing: bool = True,
        show_progress: bool = True,
    ) -> list[ProcessedVideo]:
        """Process all videos from a playlist.

        Args:
            playlist_url: Playlist URL
            max_videos: Maximum videos to process
            skip_existing: Skip already processed videos
            show_progress: Show progress bar

        Returns:
            List of ProcessedVideo results
        """
        console.print(f"[yellow]Fetching playlist info...[/]")

        # Get playlist video URLs
        videos_info = await self.downloader.get_playlist_info(playlist_url)

        if not videos_info:
            console.print("[red]No videos found in playlist[/]")
            return []

        if max_videos:
            videos_info = videos_info[:max_videos]

        console.print(f"[green]Found {len(videos_info)} videos in playlist[/]")

        # Build URLs
        urls = []
        for info in videos_info:
            url = info.get("url") or info.get("webpage_url")
            if not url:
                video_id = info.get("id")
                if video_id:
                    url = f"https://www.youtube.com/watch?v={video_id}"
            if url:
                urls.append(url)

        return await self.process_batch(urls, skip_existing, show_progress)

    async def process_channel(
        self,
        channel_url: str,
        max_videos: int | None = None,
        skip_existing: bool = True,
        show_progress: bool = True,
    ) -> list[ProcessedVideo]:
        """Process videos from a channel.

        Args:
            channel_url: Channel URL
            max_videos: Maximum videos to process
            skip_existing: Skip already processed videos
            show_progress: Show progress bar

        Returns:
            List of ProcessedVideo results
        """
        # Channels are handled similarly to playlists
        return await self.process_playlist(
            channel_url, max_videos, skip_existing, show_progress
        )

    async def resume_batch(
        self,
        urls: list[str],
        show_progress: bool = True,
    ) -> list[ProcessedVideo]:
        """Resume processing a batch, skipping already completed videos.

        Args:
            urls: List of video URLs
            show_progress: Show progress bar

        Returns:
            List of ProcessedVideo results
        """
        # Filter out already processed videos
        pending_urls = []
        for url in urls:
            video_id = self.downloader.extract_video_id(url)
            if video_id:
                exists = await self.storage.video_exists(video_id)
                if not exists:
                    pending_urls.append(url)
            else:
                pending_urls.append(url)

        skipped = len(urls) - len(pending_urls)
        if skipped > 0:
            console.print(f"[yellow]Skipping {skipped} already processed videos[/]")

        if not pending_urls:
            console.print("[green]All videos already processed![/]")
            return []

        return await self.process_batch(pending_urls, skip_existing=True, show_progress=show_progress)

    async def get_stats(self) -> dict[str, Any]:
        """Get dataset statistics."""
        return await self.storage.get_stats()

    async def __aenter__(self) -> "DatasetPipeline":
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
