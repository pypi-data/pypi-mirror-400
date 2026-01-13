# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-01-05

### Changed

- **Frame extraction and transcription are now core features** - OpenCV and Whisper are installed by default
- Simplified installation: `pip install scrappah` now includes everything needed
- Decord remains optional for GPU-accelerated frame extraction (`pip install scrappah[decord]`)

### Fixed

- Fixed Python 3.13 compatibility by pinning numba>=0.60.0
- Frame extraction and transcription no longer silently skip when dependencies are missing

## [0.1.0] - 2024-01-15

### Added

- Initial public release
- **Video downloading** via yt-dlp
  - Support for single videos, playlists, and channels
  - Configurable resolution and format options
  - Rate limiting and respectful scraping
- **Frame extraction** with dual backends
  - Decord backend (fast, GPU-accelerated)
  - OpenCV backend (compatible fallback)
  - Configurable FPS and quality settings
  - Keyframe extraction with scene change detection
- **Audio transcription** with OpenAI Whisper
  - Multiple model sizes (tiny, base, small, medium, large)
  - Automatic language detection
  - Timestamped segment output
- **Dataset management**
  - SQLite-based video index
  - Organized directory structure (videos/, frames/, transcripts/)
  - Search and list functionality
- **Async pipeline** for concurrent processing
  - Configurable concurrency limits
  - Progress tracking with rich output
  - Resume support for interrupted batches
- **CLI interface** with Typer
  - Commands: video, playlist, channel, batch, stats, list, search, delete
  - Rich progress bars and formatted output
- **Synchronous API** convenience wrappers
  - `download_video()`, `download_playlist()`, `download_channel()`, `download_batch()`
- **Full type hints** and PEP 561 compliance
- **Cross-platform support** (Windows, macOS, Linux)

### Documentation

- Comprehensive README with platform-specific installation instructions
- API documentation with examples
- Citation file (CITATION.cff) for academic use
