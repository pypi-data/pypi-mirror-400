"""Pydantic data models for the video scraper pipeline.

This module defines all data structures used throughout the pipeline,
including video metadata, transcription results, and configuration options.
"""

from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    NonNegativeFloat,
    NonNegativeInt,
    PositiveFloat,
    PositiveInt,
    field_validator,
    model_validator,
)


class VideoFormat(StrEnum):
    """Supported video formats for download."""

    MP4 = "mp4"
    WEBM = "webm"
    MKV = "mkv"
    BEST = "best"


class ImageFormat(StrEnum):
    """Supported image formats for frame extraction."""

    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"


class WhisperModel(StrEnum):
    """Available Whisper model sizes."""

    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    LARGE_V2 = "large-v2"
    LARGE_V3 = "large-v3"
    TURBO = "turbo"


class VideoMetadata(BaseModel):
    """Metadata extracted from a video source.

    Attributes:
        id: Unique identifier for the video (platform-specific).
        title: Video title.
        description: Video description or None if unavailable.
        duration: Video duration in seconds.
        upload_date: Date the video was uploaded.
        uploader: Name or ID of the uploader.
        view_count: Number of views or None if unavailable.
        resolution: Video resolution as "WIDTHxHEIGHT" string.
        fps: Frames per second of the video.
    """

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    id: str = Field(..., min_length=1, description="Unique video identifier")
    title: str = Field(..., min_length=1, description="Video title")
    description: str | None = Field(default=None, description="Video description")
    duration: PositiveFloat = Field(..., description="Duration in seconds")
    upload_date: datetime = Field(..., description="Upload date")
    uploader: str = Field(..., min_length=1, description="Uploader name or ID")
    view_count: NonNegativeInt | None = Field(default=None, description="View count")
    resolution: str = Field(..., pattern=r"^\d+x\d+$", description="Resolution WxH")
    fps: PositiveFloat = Field(..., le=240, description="Frames per second")

    @property
    def width(self) -> int:
        """Extract width from resolution string."""
        return int(self.resolution.split("x")[0])

    @property
    def height(self) -> int:
        """Extract height from resolution string."""
        return int(self.resolution.split("x")[1])


class TranscriptSegment(BaseModel):
    """A single segment of transcribed audio with timestamps.

    Attributes:
        start: Start time in seconds.
        end: End time in seconds.
        text: Transcribed text for this segment.
    """

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    start: NonNegativeFloat = Field(..., description="Start time in seconds")
    end: NonNegativeFloat = Field(..., description="End time in seconds")
    text: str = Field(..., description="Transcribed text")

    @model_validator(mode="after")
    def validate_time_range(self) -> Self:
        """Ensure end time is after start time."""
        if self.end < self.start:
            raise ValueError(
                f"End time ({self.end}) must be >= start time ({self.start})"
            )
        return self


class TranscriptResult(BaseModel):
    """Complete transcription result with segments and metadata.

    Attributes:
        text: Full transcribed text.
        segments: List of timestamped transcript segments.
        language: Detected or specified language code.
        duration: Total audio duration in seconds.
    """

    model_config = ConfigDict(frozen=True)

    text: str = Field(..., description="Full transcribed text")
    segments: tuple[TranscriptSegment, ...] = Field(
        default_factory=tuple, description="Timestamped segments"
    )
    language: str = Field(..., min_length=2, max_length=10, description="Language code")
    duration: NonNegativeFloat = Field(..., description="Total duration in seconds")

    @field_validator("segments", mode="before")
    @classmethod
    def convert_segments_to_tuple(
        cls, v: list[TranscriptSegment] | tuple[TranscriptSegment, ...]
    ) -> tuple[TranscriptSegment, ...]:
        """Convert list of segments to immutable tuple."""
        if isinstance(v, list):
            return tuple(v)
        return v


class DownloadOptions(BaseModel):
    """Configuration options for video downloading.

    Attributes:
        max_resolution: Maximum resolution to download (e.g., 1080).
        format: Preferred video format.
        rate_limit: Download rate limit in bytes/second or None for unlimited.
        skip_existing: Whether to skip already downloaded files.
    """

    model_config = ConfigDict(frozen=True)

    max_resolution: PositiveInt = Field(
        default=1080, le=8192, description="Maximum resolution height"
    )
    format: VideoFormat = Field(default=VideoFormat.MP4, description="Video format")
    rate_limit: PositiveInt | None = Field(
        default=None, description="Rate limit in bytes/sec"
    )
    skip_existing: bool = Field(
        default=True, description="Skip existing downloaded files"
    )


class ExtractionOptions(BaseModel):
    """Configuration options for frame extraction.

    Attributes:
        fps: Target frames per second for extraction.
        max_frames: Maximum number of frames to extract or None for unlimited.
        quality: JPEG quality (1-100) for output images.
        output_format: Image format for extracted frames.
    """

    model_config = ConfigDict(frozen=True)

    fps: PositiveFloat = Field(default=1.0, le=60, description="Extraction FPS")
    max_frames: PositiveInt | None = Field(
        default=None, description="Maximum frames to extract"
    )
    quality: Annotated[int, Field(ge=1, le=100)] = Field(
        default=85, description="JPEG quality 1-100"
    )
    output_format: ImageFormat = Field(
        default=ImageFormat.JPEG, description="Output image format"
    )


class TranscriptionOptions(BaseModel):
    """Configuration options for audio transcription.

    Attributes:
        model: Whisper model size to use.
        language: Language code for transcription or None for auto-detection.
    """

    model_config = ConfigDict(frozen=True)

    model: WhisperModel = Field(default=WhisperModel.BASE, description="Whisper model")
    language: str | None = Field(
        default=None, min_length=2, max_length=10, description="Language code or None"
    )


class PipelineConfig(BaseModel):
    """Complete pipeline configuration combining all options.

    Attributes:
        download: Download configuration options.
        extraction: Frame extraction options.
        transcription: Transcription options.
        output_dir: Base output directory for all pipeline artifacts.
        num_workers: Number of parallel workers for processing.
    """

    model_config = ConfigDict(frozen=True)

    download: DownloadOptions = Field(
        default_factory=DownloadOptions, description="Download options"
    )
    extraction: ExtractionOptions = Field(
        default_factory=ExtractionOptions, description="Extraction options"
    )
    transcription: TranscriptionOptions = Field(
        default_factory=TranscriptionOptions, description="Transcription options"
    )
    output_dir: Path = Field(
        default=Path("output"), description="Base output directory"
    )
    num_workers: PositiveInt = Field(
        default=4, le=32, description="Number of parallel workers"
    )

    @field_validator("output_dir", mode="before")
    @classmethod
    def convert_to_path(cls, v: str | Path) -> Path:
        """Convert string paths to Path objects."""
        return Path(v) if isinstance(v, str) else v


class ProcessedVideo(BaseModel):
    """Result of processing a single video through the pipeline.

    Attributes:
        metadata: Extracted video metadata.
        paths: Dictionary mapping artifact types to file paths.
        frame_count: Number of frames extracted.
        processed_at: Timestamp when processing completed.
    """

    model_config = ConfigDict(frozen=True)

    metadata: VideoMetadata = Field(..., description="Video metadata")
    paths: dict[str, Path] = Field(
        default_factory=dict, description="Artifact paths by type"
    )
    frame_count: NonNegativeInt = Field(default=0, description="Extracted frame count")
    processed_at: datetime = Field(
        default_factory=datetime.now, description="Processing timestamp"
    )

    @field_validator("paths", mode="before")
    @classmethod
    def convert_paths(cls, v: dict[str, str | Path]) -> dict[str, Path]:
        """Convert all path values to Path objects."""
        return {k: Path(p) if isinstance(p, str) else p for k, p in v.items()}
