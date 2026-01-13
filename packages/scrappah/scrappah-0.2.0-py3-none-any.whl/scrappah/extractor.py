"""Frame extraction module using Decord with OpenCV fallback.

This module provides efficient video frame extraction using Decord
for speed, with automatic fallback to OpenCV when Decord is unavailable.
"""

import logging
from pathlib import Path
from typing import Protocol, runtime_checkable

import numpy as np
from numpy.typing import NDArray

from scrappah.models import ExtractionOptions, ImageFormat

logger = logging.getLogger(__name__)

# Attempt to import Decord, fall back to OpenCV
_DECORD_AVAILABLE = False
_OPENCV_AVAILABLE = False

try:
    import decord
    from decord import VideoReader, cpu

    decord.bridge.set_bridge("numpy")
    _DECORD_AVAILABLE = True
    logger.debug("Decord backend available")
except ImportError:
    logger.debug("Decord not available, will try OpenCV fallback")

try:
    import cv2

    _OPENCV_AVAILABLE = True
    logger.debug("OpenCV backend available")
except ImportError:
    logger.debug("OpenCV not available")


class ExtractionError(Exception):
    """Raised when frame extraction fails."""

    pass


class NoBackendError(ExtractionError):
    """Raised when no video backend is available."""

    pass


@runtime_checkable
class VideoBackend(Protocol):
    """Protocol for video reading backends."""

    def get_frame_count(self) -> int:
        """Return total number of frames in the video."""
        ...

    def get_fps(self) -> float:
        """Return the video's frames per second."""
        ...

    def get_frame(self, index: int) -> NDArray[np.uint8]:
        """Get a single frame by index as RGB array."""
        ...

    def get_batch(self, indices: list[int]) -> list[NDArray[np.uint8]]:
        """Get multiple frames by indices as RGB arrays."""
        ...

    def close(self) -> None:
        """Release video resources."""
        ...


class DecordBackend:
    """Video backend using Decord for efficient frame access."""

    def __init__(self, video_path: Path) -> None:
        """Initialize Decord video reader.

        Args:
            video_path: Path to the video file.

        Raises:
            ExtractionError: If the video cannot be opened.
        """
        if not _DECORD_AVAILABLE:
            raise NoBackendError("Decord is not installed")

        self._path = video_path
        try:
            self._reader = VideoReader(str(video_path), ctx=cpu(0))
        except Exception as e:
            raise ExtractionError(f"Failed to open video with Decord: {e}") from e

    def get_frame_count(self) -> int:
        """Return total number of frames in the video."""
        return len(self._reader)

    def get_fps(self) -> float:
        """Return the video's frames per second."""
        return float(self._reader.get_avg_fps())

    def get_frame(self, index: int) -> NDArray[np.uint8]:
        """Get a single frame by index as RGB array."""
        return self._reader[index].asnumpy()

    def get_batch(self, indices: list[int]) -> list[NDArray[np.uint8]]:
        """Get multiple frames by indices as RGB arrays."""
        frames = self._reader.get_batch(indices)
        return [frame.asnumpy() for frame in frames]

    def close(self) -> None:
        """Release video resources."""
        del self._reader


class OpenCVBackend:
    """Video backend using OpenCV as fallback."""

    def __init__(self, video_path: Path) -> None:
        """Initialize OpenCV video capture.

        Args:
            video_path: Path to the video file.

        Raises:
            ExtractionError: If the video cannot be opened.
        """
        if not _OPENCV_AVAILABLE:
            raise NoBackendError("OpenCV is not installed")

        self._path = video_path
        self._cap = cv2.VideoCapture(str(video_path))

        if not self._cap.isOpened():
            raise ExtractionError(f"Failed to open video with OpenCV: {video_path}")

        self._frame_count = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self._fps = self._cap.get(cv2.CAP_PROP_FPS)

    def get_frame_count(self) -> int:
        """Return total number of frames in the video."""
        return self._frame_count

    def get_fps(self) -> float:
        """Return the video's frames per second."""
        return self._fps

    def get_frame(self, index: int) -> NDArray[np.uint8]:
        """Get a single frame by index as RGB array."""
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, index)
        ret, frame = self._cap.read()

        if not ret:
            raise ExtractionError(f"Failed to read frame at index {index}")

        # Convert BGR to RGB
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def get_batch(self, indices: list[int]) -> list[NDArray[np.uint8]]:
        """Get multiple frames by indices as RGB arrays."""
        frames: list[NDArray[np.uint8]] = []
        sorted_indices = sorted(enumerate(indices), key=lambda x: x[1])

        for _, idx in sorted_indices:
            frames.append(self.get_frame(idx))

        # Reorder to match original indices order
        result: list[NDArray[np.uint8]] = [np.array([])] * len(indices)
        for i, (orig_idx, _) in enumerate(sorted_indices):
            result[orig_idx] = frames[i]

        return result

    def close(self) -> None:
        """Release video resources."""
        self._cap.release()


def _get_backend(video_path: Path) -> VideoBackend:
    """Get the best available video backend.

    Args:
        video_path: Path to the video file.

    Returns:
        A VideoBackend instance.

    Raises:
        NoBackendError: If no video backend is available.
    """
    if _DECORD_AVAILABLE:
        try:
            return DecordBackend(video_path)
        except ExtractionError:
            logger.warning("Decord failed, falling back to OpenCV")

    if _OPENCV_AVAILABLE:
        return OpenCVBackend(video_path)

    raise NoBackendError(
        "No video backend available. Install decord or opencv-python."
    )


def _save_frame(
    frame: NDArray[np.uint8],
    output_path: Path,
    output_format: ImageFormat,
    quality: int,
) -> None:
    """Save a frame to disk in the specified format.

    Args:
        frame: RGB frame array.
        output_path: Path to save the image.
        output_format: Image format to use.
        quality: Quality setting for lossy formats.
    """
    if not _OPENCV_AVAILABLE:
        raise NoBackendError("OpenCV required for saving frames")

    # Convert RGB to BGR for OpenCV
    bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    encode_params: list[int] = []
    match output_format:
        case ImageFormat.JPEG:
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
        case ImageFormat.PNG:
            # PNG compression level (0-9, where 9 is max compression)
            compression = max(0, min(9, (100 - quality) // 10))
            encode_params = [cv2.IMWRITE_PNG_COMPRESSION, compression]
        case ImageFormat.WEBP:
            encode_params = [cv2.IMWRITE_WEBP_QUALITY, quality]

    success = cv2.imwrite(str(output_path), bgr_frame, encode_params)
    if not success:
        raise ExtractionError(f"Failed to save frame to {output_path}")


def _calculate_frame_indices(
    total_frames: int,
    video_fps: float,
    target_fps: float,
    max_frames: int | None,
) -> list[int]:
    """Calculate which frame indices to extract.

    Args:
        total_frames: Total number of frames in the video.
        video_fps: Original video FPS.
        target_fps: Target extraction FPS.
        max_frames: Maximum frames to extract or None.

    Returns:
        List of frame indices to extract.
    """
    if target_fps >= video_fps:
        # Extract all frames if target FPS is higher than video FPS
        indices = list(range(total_frames))
    else:
        # Calculate frame interval based on target FPS
        interval = video_fps / target_fps
        indices = []
        current = 0.0

        while current < total_frames:
            indices.append(int(current))
            current += interval

    # Apply max_frames limit
    if max_frames is not None and len(indices) > max_frames:
        # Sample evenly from available indices
        step = len(indices) / max_frames
        indices = [indices[int(i * step)] for i in range(max_frames)]

    return indices


def extract_frames(
    video_path: Path,
    output_dir: Path,
    options: ExtractionOptions | None = None,
) -> int:
    """Extract frames from a video file.

    Args:
        video_path: Path to the input video file.
        output_dir: Directory to save extracted frames.
        options: Extraction configuration options.

    Returns:
        Number of frames extracted.

    Raises:
        ExtractionError: If extraction fails.
        FileNotFoundError: If video file does not exist.
    """
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    options = options or ExtractionOptions()
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(
        "Extracting frames from %s at %.2f fps",
        video_path.name,
        options.fps,
    )

    backend = _get_backend(video_path)
    try:
        total_frames = backend.get_frame_count()
        video_fps = backend.get_fps()

        indices = _calculate_frame_indices(
            total_frames=total_frames,
            video_fps=video_fps,
            target_fps=options.fps,
            max_frames=options.max_frames,
        )

        if not indices:
            logger.warning("No frames to extract from %s", video_path.name)
            return 0

        logger.debug(
            "Extracting %d frames from %d total (video fps: %.2f)",
            len(indices),
            total_frames,
            video_fps,
        )

        # Batch extraction for efficiency
        batch_size = 32
        extracted_count = 0

        for batch_start in range(0, len(indices), batch_size):
            batch_indices = indices[batch_start : batch_start + batch_size]

            try:
                frames = backend.get_batch(batch_indices)
            except Exception as e:
                logger.error("Batch extraction failed, falling back to single: %s", e)
                frames = [backend.get_frame(idx) for idx in batch_indices]

            for i, frame in enumerate(frames):
                frame_num = batch_start + i
                suffix = options.output_format.value
                output_path = output_dir / f"frame_{frame_num:06d}.{suffix}"

                _save_frame(frame, output_path, options.output_format, options.quality)
                extracted_count += 1

        logger.info(
            "Extracted %d frames from %s to %s",
            extracted_count,
            video_path.name,
            output_dir,
        )

        return extracted_count

    finally:
        backend.close()


def _compute_frame_difference(
    frame1: NDArray[np.uint8],
    frame2: NDArray[np.uint8],
) -> float:
    """Compute normalized difference between two frames.

    Args:
        frame1: First RGB frame.
        frame2: Second RGB frame.

    Returns:
        Normalized difference score (0.0 to 1.0).
    """
    # Convert to grayscale for comparison
    gray1 = np.mean(frame1, axis=2).astype(np.float32)
    gray2 = np.mean(frame2, axis=2).astype(np.float32)

    # Compute absolute difference
    diff = np.abs(gray1 - gray2)

    # Normalize by maximum possible difference (255)
    return float(np.mean(diff) / 255.0)


def extract_keyframes(
    video_path: Path,
    output_dir: Path,
    threshold: float = 0.3,
    options: ExtractionOptions | None = None,
) -> int:
    """Extract keyframes based on scene change detection.

    Keyframes are extracted when the difference between consecutive
    frames exceeds the specified threshold.

    Args:
        video_path: Path to the input video file.
        output_dir: Directory to save extracted keyframes.
        threshold: Scene change threshold (0.0 to 1.0).
        options: Extraction configuration options.

    Returns:
        Number of keyframes extracted.

    Raises:
        ExtractionError: If extraction fails.
        FileNotFoundError: If video file does not exist.
        ValueError: If threshold is out of range.
    """
    if not 0.0 <= threshold <= 1.0:
        raise ValueError(f"Threshold must be between 0.0 and 1.0, got {threshold}")

    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    options = options or ExtractionOptions()
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(
        "Extracting keyframes from %s with threshold %.2f",
        video_path.name,
        threshold,
    )

    backend = _get_backend(video_path)
    try:
        total_frames = backend.get_frame_count()

        if total_frames == 0:
            logger.warning("Video has no frames: %s", video_path.name)
            return 0

        keyframe_indices: list[int] = [0]  # Always include first frame
        prev_frame = backend.get_frame(0)

        # Sample frames at reduced rate for efficiency
        sample_interval = max(1, int(backend.get_fps() / 10))  # ~10 samples per second

        for idx in range(sample_interval, total_frames, sample_interval):
            current_frame = backend.get_frame(idx)
            diff = _compute_frame_difference(prev_frame, current_frame)

            if diff >= threshold:
                keyframe_indices.append(idx)
                prev_frame = current_frame

                logger.debug("Keyframe detected at frame %d (diff: %.3f)", idx, diff)

        # Apply max_frames limit
        if options.max_frames and len(keyframe_indices) > options.max_frames:
            step = len(keyframe_indices) / options.max_frames
            keyframe_indices = [
                keyframe_indices[int(i * step)] for i in range(options.max_frames)
            ]

        # Extract and save keyframes
        extracted_count = 0
        for i, idx in enumerate(keyframe_indices):
            frame = backend.get_frame(idx)
            suffix = options.output_format.value
            output_path = output_dir / f"keyframe_{i:04d}_f{idx:06d}.{suffix}"

            _save_frame(frame, output_path, options.output_format, options.quality)
            extracted_count += 1

        logger.info(
            "Extracted %d keyframes from %s to %s",
            extracted_count,
            video_path.name,
            output_dir,
        )

        return extracted_count

    finally:
        backend.close()


def get_available_backend() -> str:
    """Get the name of the available video backend.

    Returns:
        Name of the available backend ('decord', 'opencv', or 'none').
    """
    if _DECORD_AVAILABLE:
        return "decord"
    if _OPENCV_AVAILABLE:
        return "opencv"
    return "none"
