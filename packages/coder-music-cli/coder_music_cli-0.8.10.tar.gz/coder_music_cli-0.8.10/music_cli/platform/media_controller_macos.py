"""macOS media controller using MediaPlayer framework.

This module provides integration with macOS media controls via:
- MPRemoteCommandCenter: Handle media key events (play/pause/next/etc.)
- MPNowPlayingInfoCenter: Display track metadata in Now Playing UI

Requires: pyobjc-framework-MediaPlayer
Install: pip install pyobjc-framework-MediaPlayer

IMPORTANT LIMITATION:
macOS's Now Playing system attributes playback to the process that owns the
audio session. Since music-cli uses ffplay (an external subprocess) to play
audio, macOS sees ffplay as the audio source, not music-cli.

This means:
- MPNowPlayingInfoCenter updates are sent but macOS ignores them
- The Now Playing widget will show whatever app actually owns the audio
- Media key events may not be routed to music-cli

For full macOS media control support, the audio playback would need to be
done within the Python process using AVFoundation or similar.

The Linux MPRIS implementation does not have this limitation because MPRIS
is a D-Bus interface that any application can register with, regardless of
audio ownership.
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

# Try to import macOS frameworks
try:
    from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
    from Foundation import NSDate, NSMutableDictionary, NSRunLoop
    from MediaPlayer import (
        MPMediaItemPropertyAlbumTitle,
        MPMediaItemPropertyArtist,
        MPMediaItemPropertyPlaybackDuration,
        MPMediaItemPropertyTitle,
        MPNowPlayingInfoCenter,
        MPNowPlayingInfoPropertyElapsedPlaybackTime,
        MPNowPlayingInfoPropertyPlaybackRate,
        MPNowPlayingPlaybackStatePaused,
        MPNowPlayingPlaybackStatePlaying,
        MPNowPlayingPlaybackStateStopped,
        MPRemoteCommandCenter,
        MPRemoteCommandHandlerStatusSuccess,
    )

    MACOS_AVAILABLE = True
except ImportError:
    MACOS_AVAILABLE = False
    logger.debug("pyobjc-framework-MediaPlayer not available")


class MacOSMediaController(MediaController):
    """macOS implementation using MPRemoteCommandCenter.

    Integrates with macOS media controls including:
    - Touch Bar media controls
    - Control Center Now Playing widget
    - Headphone button events
    - Keyboard media keys

    Note: On macOS, you need to explicitly set playback state on
    MPNowPlayingInfoCenter - it doesn't infer from AVAudioSession
    like on iOS.
    """

    def __init__(self) -> None:
        super().__init__()
        self._command_center: Any = None
        self._now_playing_center: Any = None
        self._current_metadata: MediaMetadata | None = None
        self._current_state = "stopped"

        # Store command targets to prevent garbage collection
        self._command_targets: dict[str, Any] = {}

        # Store event loop reference for thread-safe callbacks
        self._loop: asyncio.AbstractEventLoop | None = None

        # Background task for NSRunLoop
        self._runloop_task: asyncio.Task | None = None

        # Update capabilities - macOS supports most controls
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
        """Check if macOS MediaPlayer framework is available."""
        return MACOS_AVAILABLE

    async def initialize(self) -> bool:
        """Initialize macOS media controller.

        Sets up an NSApplication (required for Now Playing), registers
        command handlers with MPRemoteCommandCenter, and prepares
        MPNowPlayingInfoCenter for metadata updates.
        """
        if not MACOS_AVAILABLE:
            logger.warning(
                "macOS MediaPlayer framework not available. "
                "Install with: pip install pyobjc-framework-MediaPlayer"
            )
            return False

        try:
            # Store event loop for thread-safe callbacks
            self._loop = asyncio.get_running_loop()

            # Create/get NSApplication instance - required for Now Playing to work
            # Use accessory policy so the app doesn't appear in Dock
            app = NSApplication.sharedApplication()
            app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)

            # Get shared instances
            self._command_center = MPRemoteCommandCenter.sharedCommandCenter()
            self._now_playing_center = MPNowPlayingInfoCenter.defaultCenter()

            # Register command handlers
            self._register_commands()

            # Start a background task to pump the run loop for events
            self._runloop_task = asyncio.create_task(self._run_nsrunloop())

            self._is_initialized = True
            logger.info("macOS media controller initialized with NSApplication")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize macOS media controller: {e}")
            return False

    async def _run_nsrunloop(self) -> None:
        """Run NSRunLoop periodically to process media events.

        This is required for the command center to receive events.
        """
        try:
            while self._is_initialized:
                # Process pending events in the run loop
                run_loop = NSRunLoop.currentRunLoop()
                # Run the loop for a short time to process events
                until_date = NSDate.dateWithTimeIntervalSinceNow_(0.1)
                run_loop.runUntilDate_(until_date)
                # Yield to asyncio
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.debug(f"NSRunLoop task ended: {e}")

    def _register_commands(self) -> None:
        """Register handlers for media commands."""
        if not self._command_center:
            return

        # Play command
        play_cmd = self._command_center.playCommand()
        play_cmd.setEnabled_(True)
        self._command_targets["play"] = self._create_handler(MediaCommand.PLAY)
        play_cmd.addTargetWithHandler_(self._command_targets["play"])

        # Pause command
        pause_cmd = self._command_center.pauseCommand()
        pause_cmd.setEnabled_(True)
        self._command_targets["pause"] = self._create_handler(MediaCommand.PAUSE)
        pause_cmd.addTargetWithHandler_(self._command_targets["pause"])

        # Toggle play/pause command (headphone button)
        toggle_cmd = self._command_center.togglePlayPauseCommand()
        toggle_cmd.setEnabled_(True)
        self._command_targets["toggle"] = self._create_handler(MediaCommand.PLAY_PAUSE)
        toggle_cmd.addTargetWithHandler_(self._command_targets["toggle"])

        # Stop command
        stop_cmd = self._command_center.stopCommand()
        stop_cmd.setEnabled_(True)
        self._command_targets["stop"] = self._create_handler(MediaCommand.STOP)
        stop_cmd.addTargetWithHandler_(self._command_targets["stop"])

        # Next track command
        next_cmd = self._command_center.nextTrackCommand()
        next_cmd.setEnabled_(self._capabilities.can_next)
        if self._capabilities.can_next:
            self._command_targets["next"] = self._create_handler(MediaCommand.NEXT)
            next_cmd.addTargetWithHandler_(self._command_targets["next"])

        # Previous track command (disabled - no queue)
        prev_cmd = self._command_center.previousTrackCommand()
        prev_cmd.setEnabled_(False)

        # Disable seek commands (FFplay limitation)
        self._command_center.seekForwardCommand().setEnabled_(False)
        self._command_center.seekBackwardCommand().setEnabled_(False)
        self._command_center.changePlaybackPositionCommand().setEnabled_(False)

        # Disable skip commands
        self._command_center.skipForwardCommand().setEnabled_(False)
        self._command_center.skipBackwardCommand().setEnabled_(False)

    def _create_handler(self, command: MediaCommand):
        """Create an Objective-C compatible handler for a command.

        Returns a callable that MPRemoteCommandCenter can use as a target.
        """

        def handler(event):
            # Schedule the async handler on the event loop (thread-safe)
            if self._loop and self._loop.is_running():
                self._loop.call_soon_threadsafe(
                    lambda: self._loop.create_task(self._dispatch_command(command))
                )
            else:
                logger.warning(f"No event loop for media command: {command}")
            return MPRemoteCommandHandlerStatusSuccess

        return handler

    async def shutdown(self) -> None:
        """Shutdown macOS media controller."""
        if not self._is_initialized:
            return

        self._is_initialized = False

        try:
            # Cancel the run loop task
            if self._runloop_task:
                self._runloop_task.cancel()
                try:
                    await self._runloop_task
                except asyncio.CancelledError:
                    pass
                self._runloop_task = None

            # Clear now playing info
            if self._now_playing_center:
                self._now_playing_center.setNowPlayingInfo_(None)
                # Set playback state to stopped
                self._now_playing_center.setPlaybackState_(MPNowPlayingPlaybackStateStopped)

            # Disable commands
            if self._command_center:
                self._command_center.playCommand().setEnabled_(False)
                self._command_center.pauseCommand().setEnabled_(False)
                self._command_center.togglePlayPauseCommand().setEnabled_(False)
                self._command_center.stopCommand().setEnabled_(False)
                self._command_center.nextTrackCommand().setEnabled_(False)

            self._command_targets.clear()
            logger.info("macOS media controller shutdown")

        except Exception as e:
            logger.error(f"Error during macOS media controller shutdown: {e}")

    async def update_metadata(self, metadata: MediaMetadata) -> None:
        """Update Now Playing metadata."""
        if not self._now_playing_center:
            return

        self._current_metadata = metadata

        try:
            # Create mutable dictionary for now playing info
            info = NSMutableDictionary.dictionary()

            # Set track metadata
            if metadata.title:
                info[MPMediaItemPropertyTitle] = metadata.title

            if metadata.artist:
                info[MPMediaItemPropertyArtist] = metadata.artist

            if metadata.album:
                info[MPMediaItemPropertyAlbumTitle] = metadata.album

            if metadata.duration is not None and metadata.duration > 0:
                info[MPMediaItemPropertyPlaybackDuration] = metadata.duration

            # Set playback rate based on current state
            playback_rate = 1.0 if self._current_state == "playing" else 0.0
            info[MPNowPlayingInfoPropertyPlaybackRate] = playback_rate

            # Set elapsed time to 0 (we don't track position with FFplay)
            info[MPNowPlayingInfoPropertyElapsedPlaybackTime] = 0.0

            # Update now playing info
            self._now_playing_center.setNowPlayingInfo_(info)

            logger.debug(f"Updated macOS now playing: {metadata.title}")

        except Exception as e:
            logger.error(f"Failed to update macOS now playing metadata: {e}")

    async def update_playback_state(self, state: str, position: float = 0.0) -> None:
        """Update playback state in macOS Now Playing."""
        if not self._now_playing_center:
            return

        self._current_state = state

        try:
            # Map state to MPNowPlayingPlaybackState constants
            state_map = {
                "playing": MPNowPlayingPlaybackStatePlaying,
                "paused": MPNowPlayingPlaybackStatePaused,
                "stopped": MPNowPlayingPlaybackStateStopped,
            }

            playback_state = state_map.get(state, MPNowPlayingPlaybackStateStopped)
            self._now_playing_center.setPlaybackState_(playback_state)

            # Update playback rate in now playing info
            current_info = self._now_playing_center.nowPlayingInfo()
            if current_info:
                info = NSMutableDictionary.dictionaryWithDictionary_(current_info)
                playback_rate = 1.0 if state == "playing" else 0.0
                info[MPNowPlayingInfoPropertyPlaybackRate] = playback_rate
                info[MPNowPlayingInfoPropertyElapsedPlaybackTime] = position
                self._now_playing_center.setNowPlayingInfo_(info)

            logger.debug(f"Updated macOS playback state: {state}")

        except Exception as e:
            logger.error(f"Failed to update macOS playback state: {e}")

    async def update_volume(self, volume: int) -> None:
        """Update volume (not directly supported on macOS).

        macOS system volume is controlled separately from app volume.
        The Now Playing UI shows system volume, not app volume.
        """
        # Volume control is handled by the system on macOS
        # We don't need to do anything here
        pass
