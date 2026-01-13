"""Audio transcription module using OpenAI Whisper.

This module provides high-quality speech-to-text transcription
with timestamp segmentation using the Whisper model.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from scrappah.models import (
    TranscriptionOptions,
    TranscriptResult,
    TranscriptSegment,
    WhisperModel,
)

logger = logging.getLogger(__name__)

# Attempt to import whisper
_WHISPER_AVAILABLE = False
_whisper_module: Any = None

try:
    import whisper as _whisper_module

    _WHISPER_AVAILABLE = True
    logger.debug("Whisper module available")
except ImportError:
    logger.warning("Whisper not available. Install with: pip install openai-whisper")


class TranscriptionError(Exception):
    """Raised when transcription fails."""

    pass


class ModelNotLoadedError(TranscriptionError):
    """Raised when attempting to transcribe without a loaded model."""

    pass


class WhisperNotAvailableError(TranscriptionError):
    """Raised when Whisper is not installed."""

    pass


class Transcriber:
    """Whisper-based audio transcriber with model caching.

    This class manages Whisper model loading and provides methods
    for transcribing audio/video files with timestamp segmentation.

    Attributes:
        model_name: Currently loaded model name.
        device: Device the model is loaded on ('cuda' or 'cpu').
    """

    def __init__(self, options: TranscriptionOptions | None = None) -> None:
        """Initialize the transcriber.

        Args:
            options: Transcription options. If provided, loads the model immediately.

        Raises:
            WhisperNotAvailableError: If Whisper is not installed.
        """
        if not _WHISPER_AVAILABLE:
            raise WhisperNotAvailableError(
                "Whisper is not installed. Install with: pip install openai-whisper"
            )

        self._model: Any = None
        self._model_name: WhisperModel | None = None
        self._device: str = "cpu"
        self._options = options or TranscriptionOptions()

        if options is not None:
            self.load_model(options.model)

    @property
    def model_name(self) -> WhisperModel | None:
        """Get the currently loaded model name."""
        return self._model_name

    @property
    def device(self) -> str:
        """Get the device the model is loaded on."""
        return self._device

    @property
    def is_loaded(self) -> bool:
        """Check if a model is currently loaded."""
        return self._model is not None

    def load_model(self, model: WhisperModel | None = None) -> None:
        """Load a Whisper model.

        Args:
            model: Model size to load. Uses options default if not specified.

        Raises:
            TranscriptionError: If model loading fails.
        """
        model = model or self._options.model

        if self._model is not None and self._model_name == model:
            logger.debug("Model %s already loaded", model.value)
            return

        logger.info("Loading Whisper model: %s", model.value)

        try:
            import torch

            self._device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info("Using device: %s", self._device)
        except ImportError:
            self._device = "cpu"
            logger.info("PyTorch CUDA check unavailable, using CPU")

        try:
            self._model = _whisper_module.load_model(model.value, device=self._device)
            self._model_name = model
            logger.info("Model %s loaded successfully on %s", model.value, self._device)
        except Exception as e:
            raise TranscriptionError(f"Failed to load Whisper model: {e}") from e

    def unload_model(self) -> None:
        """Unload the current model to free memory."""
        if self._model is not None:
            del self._model
            self._model = None
            self._model_name = None
            logger.info("Model unloaded")

            # Attempt to clear CUDA cache
            try:
                import torch

                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except ImportError:
                pass

    def transcribe(
        self,
        video_path: Path,
        output_path: Path | None = None,
        options: TranscriptionOptions | None = None,
    ) -> TranscriptResult:
        """Transcribe audio from a video or audio file.

        Args:
            video_path: Path to the video or audio file.
            output_path: Optional path to save JSON transcript.
            options: Transcription options (overrides instance options).

        Returns:
            TranscriptResult with full text and timestamped segments.

        Raises:
            FileNotFoundError: If the input file does not exist.
            ModelNotLoadedError: If no model is loaded.
            TranscriptionError: If transcription fails.
        """
        if not video_path.exists():
            raise FileNotFoundError(f"Input file not found: {video_path}")

        options = options or self._options

        # Ensure model is loaded
        if not self.is_loaded:
            self.load_model(options.model)
        elif self._model_name != options.model:
            logger.info(
                "Switching model from %s to %s",
                self._model_name,
                options.model.value,
            )
            self.load_model(options.model)

        logger.info("Transcribing: %s", video_path.name)

        try:
            # Prepare transcription parameters
            transcribe_params: dict[str, Any] = {
                "verbose": False,
                "word_timestamps": False,
            }

            if options.language is not None:
                transcribe_params["language"] = options.language
                logger.debug("Using specified language: %s", options.language)

            # Perform transcription
            result = self._model.transcribe(str(video_path), **transcribe_params)

            # Extract segments
            segments = tuple(
                TranscriptSegment(
                    start=seg["start"],
                    end=seg["end"],
                    text=seg["text"].strip(),
                )
                for seg in result.get("segments", [])
            )

            # Calculate duration from segments or use 0
            duration = segments[-1].end if segments else 0.0

            transcript_result = TranscriptResult(
                text=result["text"].strip(),
                segments=segments,
                language=result.get("language", options.language or "unknown"),
                duration=duration,
            )

            logger.info(
                "Transcription complete: %d segments, %.1f seconds, language: %s",
                len(segments),
                duration,
                transcript_result.language,
            )

            # Save to JSON if output path specified
            if output_path is not None:
                self._save_transcript(transcript_result, output_path, video_path)

            return transcript_result

        except Exception as e:
            if isinstance(e, (FileNotFoundError, ModelNotLoadedError)):
                raise
            raise TranscriptionError(f"Transcription failed: {e}") from e

    def _save_transcript(
        self,
        result: TranscriptResult,
        output_path: Path,
        source_path: Path,
    ) -> None:
        """Save transcript result to JSON file.

        Args:
            result: Transcript result to save.
            output_path: Path to save the JSON file.
            source_path: Original source file path for metadata.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Build JSON structure with metadata
        json_data = {
            "metadata": {
                "source_file": source_path.name,
                "transcribed_at": datetime.now().isoformat(),
                "model": self._model_name.value if self._model_name else "unknown",
                "device": self._device,
            },
            "result": {
                "text": result.text,
                "language": result.language,
                "duration": result.duration,
                "segments": [
                    {
                        "start": seg.start,
                        "end": seg.end,
                        "text": seg.text,
                    }
                    for seg in result.segments
                ],
            },
        }

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        logger.info("Transcript saved to: %s", output_path)

    def __enter__(self) -> "Transcriber":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - unload model."""
        self.unload_model()


def transcribe_file(
    video_path: Path,
    output_path: Path | None = None,
    options: TranscriptionOptions | None = None,
) -> TranscriptResult:
    """Convenience function to transcribe a single file.

    This function creates a temporary Transcriber instance,
    transcribes the file, and cleans up automatically.

    Args:
        video_path: Path to the video or audio file.
        output_path: Optional path to save JSON transcript.
        options: Transcription options.

    Returns:
        TranscriptResult with full text and timestamped segments.
    """
    options = options or TranscriptionOptions()

    with Transcriber(options) as transcriber:
        return transcriber.transcribe(video_path, output_path, options)


def is_whisper_available() -> bool:
    """Check if Whisper is available for transcription.

    Returns:
        True if Whisper is installed and importable.
    """
    return _WHISPER_AVAILABLE
