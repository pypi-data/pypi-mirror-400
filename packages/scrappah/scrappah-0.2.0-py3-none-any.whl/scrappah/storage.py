"""Database and file management for video dataset storage."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import aiosqlite
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class VideoRecord(BaseModel):
    """Represents a video record in the database."""

    id: str
    title: str
    duration: float | None = None
    video_path: str | None = None
    frames_dir: str | None = None
    transcript_path: str | None = None
    frame_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
    downloaded_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class DatasetStorage:
    """Manages SQLite database and file system storage for video datasets.

    Handles:
    - Async SQLite operations for video metadata
    - Directory structure for videos, frames, and transcripts
    - CRUD operations for video records
    - Statistics and querying
    """

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS videos (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        duration REAL,
        video_path TEXT,
        frames_dir TEXT,
        transcript_path TEXT,
        frame_count INTEGER DEFAULT 0,
        metadata TEXT DEFAULT '{}',
        downloaded_at TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_videos_downloaded_at ON videos(downloaded_at);
    CREATE INDEX IF NOT EXISTS idx_videos_title ON videos(title);
    """

    def __init__(self, base_dir: str | Path = "dataset"):
        """Initialize storage with base directory.

        Args:
            base_dir: Base directory for all dataset files
        """
        self.base_dir = Path(base_dir).resolve()
        self.db_path = self.base_dir / "dataset.db"
        self._db: aiosqlite.Connection | None = None
        self._lock = asyncio.Lock()

    @property
    def videos_dir(self) -> Path:
        """Directory for downloaded video files."""
        return self.base_dir / "videos"

    @property
    def frames_dir(self) -> Path:
        """Directory for extracted frames."""
        return self.base_dir / "frames"

    @property
    def transcripts_dir(self) -> Path:
        """Directory for transcription files."""
        return self.base_dir / "transcripts"

    async def init_db(self) -> None:
        """Initialize database and create directory structure.

        Creates all necessary directories and database tables.
        Safe to call multiple times.
        """
        # Create directory structure
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.videos_dir.mkdir(parents=True, exist_ok=True)
        self.frames_dir.mkdir(parents=True, exist_ok=True)
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initialized directory structure at {self.base_dir}")

        # Initialize database
        async with self._lock:
            self._db = await aiosqlite.connect(self.db_path)
            self._db.row_factory = aiosqlite.Row
            await self._db.executescript(self.SCHEMA)
            await self._db.commit()

        logger.info(f"Database initialized at {self.db_path}")

    async def close(self) -> None:
        """Close database connection."""
        async with self._lock:
            if self._db:
                await self._db.close()
                self._db = None

    async def _ensure_connected(self) -> aiosqlite.Connection:
        """Ensure database connection is active."""
        if self._db is None:
            await self.init_db()
        return self._db  # type: ignore

    async def add_video(self, video: VideoRecord) -> None:
        """Add or update a video record in the database.

        Args:
            video: VideoRecord to add or update

        Raises:
            RuntimeError: If database is not initialized
        """
        db = await self._ensure_connected()

        metadata_json = json.dumps(video.metadata)
        downloaded_at_str = video.downloaded_at.isoformat()

        async with self._lock:
            await db.execute(
                """
                INSERT OR REPLACE INTO videos
                (id, title, duration, video_path, frames_dir, transcript_path,
                 frame_count, metadata, downloaded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    video.id,
                    video.title,
                    video.duration,
                    video.video_path,
                    video.frames_dir,
                    video.transcript_path,
                    video.frame_count,
                    metadata_json,
                    downloaded_at_str,
                ),
            )
            await db.commit()

        logger.debug(f"Added/updated video: {video.id} - {video.title}")

    async def get_video(self, video_id: str) -> VideoRecord | None:
        """Retrieve a video record by ID.

        Args:
            video_id: Unique video identifier

        Returns:
            VideoRecord if found, None otherwise
        """
        db = await self._ensure_connected()

        async with self._lock:
            async with db.execute(
                "SELECT * FROM videos WHERE id = ?", (video_id,)
            ) as cursor:
                row = await cursor.fetchone()

        if row is None:
            return None

        return self._row_to_record(row)

    async def video_exists(self, video_id: str) -> bool:
        """Check if a video exists in the database.

        Args:
            video_id: Unique video identifier

        Returns:
            True if video exists, False otherwise
        """
        db = await self._ensure_connected()

        async with self._lock:
            async with db.execute(
                "SELECT 1 FROM videos WHERE id = ?", (video_id,)
            ) as cursor:
                row = await cursor.fetchone()

        return row is not None

    async def list_videos(
        self,
        limit: int | None = None,
        offset: int = 0,
        order_by: str = "downloaded_at",
        descending: bool = True,
    ) -> list[VideoRecord]:
        """List video records with pagination.

        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            order_by: Column to order by
            descending: Whether to sort in descending order

        Returns:
            List of VideoRecord objects
        """
        db = await self._ensure_connected()

        # Validate order_by to prevent SQL injection
        valid_columns = {
            "id",
            "title",
            "duration",
            "frame_count",
            "downloaded_at",
        }
        if order_by not in valid_columns:
            order_by = "downloaded_at"

        order_dir = "DESC" if descending else "ASC"
        query = f"SELECT * FROM videos ORDER BY {order_by} {order_dir}"

        if limit is not None:
            query += f" LIMIT {limit} OFFSET {offset}"

        async with self._lock:
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()

        return [self._row_to_record(row) for row in rows]

    async def get_stats(self) -> dict[str, Any]:
        """Get dataset statistics.

        Returns:
            Dictionary with stats including total videos, frames, storage size
        """
        db = await self._ensure_connected()

        async with self._lock:
            async with db.execute(
                """
                SELECT
                    COUNT(*) as total_videos,
                    SUM(frame_count) as total_frames,
                    SUM(duration) as total_duration,
                    AVG(duration) as avg_duration,
                    MIN(downloaded_at) as first_download,
                    MAX(downloaded_at) as last_download
                FROM videos
                """
            ) as cursor:
                row = await cursor.fetchone()

        # Calculate storage size
        storage_bytes = self._calculate_storage_size()

        return {
            "total_videos": row["total_videos"] or 0,
            "total_frames": row["total_frames"] or 0,
            "total_duration_seconds": row["total_duration"] or 0.0,
            "avg_duration_seconds": row["avg_duration"] or 0.0,
            "first_download": row["first_download"],
            "last_download": row["last_download"],
            "storage_bytes": storage_bytes,
            "storage_human": self._format_bytes(storage_bytes),
        }

    async def delete_video(self, video_id: str, delete_files: bool = True) -> bool:
        """Delete a video record and optionally its files.

        Args:
            video_id: Video ID to delete
            delete_files: Whether to delete associated files

        Returns:
            True if video was deleted, False if not found
        """
        video = await self.get_video(video_id)
        if video is None:
            return False

        if delete_files:
            # Delete video file
            if video.video_path:
                video_file = Path(video.video_path)
                if video_file.exists():
                    video_file.unlink()

            # Delete frames directory
            if video.frames_dir:
                frames_path = Path(video.frames_dir)
                if frames_path.exists():
                    import shutil

                    shutil.rmtree(frames_path)

            # Delete transcript
            if video.transcript_path:
                transcript_file = Path(video.transcript_path)
                if transcript_file.exists():
                    transcript_file.unlink()

        db = await self._ensure_connected()
        async with self._lock:
            await db.execute("DELETE FROM videos WHERE id = ?", (video_id,))
            await db.commit()

        logger.info(f"Deleted video: {video_id}")
        return True

    async def search_videos(self, query: str, limit: int = 50) -> list[VideoRecord]:
        """Search videos by title.

        Args:
            query: Search query (case-insensitive partial match)
            limit: Maximum results to return

        Returns:
            List of matching VideoRecord objects
        """
        db = await self._ensure_connected()

        async with self._lock:
            async with db.execute(
                """
                SELECT * FROM videos
                WHERE title LIKE ?
                ORDER BY downloaded_at DESC
                LIMIT ?
                """,
                (f"%{query}%", limit),
            ) as cursor:
                rows = await cursor.fetchall()

        return [self._row_to_record(row) for row in rows]

    def get_video_path(self, video_id: str, extension: str = "mp4") -> Path:
        """Get the expected path for a video file.

        Args:
            video_id: Video identifier
            extension: File extension

        Returns:
            Path where video should be stored
        """
        return self.videos_dir / f"{video_id}.{extension}"

    def get_frames_path(self, video_id: str) -> Path:
        """Get the expected directory for video frames.

        Args:
            video_id: Video identifier

        Returns:
            Path where frames should be stored
        """
        return self.frames_dir / video_id

    def get_transcript_path(self, video_id: str) -> Path:
        """Get the expected path for transcript file.

        Args:
            video_id: Video identifier

        Returns:
            Path where transcript should be stored
        """
        return self.transcripts_dir / f"{video_id}.json"

    def _row_to_record(self, row: aiosqlite.Row) -> VideoRecord:
        """Convert database row to VideoRecord."""
        metadata = json.loads(row["metadata"]) if row["metadata"] else {}
        downloaded_at = datetime.fromisoformat(row["downloaded_at"])

        return VideoRecord(
            id=row["id"],
            title=row["title"],
            duration=row["duration"],
            video_path=row["video_path"],
            frames_dir=row["frames_dir"],
            transcript_path=row["transcript_path"],
            frame_count=row["frame_count"],
            metadata=metadata,
            downloaded_at=downloaded_at,
        )

    def _calculate_storage_size(self) -> int:
        """Calculate total storage size in bytes."""
        total = 0
        for directory in [self.videos_dir, self.frames_dir, self.transcripts_dir]:
            if directory.exists():
                for file in directory.rglob("*"):
                    if file.is_file():
                        total += file.stat().st_size
        return total

    @staticmethod
    def _format_bytes(size: int) -> str:
        """Format bytes to human-readable string."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"

    async def __aenter__(self) -> "DatasetStorage":
        """Async context manager entry."""
        await self.init_db()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
