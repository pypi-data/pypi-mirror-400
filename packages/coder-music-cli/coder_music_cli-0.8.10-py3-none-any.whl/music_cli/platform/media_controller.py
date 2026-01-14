"""Abstract media controller interface for OS integration.

This module provides the base interface for platform-specific media controllers
that integrate with the operating system's media transport controls:
- macOS: MPRemoteCommandCenter / MPNowPlayingInfoCenter
- Linux: MPRIS D-Bus interface
- Windows: SystemMediaTransportControls
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..player.base import TrackInfo

logger = logging.getLogger(__name__)


class MediaCommand(Enum):
    """Commands that can be received from OS media controls."""

    PLAY = "play"
    PAUSE = "pause"
    PLAY_PAUSE = "play_pause"
    STOP = "stop"
    NEXT = "next"
    PREVIOUS = "previous"
    SEEK_FORWARD = "seek_forward"
    SEEK_BACKWARD = "seek_backward"
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"


@dataclass
class MediaMetadata:
    """Metadata for currently playing track in OS media UI.

    This is a simplified representation of TrackInfo specifically
    for display in system media controls.
    """

    title: str = "Unknown"
    artist: str | None = None
    album: str | None = None
    duration: float | None = None  # Duration in seconds
    artwork_url: str | None = None  # URL or file path to artwork
    source_type: str = "unknown"  # local, radio, youtube, ai

    @classmethod
    def from_track_info(cls, track: TrackInfo | None) -> MediaMetadata:
        """Create MediaMetadata from a TrackInfo object."""
        if track is None:
            return cls()

        return cls(
            title=track.title or "Unknown",
            artist=track.artist,
            album=track.metadata.get("album") if track.metadata else None,
            duration=track.duration,
            artwork_url=track.metadata.get("thumbnail") if track.metadata else None,
            source_type=track.source_type,
        )


@dataclass
class MediaCapabilities:
    """Advertised capabilities of the media controller.

    Used to inform the OS which controls should be enabled/disabled.
    """

    can_play: bool = True
    can_pause: bool = True
    can_stop: bool = True
    can_next: bool = True
    can_previous: bool = False  # Not implemented (no queue)
    can_seek: bool = False  # FFplay limitation
    can_control_volume: bool = True


# Type alias for command handlers
MediaCommandHandler = Callable[[MediaCommand], Awaitable[None]]


class MediaController(ABC):
    """Abstract base class for OS-level media controls.

    Provides integration with operating system media transport controls,
    allowing users to control playback via:
    - Headphone buttons
    - Keyboard media keys
    - OS media widgets (lock screen, control center, etc.)

    Command flow: OS → MediaController → Daemon (via callback)
    Metadata flow: Daemon → MediaController → OS
    """

    def __init__(self) -> None:
        self._capabilities = MediaCapabilities()
        self._command_handler: MediaCommandHandler | None = None
        self._is_initialized = False

    @property
    def capabilities(self) -> MediaCapabilities:
        """Get the capabilities of this media controller."""
        return self._capabilities

    @property
    def is_initialized(self) -> bool:
        """Check if the controller has been initialized."""
        return self._is_initialized

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the media controller is available on this platform.

        Returns False if required platform libraries are not installed.
        """

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the media controller.

        This should:
        - Connect to the platform's media API
        - Register for media key events
        - Set up any required event loops

        Returns:
            True if initialization succeeded, False otherwise.
        """

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown and cleanup resources.

        This should:
        - Unregister from media key events
        - Release any platform resources
        - Clear now playing info
        """

    @abstractmethod
    async def update_metadata(self, metadata: MediaMetadata) -> None:
        """Update the now playing metadata in OS media UI.

        Args:
            metadata: Track metadata to display.
        """

    @abstractmethod
    async def update_playback_state(
        self,
        state: str,  # "playing", "paused", "stopped"
        position: float = 0.0,  # Current position in seconds
    ) -> None:
        """Update the playback state in OS media UI.

        Args:
            state: Current playback state.
            position: Current playback position (if available).
        """

    @abstractmethod
    async def update_volume(self, volume: int) -> None:
        """Update the volume level (0-100) in OS media UI.

        Note: Some platforms may not support volume display/control.

        Args:
            volume: Volume level from 0 to 100.
        """

    def set_command_handler(self, handler: MediaCommandHandler | None) -> None:
        """Set the callback for handling media commands from OS.

        Args:
            handler: Async function to call when a media command is received.
                     Pass None to unregister.
        """
        self._command_handler = handler

    async def _dispatch_command(self, command: MediaCommand) -> None:
        """Dispatch a command to the registered handler.

        Internal method called by platform implementations when
        a media key event is received.
        """
        if self._command_handler:
            try:
                await self._command_handler(command)
            except Exception as e:
                logger.error(f"Error handling media command {command}: {e}")


class NoOpMediaController(MediaController):
    """No-operation media controller for when platform support is unavailable.

    This implementation does nothing but logs warnings. It's used as a fallback
    when the required platform libraries are not installed or when running on
    an unsupported platform.
    """

    def __init__(self) -> None:
        super().__init__()
        self._warned = False

    @property
    def is_available(self) -> bool:
        """NoOp controller is always 'available' as a fallback."""
        return True

    async def initialize(self) -> bool:
        """Initialize (no-op)."""
        if not self._warned:
            logger.info("Media controller not available on this platform")
            self._warned = True
        self._is_initialized = True
        return True

    async def shutdown(self) -> None:
        """Shutdown (no-op)."""
        self._is_initialized = False

    async def update_metadata(self, metadata: MediaMetadata) -> None:
        """Update metadata (no-op)."""
        pass

    async def update_playback_state(self, state: str, position: float = 0.0) -> None:
        """Update playback state (no-op)."""
        pass

    async def update_volume(self, volume: int) -> None:
        """Update volume (no-op)."""
        pass
