"""YouTube audio cache management for music-cli.

This module provides caching for YouTube audio to enable offline playback.
Tracks are automatically cached when played and can be replayed without
internet connection.
"""

import json
import logging
import re
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class CachedYouTubeTrack:
    """A cached YouTube audio track."""

    video_id: str
    youtube_url: str
    file_path: str
    title: str
    artist: str | None
    duration: float | None
    thumbnail: str | None
    cached_at: str
    last_accessed: str
    file_size: int

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "video_id": self.video_id,
            "youtube_url": self.youtube_url,
            "file_path": self.file_path,
            "title": self.title,
            "artist": self.artist,
            "duration": self.duration,
            "thumbnail": self.thumbnail,
            "cached_at": self.cached_at,
            "last_accessed": self.last_accessed,
            "file_size": self.file_size,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CachedYouTubeTrack":
        """Create from dictionary."""
        return cls(
            video_id=data.get("video_id", ""),
            youtube_url=data.get("youtube_url", ""),
            file_path=data.get("file_path", ""),
            title=data.get("title", "Unknown"),
            artist=data.get("artist"),
            duration=data.get("duration"),
            thumbnail=data.get("thumbnail"),
            cached_at=data.get("cached_at", ""),
            last_accessed=data.get("last_accessed", ""),
            file_size=data.get("file_size", 0),
        )

    def file_exists(self) -> bool:
        """Check if the cached audio file exists."""
        return Path(self.file_path).exists()

    def display_title(self, max_length: int = 50) -> str:
        """Get a truncated title for display."""
        if len(self.title) <= max_length:
            return self.title
        return self.title[: max_length - 3] + "..."


def extract_video_id(url: str) -> str | None:
    """Extract video ID from YouTube URL.

    Args:
        url: YouTube URL in any supported format.

    Returns:
        11-character video ID or None if not found.
    """
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})",
        r"music\.youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


class YouTubeCacheManager:
    """Manages YouTube audio cache with LRU eviction."""

    DEFAULT_MAX_SIZE_GB = 2.0

    def __init__(
        self,
        cache_file: Path | None = None,
        cache_dir: Path | None = None,
        max_size_gb: float | None = None,
    ):
        """Initialize YouTube cache manager.

        Args:
            cache_file: Path to youtube_cache.json
            cache_dir: Directory for cached audio files
            max_size_gb: Maximum cache size in GB
        """
        from .config import get_config

        config = get_config()

        if cache_file is None:
            cache_file = config.youtube_cache_file
        if cache_dir is None:
            cache_dir = config.youtube_cache_dir
        if max_size_gb is None:
            config_value = config.get("youtube.cache.max_size_gb", self.DEFAULT_MAX_SIZE_GB)
            max_size_gb = (
                float(config_value) if config_value is not None else self.DEFAULT_MAX_SIZE_GB
            )

        self.cache_file = cache_file
        self.cache_dir = cache_dir
        size_gb: float = max_size_gb if max_size_gb is not None else self.DEFAULT_MAX_SIZE_GB
        self.max_size_bytes = int(size_gb * 1024 * 1024 * 1024)
        self._lock = threading.Lock()

        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create cache directory and file if needed."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        if not self.cache_file.exists():
            self.cache_file.write_text("{}")

    def _load_cache(self) -> dict[str, CachedYouTubeTrack]:
        """Load cache index from JSON file."""
        try:
            data = json.loads(self.cache_file.read_text())
            return {
                video_id: CachedYouTubeTrack.from_dict(track_data)
                for video_id, track_data in data.items()
            }
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load YouTube cache: {e}")
            return {}

    def _save_cache(self, cache: dict[str, CachedYouTubeTrack]) -> None:
        """Save cache index to JSON file."""
        data = {video_id: track.to_dict() for video_id, track in cache.items()}
        self.cache_file.write_text(json.dumps(data, indent=2))

    def get_by_video_id(self, video_id: str) -> CachedYouTubeTrack | None:
        """Get cached track by video ID, updating last_accessed.

        Args:
            video_id: YouTube video ID.

        Returns:
            CachedYouTubeTrack if found and file exists, None otherwise.
        """
        with self._lock:
            cache = self._load_cache()
            track = cache.get(video_id)

            if track and track.file_exists():
                track.last_accessed = datetime.now().isoformat()
                cache[video_id] = track
                self._save_cache(cache)
                return track
            elif track and not track.file_exists():
                del cache[video_id]
                self._save_cache(cache)
                logger.info(f"Removed stale cache entry: {track.title}")

        return None

    def get_by_url(self, youtube_url: str) -> CachedYouTubeTrack | None:
        """Get cached track by YouTube URL.

        Args:
            youtube_url: Full YouTube URL.

        Returns:
            CachedYouTubeTrack if cached, None otherwise.
        """
        video_id = extract_video_id(youtube_url)
        if video_id:
            return self.get_by_video_id(video_id)
        return None

    def add_track(
        self,
        video_id: str,
        youtube_url: str,
        file_path: str,
        title: str,
        artist: str | None,
        duration: float | None,
        thumbnail: str | None,
    ) -> CachedYouTubeTrack:
        """Add a new cached track.

        Args:
            video_id: YouTube video ID.
            youtube_url: Original YouTube URL.
            file_path: Path to cached audio file.
            title: Video title.
            artist: Channel/uploader name.
            duration: Duration in seconds.
            thumbnail: Thumbnail URL.

        Returns:
            The created CachedYouTubeTrack.
        """
        path = Path(file_path)
        if not path.exists():
            logger.error(f"Cannot add track: file not found: {file_path}")
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        file_size = path.stat().st_size
        now = datetime.now().isoformat()

        track = CachedYouTubeTrack(
            video_id=video_id,
            youtube_url=youtube_url,
            file_path=file_path,
            title=title,
            artist=artist,
            duration=duration,
            thumbnail=thumbnail,
            cached_at=now,
            last_accessed=now,
            file_size=file_size,
        )

        with self._lock:
            cache = self._load_cache()
            cache[video_id] = track
            self._save_cache(cache)
            self._evict_if_needed()

        logger.info(f"Cached YouTube audio: {title}")
        return track

    def get_all(self) -> list[CachedYouTubeTrack]:
        """Get all cached tracks, sorted by last_accessed (newest first).

        Returns:
            List of CachedYouTubeTrack sorted by most recently accessed.
        """
        cache = self._load_cache()
        tracks = list(cache.values())
        tracks.sort(key=lambda t: t.last_accessed, reverse=True)
        return tracks

    def get_by_index(self, index: int) -> CachedYouTubeTrack | None:
        """Get track by 1-based index (most recently accessed first).

        Args:
            index: 1-based index.

        Returns:
            CachedYouTubeTrack if found, None otherwise.
        """
        tracks = self.get_all()
        if 1 <= index <= len(tracks):
            return tracks[index - 1]
        return None

    def remove_by_index(self, index: int) -> CachedYouTubeTrack | None:
        """Remove track by 1-based index.

        Args:
            index: 1-based index.

        Returns:
            Removed CachedYouTubeTrack or None if invalid index.
        """
        tracks = self.get_all()
        if not (1 <= index <= len(tracks)):
            return None

        track = tracks[index - 1]
        return self.remove_by_video_id(track.video_id)

    def remove_by_video_id(self, video_id: str) -> CachedYouTubeTrack | None:
        """Remove track by video ID.

        Args:
            video_id: YouTube video ID.

        Returns:
            Removed CachedYouTubeTrack or None if not found.
        """
        with self._lock:
            cache = self._load_cache()
            track = cache.pop(video_id, None)

            if track:
                try:
                    file_path = Path(track.file_path)
                    if file_path.exists():
                        file_path.unlink()
                        logger.info(f"Deleted cached audio: {file_path}")
                except OSError as e:
                    logger.warning(f"Failed to delete cached file: {e}")

                self._save_cache(cache)

        return track

    def clear(self) -> int:
        """Clear all cached tracks.

        Returns:
            Number of tracks removed.
        """
        with self._lock:
            tracks = self.get_all()
            count = len(tracks)

            for track in tracks:
                try:
                    file_path = Path(track.file_path)
                    if file_path.exists():
                        file_path.unlink()
                except OSError as e:
                    logger.warning(f"Failed to delete {track.file_path}: {e}")

            self._save_cache({})
            logger.info(f"Cleared YouTube cache: {count} tracks removed")
        return count

    def get_total_size(self) -> int:
        """Get total cache size in bytes.

        Returns:
            Total size of all cached files.
        """
        return sum(t.file_size for t in self.get_all() if t.file_exists())

    def get_stats(self) -> dict:
        """Get cache statistics.

        Returns:
            Dictionary with count, sizes, and usage percentage.
        """
        tracks = self.get_all()
        total_size = sum(t.file_size for t in tracks if t.file_exists())
        return {
            "count": len(tracks),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "max_size_gb": round(self.max_size_bytes / (1024 * 1024 * 1024), 2),
            "usage_percent": (
                round((total_size / self.max_size_bytes) * 100, 1) if self.max_size_bytes > 0 else 0
            ),
        }

    def count(self) -> int:
        """Get number of cached tracks.

        Returns:
            Number of tracks in cache.
        """
        return len(self._load_cache())

    def _evict_if_needed(self) -> int:
        """Evict oldest tracks if cache exceeds max size.

        Returns:
            Number of tracks evicted.
        """
        evicted = 0
        cache = self._load_cache()

        sorted_tracks = sorted(cache.values(), key=lambda t: t.last_accessed)

        total_size = sum(t.file_size for t in sorted_tracks if t.file_exists())

        while total_size > self.max_size_bytes and sorted_tracks:
            oldest = sorted_tracks.pop(0)
            try:
                file_path = Path(oldest.file_path)
                if file_path.exists():
                    file_path.unlink()
            except OSError as e:
                logger.warning(f"Failed to evict {oldest.file_path}: {e}")
            del cache[oldest.video_id]
            total_size -= oldest.file_size
            evicted += 1
            logger.info(f"LRU evicted: {oldest.title}")

        if evicted > 0:
            self._save_cache(cache)

        return evicted


_youtube_cache: YouTubeCacheManager | None = None
_youtube_cache_lock = threading.Lock()


def get_youtube_cache() -> YouTubeCacheManager:
    """Get the global YouTube cache manager instance.

    Returns:
        Singleton YouTubeCacheManager instance.
    """
    global _youtube_cache
    if _youtube_cache is None:
        with _youtube_cache_lock:
            if _youtube_cache is None:
                _youtube_cache = YouTubeCacheManager()
    return _youtube_cache
