"""Windows media controller using SystemMediaTransportControls.

This module provides integration with Windows media controls via
SystemMediaTransportControls (SMTC), allowing music-cli to:
- Appear in Windows media overlay
- Respond to media keys (play/pause/next)
- Display track metadata in system UI

Requires: winrt-Windows.Media.Playback
Install: pip install winrt-Windows.Media.Playback
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from .media_controller import (
    MediaCapabilities,
    MediaCommand,
    MediaController,
    MediaMetadata,
)

logger = logging.getLogger(__name__)

# Try to import Windows Runtime libraries
try:
    from winrt.windows.media import (
        MediaPlaybackStatus,
        MediaPlaybackType,
        SystemMediaTransportControls,
        SystemMediaTransportControlsButton,
        SystemMediaTransportControlsButtonPressedEventArgs,
    )
    from winrt.windows.media.playback import MediaPlayer

    WINRT_AVAILABLE = True
except ImportError:
    WINRT_AVAILABLE = False
    logger.debug("winrt-Windows.Media not available")


class WindowsMediaController(MediaController):
    """Windows implementation using SystemMediaTransportControls.

    Integrates with Windows 10/11 media controls including:
    - Media overlay (shows on volume change)
    - Keyboard media keys
    - Bluetooth headphone controls
    - Lock screen media controls

    Note: Windows SMTC requires a MediaPlayer instance to access
    the system transport controls. We create one internally but
    don't use it for actual playback (FFplay handles that).
    """

    def __init__(self) -> None:
        super().__init__()
        self._media_player: Any = None
        self._smtc: Any = None
        self._display_updater: Any = None
        self._current_metadata: MediaMetadata | None = None

        # Store event loop reference for thread-safe callbacks
        self._loop: asyncio.AbstractEventLoop | None = None

        # Update capabilities for Windows
        self._capabilities = MediaCapabilities(
            can_play=True,
            can_pause=True,
            can_stop=True,
            can_next=True,
            can_previous=False,  # No queue management
            can_seek=False,  # FFplay limitation
            can_control_volume=False,  # Volume handled by system
        )

    @property
    def is_available(self) -> bool:
        """Check if Windows Runtime libraries are available."""
        return WINRT_AVAILABLE

    async def initialize(self) -> bool:
        """Initialize Windows media controller.

        Creates a MediaPlayer instance to access SystemMediaTransportControls
        and registers button event handlers.
        """
        if not WINRT_AVAILABLE:
            logger.warning(
                "Windows Runtime not available. "
                "Install with: pip install winrt-Windows.Media.Playback"
            )
            return False

        try:
            # Store event loop for thread-safe callbacks
            self._loop = asyncio.get_running_loop()

            # Create MediaPlayer to get access to SMTC
            self._media_player = MediaPlayer()
            self._smtc = self._media_player.system_media_transport_controls
            self._display_updater = self._smtc.display_updater

            # Disable automatic CommandManager (we handle commands manually)
            self._media_player.command_manager.is_enabled = False

            # Enable SMTC
            self._smtc.is_enabled = True

            # Configure enabled buttons
            self._smtc.is_play_enabled = True
            self._smtc.is_pause_enabled = True
            self._smtc.is_stop_enabled = True
            self._smtc.is_next_enabled = self._capabilities.can_next
            self._smtc.is_previous_enabled = False  # No queue

            # Disable seek buttons (FFplay limitation)
            self._smtc.is_fast_forward_enabled = False
            self._smtc.is_rewind_enabled = False

            # Register button handler
            self._smtc.add_button_pressed(self._on_button_pressed)

            # Set media type to music
            self._display_updater.type = MediaPlaybackType.MUSIC

            self._is_initialized = True
            logger.info("Windows media controller initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Windows media controller: {e}")
            return False

    def _on_button_pressed(
        self,
        sender: SystemMediaTransportControls,
        args: SystemMediaTransportControlsButtonPressedEventArgs,
    ) -> None:
        """Handle button press events from Windows media controls."""
        button = args.button

        # Map Windows buttons to our commands
        # Use PLAY_PAUSE for both play and pause buttons - the daemon handles toggle logic
        command_map = {
            SystemMediaTransportControlsButton.PLAY: MediaCommand.PLAY_PAUSE,
            SystemMediaTransportControlsButton.PAUSE: MediaCommand.PLAY_PAUSE,
            SystemMediaTransportControlsButton.STOP: MediaCommand.STOP,
            SystemMediaTransportControlsButton.NEXT: MediaCommand.NEXT,
            SystemMediaTransportControlsButton.PREVIOUS: MediaCommand.PREVIOUS,
            SystemMediaTransportControlsButton.FAST_FORWARD: MediaCommand.SEEK_FORWARD,
            SystemMediaTransportControlsButton.REWIND: MediaCommand.SEEK_BACKWARD,
        }

        command = command_map.get(button)
        if command:
            # Dispatch command on event loop (thread-safe)
            if self._loop and self._loop.is_running():
                self._loop.call_soon_threadsafe(
                    lambda cmd=command: self._loop.create_task(self._dispatch_command(cmd))
                )
            else:
                logger.warning(f"No event loop for Windows media command: {command}")

    async def shutdown(self) -> None:
        """Shutdown Windows media controller."""
        if not self._is_initialized:
            return

        try:
            if self._smtc:
                self._smtc.is_enabled = False

            if self._display_updater:
                self._display_updater.clear_all()

            self._is_initialized = False
            logger.info("Windows media controller shutdown")

        except Exception as e:
            logger.error(f"Error during Windows media controller shutdown: {e}")

    async def update_metadata(self, metadata: MediaMetadata) -> None:
        """Update Windows media overlay metadata."""
        if not self._display_updater:
            return

        self._current_metadata = metadata

        try:
            # Set media type
            self._display_updater.type = MediaPlaybackType.MUSIC

            # Update music properties
            music_props = self._display_updater.music_properties

            if metadata.title:
                music_props.title = metadata.title

            if metadata.artist:
                music_props.artist = metadata.artist

            if metadata.album:
                music_props.album_title = metadata.album

            # Commit the update
            self._display_updater.update()

            logger.debug(f"Updated Windows media metadata: {metadata.title}")

        except Exception as e:
            logger.error(f"Failed to update Windows media metadata: {e}")

    async def update_playback_state(self, state: str, position: float = 0.0) -> None:
        """Update Windows media playback status."""
        if not self._smtc:
            return

        try:
            # Map state to Windows MediaPlaybackStatus
            state_map = {
                "playing": MediaPlaybackStatus.PLAYING,
                "paused": MediaPlaybackStatus.PAUSED,
                "stopped": MediaPlaybackStatus.STOPPED,
                "loading": MediaPlaybackStatus.CHANGING,
            }

            playback_status = state_map.get(state, MediaPlaybackStatus.STOPPED)
            self._smtc.playback_status = playback_status

            logger.debug(f"Updated Windows playback state: {state}")

        except Exception as e:
            logger.error(f"Failed to update Windows playback state: {e}")

    async def update_volume(self, volume: int) -> None:
        """Update volume (not directly controlled via SMTC).

        Windows system volume is controlled separately.
        SMTC shows the system volume, not app-specific volume.
        """
        # Windows SMTC doesn't have a volume property we can set
        # The volume shown in the overlay is the system volume
        pass
