"""Synchronous convenience wrappers for scrappah.

These functions wrap the async API for users who prefer synchronous code.
Perfect for scripts, notebooks, and simple use cases.

Example:
    >>> from scrappah import download_video
    >>> result = download_video("https://youtube.com/watch?v=...")
    >>> print(f"Downloaded: {result.title}")
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from scrappah.pipeline import DatasetPipeline, PipelineOptions, ProcessedVideo


def download_video(
    url: str,
    output_dir: str | Path = "dataset",
    fps: float = 1.0,
    extract_frames: bool = True,
    transcribe: bool = True,
    whisper_model: str = "base",
    skip_existing: bool = True,
    **options: Any,
) -> ProcessedVideo:
    """Download and process a single video (synchronous).

    This is a convenience wrapper around the async API for simple use cases.

    Args:
        url: Video URL to process (YouTube, Vimeo, etc.)
        output_dir: Directory to save the dataset
        fps: Frames per second to extract (default: 1.0)
        extract_frames: Whether to extract video frames (default: True)
        transcribe: Whether to transcribe audio (default: True)
        whisper_model: Whisper model size (default: "base")
        skip_existing: Skip if already processed (default: True)
        **options: Additional PipelineOptions parameters

    Returns:
        ProcessedVideo with paths to video, frames, and transcript

    Example:
        >>> result = download_video(
        ...     "https://youtube.com/watch?v=dQw4w9WgXcQ",
        ...     output_dir="./my_dataset",
        ...     fps=0.5,
        ...     whisper_model="small",
        ... )
        >>> print(result.title)
        >>> print(result.frame_count)
    """

    async def _run() -> ProcessedVideo:
        opts = PipelineOptions(
            output_dir=output_dir,
            fps=fps,
            extract_frames=extract_frames,
            transcribe=transcribe,
            whisper_model=whisper_model,
            **options,
        )
        async with DatasetPipeline(opts) as pipeline:
            return await pipeline.process_video(url, skip_existing=skip_existing)

    return asyncio.run(_run())


def download_playlist(
    url: str,
    output_dir: str | Path = "dataset",
    max_videos: int | None = None,
    fps: float = 1.0,
    extract_frames: bool = True,
    transcribe: bool = True,
    whisper_model: str = "base",
    max_concurrent: int = 2,
    skip_existing: bool = True,
    **options: Any,
) -> list[ProcessedVideo]:
    """Download and process videos from a playlist (synchronous).

    Args:
        url: Playlist URL
        output_dir: Directory to save the dataset
        max_videos: Maximum videos to process (None for all)
        fps: Frames per second to extract
        extract_frames: Whether to extract video frames
        transcribe: Whether to transcribe audio
        whisper_model: Whisper model size
        max_concurrent: Maximum concurrent downloads
        skip_existing: Skip already processed videos
        **options: Additional PipelineOptions parameters

    Returns:
        List of ProcessedVideo results

    Example:
        >>> results = download_playlist(
        ...     "https://youtube.com/playlist?list=...",
        ...     max_videos=10,
        ...     fps=0.5,
        ... )
        >>> successful = [r for r in results if r.success]
        >>> print(f"Downloaded {len(successful)} videos")
    """

    async def _run() -> list[ProcessedVideo]:
        opts = PipelineOptions(
            output_dir=output_dir,
            fps=fps,
            extract_frames=extract_frames,
            transcribe=transcribe,
            whisper_model=whisper_model,
            max_concurrent=max_concurrent,
            **options,
        )
        async with DatasetPipeline(opts) as pipeline:
            return await pipeline.process_playlist(
                url, max_videos=max_videos, skip_existing=skip_existing
            )

    return asyncio.run(_run())


def download_channel(
    url: str,
    output_dir: str | Path = "dataset",
    max_videos: int | None = None,
    fps: float = 1.0,
    extract_frames: bool = True,
    transcribe: bool = True,
    whisper_model: str = "base",
    max_concurrent: int = 2,
    skip_existing: bool = True,
    **options: Any,
) -> list[ProcessedVideo]:
    """Download and process videos from a channel (synchronous).

    Args:
        url: Channel URL
        output_dir: Directory to save the dataset
        max_videos: Maximum videos to process (None for all)
        fps: Frames per second to extract
        extract_frames: Whether to extract video frames
        transcribe: Whether to transcribe audio
        whisper_model: Whisper model size
        max_concurrent: Maximum concurrent downloads
        skip_existing: Skip already processed videos
        **options: Additional PipelineOptions parameters

    Returns:
        List of ProcessedVideo results
    """

    async def _run() -> list[ProcessedVideo]:
        opts = PipelineOptions(
            output_dir=output_dir,
            fps=fps,
            extract_frames=extract_frames,
            transcribe=transcribe,
            whisper_model=whisper_model,
            max_concurrent=max_concurrent,
            **options,
        )
        async with DatasetPipeline(opts) as pipeline:
            return await pipeline.process_channel(
                url, max_videos=max_videos, skip_existing=skip_existing
            )

    return asyncio.run(_run())


def download_batch(
    urls: list[str],
    output_dir: str | Path = "dataset",
    fps: float = 1.0,
    extract_frames: bool = True,
    transcribe: bool = True,
    whisper_model: str = "base",
    max_concurrent: int = 2,
    skip_existing: bool = True,
    **options: Any,
) -> list[ProcessedVideo]:
    """Download and process multiple videos (synchronous).

    Args:
        urls: List of video URLs to process
        output_dir: Directory to save the dataset
        fps: Frames per second to extract
        extract_frames: Whether to extract video frames
        transcribe: Whether to transcribe audio
        whisper_model: Whisper model size
        max_concurrent: Maximum concurrent downloads
        skip_existing: Skip already processed videos
        **options: Additional PipelineOptions parameters

    Returns:
        List of ProcessedVideo results
    """

    async def _run() -> list[ProcessedVideo]:
        opts = PipelineOptions(
            output_dir=output_dir,
            fps=fps,
            extract_frames=extract_frames,
            transcribe=transcribe,
            whisper_model=whisper_model,
            max_concurrent=max_concurrent,
            **options,
        )
        async with DatasetPipeline(opts) as pipeline:
            return await pipeline.process_batch(urls, skip_existing=skip_existing)

    return asyncio.run(_run())
