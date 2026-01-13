"""Scrappah - Video dataset toolkit for research.

A Python library for downloading videos, extracting frames, and transcribing
audio from online video sources. Designed for ML researchers building datasets.

Example:
    >>> import asyncio
    >>> from scrappah import DatasetPipeline, PipelineOptions
    >>>
    >>> async def main():
    ...     options = PipelineOptions(output_dir="./dataset")
    ...     async with DatasetPipeline(options) as pipeline:
    ...         result = await pipeline.process_video("https://youtube.com/...")
    ...         print(f"Processed: {result.title}")
    >>>
    >>> asyncio.run(main())

For synchronous usage:
    >>> from scrappah import download_video
    >>> result = download_video("https://youtube.com/...", output_dir="./dataset")
"""

from scrappah.__version__ import __version__

# Core Pipeline
from scrappah.pipeline import (
    DatasetPipeline,
    PipelineOptions,
    ProcessedVideo,
)

# Downloading
from scrappah.downloader import (
    VideoDownloader,
    VideoMetadata,
    DownloadOptions,
    DownloadError,
)

# Storage
from scrappah.storage import (
    DatasetStorage,
    VideoRecord,
)

# Synchronous convenience functions
from scrappah.sync import (
    download_video,
    download_playlist,
    download_channel,
    download_batch,
)

# Models
from scrappah.models import (
    VideoFormat,
    ImageFormat,
    WhisperModel,
    ExtractionOptions,
    TranscriptionOptions,
    TranscriptResult,
    TranscriptSegment,
)

# Frame extraction (lazy imports to handle optional dependencies)
from scrappah.extractor import (
    extract_frames,
    extract_keyframes,
    get_available_backend,
    ExtractionError,
    NoBackendError,
)

# Transcription (lazy imports to handle optional dependencies)
from scrappah.transcriber import (
    Transcriber,
    transcribe_file,
    is_whisper_available,
    TranscriptionError,
    ModelNotLoadedError,
    WhisperNotAvailableError,
)

__all__ = [
    # Version
    "__version__",
    # Pipeline
    "DatasetPipeline",
    "PipelineOptions",
    "ProcessedVideo",
    # Downloading
    "VideoDownloader",
    "VideoMetadata",
    "DownloadOptions",
    "DownloadError",
    # Storage
    "DatasetStorage",
    "VideoRecord",
    # Sync convenience functions
    "download_video",
    "download_playlist",
    "download_channel",
    "download_batch",
    # Models
    "VideoFormat",
    "ImageFormat",
    "WhisperModel",
    "ExtractionOptions",
    "TranscriptionOptions",
    "TranscriptResult",
    "TranscriptSegment",
    # Frame extraction
    "extract_frames",
    "extract_keyframes",
    "get_available_backend",
    "ExtractionError",
    "NoBackendError",
    # Transcription
    "Transcriber",
    "transcribe_file",
    "is_whisper_available",
    "TranscriptionError",
    "ModelNotLoadedError",
    "WhisperNotAvailableError",
]
