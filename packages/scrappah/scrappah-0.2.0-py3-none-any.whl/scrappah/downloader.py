"""yt-dlp wrapper for video downloading with rate limiting and progress support.

Note on SSL errors (Fedora and OpenSSL 3.x):
    On Fedora 37+ and other distributions with OpenSSL 3.x and strict crypto-policies,
    you may encounter 'SSLError: unknown error (_ssl.c:3123)' when downloading videos.

    The fix is applied automatically in main.py by setting OPENSSL_CONF=/dev/null
    before any SSL-related imports. If you're using this module directly, you may
    need to set this environment variable before importing:

        import os
        os.environ["OPENSSL_CONF"] = "/dev/null"
        from src.downloader import VideoDownloader
"""

from __future__ import annotations

import asyncio
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import shutil

import yt_dlp

logger = logging.getLogger(__name__)


def _is_ffmpeg_available() -> bool:
    """Check if ffmpeg is available on the system."""
    return shutil.which("ffmpeg") is not None


@dataclass
class DownloadOptions:
    """Configuration options for video downloads."""

    format: str = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
    max_height: int | None = 1080
    rate_limit: str | None = None  # e.g., "1M" for 1MB/s
    min_delay: float = 1.0  # Minimum delay between downloads (seconds)
    max_delay: float = 3.0  # Maximum delay between downloads (seconds)
    retries: int = 3
    extract_audio: bool = False
    keep_video: bool = True
    cookies_file: str | None = None
    proxy: str | None = None
    geo_bypass: bool = True
    age_limit: int | None = None
    quiet: bool = False
    no_warnings: bool = False
    # SSL options for handling certificate verification issues
    no_check_certificate: bool = False  # Disable SSL certificate verification
    legacy_server_connect: bool = True  # Enable legacy SSL renegotiation (helps with some servers)


@dataclass
class VideoMetadata:
    """Metadata extracted from a downloaded video."""

    id: str
    title: str
    duration: float | None
    description: str | None
    uploader: str | None
    upload_date: str | None
    view_count: int | None
    like_count: int | None
    channel_id: str | None
    channel_url: str | None
    thumbnail: str | None
    webpage_url: str
    file_path: Path | None
    format_id: str | None
    width: int | None
    height: int | None
    fps: float | None
    vcodec: str | None
    acodec: str | None
    filesize: int | None
    raw_info: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_info_dict(cls, info: dict[str, Any], file_path: Path | None = None) -> "VideoMetadata":
        """Create VideoMetadata from yt-dlp info dictionary.

        Args:
            info: yt-dlp info dictionary
            file_path: Path to downloaded file

        Returns:
            VideoMetadata instance
        """
        return cls(
            id=info.get("id", ""),
            title=info.get("title", "Unknown"),
            duration=info.get("duration"),
            description=info.get("description"),
            uploader=info.get("uploader"),
            upload_date=info.get("upload_date"),
            view_count=info.get("view_count"),
            like_count=info.get("like_count"),
            channel_id=info.get("channel_id"),
            channel_url=info.get("channel_url"),
            thumbnail=info.get("thumbnail"),
            webpage_url=info.get("webpage_url", ""),
            file_path=file_path,
            format_id=info.get("format_id"),
            width=info.get("width"),
            height=info.get("height"),
            fps=info.get("fps"),
            vcodec=info.get("vcodec"),
            acodec=info.get("acodec"),
            filesize=info.get("filesize") or info.get("filesize_approx"),
            raw_info=info,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "title": self.title,
            "duration": self.duration,
            "description": self.description,
            "uploader": self.uploader,
            "upload_date": self.upload_date,
            "view_count": self.view_count,
            "like_count": self.like_count,
            "channel_id": self.channel_id,
            "channel_url": self.channel_url,
            "thumbnail": self.thumbnail,
            "webpage_url": self.webpage_url,
            "format_id": self.format_id,
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "vcodec": self.vcodec,
            "acodec": self.acodec,
            "filesize": self.filesize,
        }


ProgressCallback = Callable[[str, float, str], None]


class DownloadError(Exception):
    """Exception raised when download fails."""

    def __init__(self, message: str, video_id: str | None = None, original_error: Exception | None = None):
        super().__init__(message)
        self.video_id = video_id
        self.original_error = original_error


class VideoDownloader:
    """Async wrapper for yt-dlp with rate limiting and progress callbacks.

    Features:
    - Async download operations
    - Configurable rate limiting between downloads
    - Progress callbacks for UI integration
    - Playlist support with max video limits
    - Skip already downloaded videos
    - Robust error handling with retries
    """

    def __init__(self, options: DownloadOptions | None = None):
        """Initialize downloader with options.

        Args:
            options: Download configuration options
        """
        self.options = options or DownloadOptions()
        self._last_download_time: float = 0
        self._download_lock = asyncio.Lock()
        self._progress_callback: ProgressCallback | None = None

    def set_progress_callback(self, callback: ProgressCallback | None) -> None:
        """Set progress callback for download updates.

        Args:
            callback: Function(video_id, progress_percent, status_message)
        """
        self._progress_callback = callback

    def _build_ssl_opts(self) -> dict[str, Any]:
        """Build SSL-related options for yt-dlp.

        Handles SSL certificate verification issues common on some Linux distributions
        (e.g., Fedora) where Python's SSL module may have compatibility issues.

        Returns:
            Dictionary with SSL-related yt-dlp options
        """
        ssl_opts: dict[str, Any] = {
            # Enable legacy SSL renegotiation to handle servers with older SSL configs
            "legacy_server_connect": self.options.legacy_server_connect,
        }

        if self.options.no_check_certificate:
            # Only disable certificate verification if explicitly requested
            ssl_opts["nocheckcertificate"] = True

        return ssl_opts

    def _build_ydl_opts(self, output_dir: Path, output_template: str | None = None) -> dict[str, Any]:
        """Build yt-dlp options dictionary.

        Args:
            output_dir: Directory for downloaded files
            output_template: Custom output filename template

        Returns:
            yt-dlp options dictionary
        """
        template = output_template or "%(id)s.%(ext)s"
        output_path = str(output_dir / template)

        opts: dict[str, Any] = {
            "format": self.options.format,
            "outtmpl": output_path,
            "retries": self.options.retries,
            "geo_bypass": self.options.geo_bypass,
            "ignoreerrors": False,
            "no_warnings": self.options.no_warnings,
            "quiet": self.options.quiet,
            "noprogress": self.options.quiet,
            "extract_flat": False,
            "writethumbnail": False,
            "writesubtitles": False,
            "writeautomaticsub": False,
        }

        # Add SSL options to handle certificate verification issues
        opts.update(self._build_ssl_opts())

        if self.options.max_height:
            if _is_ffmpeg_available():
                # With ffmpeg, we can merge separate video and audio streams
                opts["format"] = f"bestvideo[height<={self.options.max_height}]+bestaudio/best[height<={self.options.max_height}]/best"
            else:
                # Without ffmpeg, use pre-merged formats only (no merging required)
                logger.warning("FFmpeg not found - using pre-merged formats only (quality may be limited)")
                opts["format"] = f"best[height<={self.options.max_height}]/best"
        else:
            if not _is_ffmpeg_available():
                logger.warning("FFmpeg not found - using pre-merged formats only (quality may be limited)")
                opts["format"] = "best"

        if self.options.rate_limit:
            opts["ratelimit"] = self._parse_rate_limit(self.options.rate_limit)

        if self.options.cookies_file:
            opts["cookiefile"] = self.options.cookies_file

        if self.options.proxy:
            opts["proxy"] = self.options.proxy

        if self.options.age_limit:
            opts["age_limit"] = self.options.age_limit

        if self._progress_callback:
            opts["progress_hooks"] = [self._progress_hook]

        return opts

    def _progress_hook(self, d: dict[str, Any]) -> None:
        """yt-dlp progress hook for callbacks."""
        if not self._progress_callback:
            return

        video_id = d.get("info_dict", {}).get("id", "unknown")
        status = d.get("status", "unknown")

        if status == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            if total > 0:
                progress = (downloaded / total) * 100
                speed = d.get("speed", 0)
                speed_str = self._format_speed(speed) if speed else "N/A"
                self._progress_callback(video_id, progress, f"Downloading: {speed_str}")
        elif status == "finished":
            self._progress_callback(video_id, 100.0, "Download complete")
        elif status == "error":
            self._progress_callback(video_id, -1.0, "Download failed")

    @staticmethod
    def _format_speed(speed: float) -> str:
        """Format download speed for display."""
        if speed < 1024:
            return f"{speed:.0f} B/s"
        elif speed < 1024 * 1024:
            return f"{speed / 1024:.1f} KB/s"
        else:
            return f"{speed / (1024 * 1024):.1f} MB/s"

    @staticmethod
    def _parse_rate_limit(rate_str: str) -> int:
        """Parse rate limit string to bytes per second."""
        match = re.match(r"(\d+(?:\.\d+)?)\s*([KMG])?", rate_str.upper())
        if not match:
            return 0

        value = float(match.group(1))
        unit = match.group(2)

        multipliers = {"K": 1024, "M": 1024**2, "G": 1024**3}
        multiplier = multipliers.get(unit, 1)

        return int(value * multiplier)

    async def _apply_rate_limit(self) -> None:
        """Apply rate limiting delay between downloads."""
        import random

        async with self._download_lock:
            now = time.time()
            elapsed = now - self._last_download_time

            delay = random.uniform(self.options.min_delay, self.options.max_delay)
            if elapsed < delay:
                await asyncio.sleep(delay - elapsed)

            self._last_download_time = time.time()

    async def get_video_info(self, url: str) -> VideoMetadata:
        """Extract video metadata without downloading.

        Args:
            url: Video URL

        Returns:
            VideoMetadata with video information

        Raises:
            DownloadError: If metadata extraction fails
        """
        opts: dict[str, Any] = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "skip_download": True,
        }
        # Add SSL options to handle certificate verification issues
        opts.update(self._build_ssl_opts())

        try:
            loop = asyncio.get_event_loop()
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))

            if info is None:
                raise DownloadError("Failed to extract video info", video_id=None)

            return VideoMetadata.from_info_dict(info)

        except yt_dlp.utils.DownloadError as e:
            raise DownloadError(str(e), original_error=e)

    async def download_video(
        self,
        url: str,
        output_dir: Path | str,
        skip_existing: bool = True,
    ) -> VideoMetadata:
        """Download a single video.

        Args:
            url: Video URL to download
            output_dir: Directory for downloaded file
            skip_existing: Skip if file already exists

        Returns:
            VideoMetadata with download information

        Raises:
            DownloadError: If download fails
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        await self._apply_rate_limit()

        opts = self._build_ydl_opts(output_dir)

        try:
            loop = asyncio.get_event_loop()

            # First extract info to get video ID
            with yt_dlp.YoutubeDL({**opts, "skip_download": True}) as ydl:
                info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))

            if info is None:
                raise DownloadError("Failed to extract video info")

            video_id = info.get("id", "")

            # Check if already exists
            if skip_existing:
                expected_path = output_dir / f"{video_id}.mp4"
                if expected_path.exists():
                    logger.info(f"Skipping already downloaded video: {video_id}")
                    return VideoMetadata.from_info_dict(info, expected_path)

            # Download the video
            logger.info(f"Downloading video: {info.get('title', video_id)}")

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))

            if info is None:
                raise DownloadError("Download returned no info", video_id=video_id)

            # Find the downloaded file
            file_path = self._find_downloaded_file(output_dir, video_id)

            return VideoMetadata.from_info_dict(info, file_path)

        except yt_dlp.utils.DownloadError as e:
            raise DownloadError(str(e), original_error=e)
        except Exception as e:
            raise DownloadError(f"Unexpected error: {e}", original_error=e)

    def _find_downloaded_file(self, output_dir: Path, video_id: str) -> Path | None:
        """Find the downloaded file by video ID."""
        for ext in ["mp4", "webm", "mkv", "avi", "mov", "flv"]:
            path = output_dir / f"{video_id}.{ext}"
            if path.exists():
                return path

        # Search for any file starting with video_id
        for file in output_dir.iterdir():
            if file.stem == video_id or file.name.startswith(f"{video_id}."):
                return file

        return None

    async def download_playlist(
        self,
        url: str,
        output_dir: Path | str,
        max_videos: int | None = None,
        skip_existing: bool = True,
    ) -> list[VideoMetadata]:
        """Download videos from a playlist.

        Args:
            url: Playlist URL
            output_dir: Directory for downloaded files
            max_videos: Maximum number of videos to download
            skip_existing: Skip already downloaded videos

        Returns:
            List of VideoMetadata for downloaded videos

        Raises:
            DownloadError: If playlist extraction fails
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Extract playlist info
        opts: dict[str, Any] = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
            "ignoreerrors": True,
        }
        # Add SSL options to handle certificate verification issues
        opts.update(self._build_ssl_opts())

        try:
            loop = asyncio.get_event_loop()
            with yt_dlp.YoutubeDL(opts) as ydl:
                playlist_info = await loop.run_in_executor(
                    None, lambda: ydl.extract_info(url, download=False)
                )

            if playlist_info is None:
                raise DownloadError("Failed to extract playlist info")

            entries = playlist_info.get("entries", [])
            if not entries:
                logger.warning("No videos found in playlist")
                return []

            # Filter out None entries (private/deleted videos)
            entries = [e for e in entries if e is not None]

            if max_videos:
                entries = entries[:max_videos]

            logger.info(f"Found {len(entries)} videos in playlist")

            results: list[VideoMetadata] = []
            for i, entry in enumerate(entries, 1):
                video_url = entry.get("url") or entry.get("webpage_url")
                if not video_url:
                    video_id = entry.get("id")
                    if video_id:
                        video_url = f"https://www.youtube.com/watch?v={video_id}"
                    else:
                        continue

                try:
                    logger.info(f"Downloading {i}/{len(entries)}: {entry.get('title', 'Unknown')}")
                    metadata = await self.download_video(video_url, output_dir, skip_existing)
                    results.append(metadata)
                except DownloadError as e:
                    logger.error(f"Failed to download video {i}: {e}")
                    continue

            return results

        except yt_dlp.utils.DownloadError as e:
            raise DownloadError(f"Playlist error: {e}", original_error=e)

    async def get_playlist_info(self, url: str) -> list[dict[str, Any]]:
        """Get information about all videos in a playlist without downloading.

        Args:
            url: Playlist URL

        Returns:
            List of video info dictionaries
        """
        opts: dict[str, Any] = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
            "ignoreerrors": True,
        }
        # Add SSL options to handle certificate verification issues
        opts.update(self._build_ssl_opts())

        try:
            loop = asyncio.get_event_loop()
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))

            if info is None:
                return []

            entries = info.get("entries", [])
            return [e for e in entries if e is not None]

        except yt_dlp.utils.DownloadError:
            return []

    async def download_channel(
        self,
        url: str,
        output_dir: Path | str,
        max_videos: int | None = None,
        skip_existing: bool = True,
    ) -> list[VideoMetadata]:
        """Download videos from a channel.

        Args:
            url: Channel URL
            output_dir: Directory for downloaded files
            max_videos: Maximum number of videos to download
            skip_existing: Skip already downloaded videos

        Returns:
            List of VideoMetadata for downloaded videos
        """
        # Channels are handled similarly to playlists in yt-dlp
        return await self.download_playlist(url, output_dir, max_videos, skip_existing)

    @staticmethod
    def extract_video_id(url: str) -> str | None:
        """Extract video ID from various URL formats.

        Args:
            url: Video URL

        Returns:
            Video ID if found, None otherwise
        """
        patterns = [
            r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})",
            r"vimeo\.com/(\d+)",
            r"dailymotion\.com/video/([a-zA-Z0-9]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None
