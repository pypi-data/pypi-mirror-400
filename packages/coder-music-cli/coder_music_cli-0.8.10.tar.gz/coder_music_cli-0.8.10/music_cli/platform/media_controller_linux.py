"""Linux media controller using MPRIS D-Bus interface.

This module provides integration with Linux desktop environments via
the MPRIS (Media Player Remote Interfacing Specification) D-Bus interface.

MPRIS allows music-cli to:
- Appear in desktop media widgets (KDE, GNOME, etc.)
- Respond to media keys (play/pause/next)
- Display track metadata in notifications

Requires: dbus-next
Install: pip install dbus-next

Note: The dbus-next library uses string type annotations like "s", "b", "as"
as D-Bus type signatures. These are intentional and part of the library's API.
"""
# ruff: noqa: UP037, F821, F722

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

# MPRIS constants
MPRIS_BUS_NAME = "org.mpris.MediaPlayer2.music_cli"
MPRIS_OBJECT_PATH = "/org/mpris/MediaPlayer2"
MPRIS_INTERFACE = "org.mpris.MediaPlayer2"
MPRIS_PLAYER_INTERFACE = "org.mpris.MediaPlayer2.Player"

# Try to import D-Bus library
try:
    from dbus_next import BusType, Variant
    from dbus_next.aio import MessageBus
    from dbus_next.service import ServiceInterface, dbus_property, method

    DBUS_AVAILABLE = True
except ImportError:
    DBUS_AVAILABLE = False
    logger.debug("dbus-next not available")


if DBUS_AVAILABLE:

    class MPRISRootInterface(ServiceInterface):
        """MPRIS MediaPlayer2 root interface.

        Provides basic identity information about the media player.
        """

        def __init__(self) -> None:
            super().__init__(MPRIS_INTERFACE)

        @dbus_property()
        def Identity(self) -> "s":  # noqa: N802
            """Return the player identity."""
            return "music-cli"

        @dbus_property()
        def DesktopEntry(self) -> "s":  # noqa: N802
            """Return the desktop entry name."""
            return "music-cli"

        @dbus_property()
        def CanQuit(self) -> "b":  # noqa: N802
            """Whether the player can quit."""
            return False

        @dbus_property()
        def CanRaise(self) -> "b":  # noqa: N802
            """Whether the player can raise its window."""
            return False

        @dbus_property()
        def HasTrackList(self) -> "b":  # noqa: N802
            """Whether the player has a track list."""
            return False

        @dbus_property()
        def SupportedUriSchemes(self) -> "as":  # noqa: N802
            """Return supported URI schemes."""
            return ["file", "http", "https"]

        @dbus_property()
        def SupportedMimeTypes(self) -> "as":  # noqa: N802
            """Return supported MIME types."""
            return ["audio/mpeg", "audio/mp3", "audio/x-wav", "audio/ogg", "audio/flac"]

        @method()
        def Quit(self) -> None:  # noqa: N802
            """Quit the player (not supported)."""
            pass

        @method()
        def Raise(self) -> None:  # noqa: N802
            """Raise the player window (not supported - CLI app)."""
            pass

    class MPRISPlayerInterface(ServiceInterface):
        """MPRIS MediaPlayer2.Player interface.

        Handles playback control and metadata.
        """

        def __init__(self, controller: LinuxMediaController) -> None:
            super().__init__(MPRIS_PLAYER_INTERFACE)
            self._controller = controller
            self._metadata: dict[str, Any] = {}
            self._playback_status = "Stopped"
            self._volume = 0.8
            self._position = 0

        def update_metadata(self, metadata: MediaMetadata) -> None:
            """Update the stored metadata."""
            mpris_metadata: dict[str, Any] = {
                "mpris:trackid": Variant(
                    "o", f"/org/mpris/MediaPlayer2/Track/{hash(metadata.title or 'unknown')}"
                ),
            }

            if metadata.title:
                mpris_metadata["xesam:title"] = Variant("s", metadata.title)

            if metadata.artist:
                mpris_metadata["xesam:artist"] = Variant("as", [metadata.artist])

            if metadata.album:
                mpris_metadata["xesam:album"] = Variant("s", metadata.album)

            if metadata.duration is not None and metadata.duration > 0:
                # MPRIS uses microseconds
                mpris_metadata["mpris:length"] = Variant("x", int(metadata.duration * 1_000_000))

            if metadata.artwork_url:
                mpris_metadata["mpris:artUrl"] = Variant("s", metadata.artwork_url)

            self._metadata = mpris_metadata

        def update_playback_status(self, status: str) -> None:
            """Update playback status (Playing, Paused, Stopped)."""
            status_map = {
                "playing": "Playing",
                "paused": "Paused",
                "stopped": "Stopped",
            }
            self._playback_status = status_map.get(status, "Stopped")

        def update_volume(self, volume: int) -> None:
            """Update volume (0-100 to 0.0-1.0)."""
            self._volume = volume / 100.0

        # D-Bus properties

        @dbus_property()
        def PlaybackStatus(self) -> "s":  # noqa: N802
            """Return current playback status."""
            return self._playback_status

        @dbus_property()
        def Metadata(self) -> "a{sv}":  # noqa: N802
            """Return current track metadata."""
            return self._metadata

        @dbus_property()
        def Volume(self) -> "d":  # noqa: N802
            """Return current volume (0.0 to 1.0)."""
            return self._volume

        @Volume.setter  # type: ignore[no-redef]
        def Volume(self, value: "d") -> None:  # noqa: N802
            """Set volume (triggers command to daemon)."""
            old_volume = self._volume
            self._volume = value
            # Note: Volume changes from D-Bus are not currently propagated
            # to the daemon because FFplay doesn't support runtime volume changes.
            # This setter updates the internal state for D-Bus property consistency.
            logger.debug(f"MPRIS volume changed: {old_volume:.2f} -> {value:.2f}")

        @dbus_property()
        def Position(self) -> "x":  # noqa: N802
            """Return current position in microseconds."""
            return self._position

        @dbus_property()
        def Rate(self) -> "d":  # noqa: N802
            """Return playback rate (always 1.0)."""
            return 1.0

        @dbus_property()
        def MinimumRate(self) -> "d":  # noqa: N802
            """Return minimum playback rate."""
            return 1.0

        @dbus_property()
        def MaximumRate(self) -> "d":  # noqa: N802
            """Return maximum playback rate."""
            return 1.0

        @dbus_property()
        def CanGoNext(self) -> "b":  # noqa: N802
            """Whether we can go to next track."""
            return True

        @dbus_property()
        def CanGoPrevious(self) -> "b":  # noqa: N802
            """Whether we can go to previous track."""
            return False  # No queue management

        @dbus_property()
        def CanPlay(self) -> "b":  # noqa: N802
            """Whether we can play."""
            return True

        @dbus_property()
        def CanPause(self) -> "b":  # noqa: N802
            """Whether we can pause."""
            return True

        @dbus_property()
        def CanSeek(self) -> "b":  # noqa: N802
            """Whether we can seek."""
            return False  # FFplay limitation

        @dbus_property()
        def CanControl(self) -> "b":  # noqa: N802
            """Whether we can control playback."""
            return True

        # D-Bus methods

        @method()
        def Play(self) -> None:  # noqa: N802
            """Start/resume playback."""
            self._dispatch_command(MediaCommand.PLAY)

        @method()
        def Pause(self) -> None:  # noqa: N802
            """Pause playback."""
            self._dispatch_command(MediaCommand.PAUSE)

        @method()
        def PlayPause(self) -> None:  # noqa: N802
            """Toggle play/pause."""
            self._dispatch_command(MediaCommand.PLAY_PAUSE)

        @method()
        def Stop(self) -> None:  # noqa: N802
            """Stop playback."""
            self._dispatch_command(MediaCommand.STOP)

        @method()
        def Next(self) -> None:  # noqa: N802
            """Skip to next track."""
            self._dispatch_command(MediaCommand.NEXT)

        @method()
        def Previous(self) -> None:  # noqa: N802
            """Go to previous track (not implemented)."""
            pass  # No queue management

        @method()
        def Seek(self, offset: "x") -> None:  # noqa: N802
            """Seek by offset (not supported)."""
            pass  # FFplay limitation

        @method()
        def SetPosition(self, track_id: "o", position: "x") -> None:  # noqa: N802
            """Set position (not supported)."""
            pass  # FFplay limitation

        def _dispatch_command(self, command: MediaCommand) -> None:
            """Dispatch command to controller (thread-safe)."""
            loop = self._controller._loop
            if loop and loop.is_running():
                loop.call_soon_threadsafe(
                    lambda: loop.create_task(self._controller._dispatch_command(command))
                )
            else:
                logger.warning(f"No event loop for MPRIS command: {command}")


class LinuxMediaController(MediaController):
    """Linux implementation using MPRIS D-Bus interface.

    Exports an MPRIS-compatible service on the session bus, allowing
    integration with desktop environments like:
    - GNOME (Media controls extension)
    - KDE Plasma (Media Player applet)
    - playerctl command-line tool
    """

    def __init__(self) -> None:
        super().__init__()
        self._bus: Any = None
        self._root_interface: Any = None
        self._player_interface: Any = None

        # Store event loop reference for thread-safe callbacks
        self._loop: asyncio.AbstractEventLoop | None = None

        # Update capabilities for MPRIS
        self._capabilities = MediaCapabilities(
            can_play=True,
            can_pause=True,
            can_stop=True,
            can_next=True,
            can_previous=False,  # No queue management
            can_seek=False,  # FFplay limitation
            can_control_volume=True,
        )

    @property
    def is_available(self) -> bool:
        """Check if D-Bus library is available."""
        return DBUS_AVAILABLE

    async def initialize(self) -> bool:
        """Initialize MPRIS D-Bus service.

        Connects to the session bus and exports MPRIS interfaces.
        """
        if not DBUS_AVAILABLE:
            logger.warning("dbus-next not available. Install with: pip install dbus-next")
            return False

        try:
            # Store event loop for thread-safe callbacks
            self._loop = asyncio.get_running_loop()

            # Connect to session bus
            self._bus = await MessageBus(bus_type=BusType.SESSION).connect()

            # Create and export interfaces
            self._root_interface = MPRISRootInterface()
            self._player_interface = MPRISPlayerInterface(self)

            self._bus.export(MPRIS_OBJECT_PATH, self._root_interface)
            self._bus.export(MPRIS_OBJECT_PATH, self._player_interface)

            # Request bus name
            await self._bus.request_name(MPRIS_BUS_NAME)

            self._is_initialized = True
            logger.info(f"Linux MPRIS media controller initialized: {MPRIS_BUS_NAME}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize MPRIS controller: {e}")
            return False

    async def shutdown(self) -> None:
        """Shutdown MPRIS D-Bus service."""
        if not self._is_initialized:
            return

        try:
            if self._bus:
                # Release bus name
                await self._bus.release_name(MPRIS_BUS_NAME)
                self._bus.disconnect()

            self._is_initialized = False
            logger.info("Linux MPRIS media controller shutdown")

        except Exception as e:
            logger.error(f"Error during MPRIS shutdown: {e}")

    async def update_metadata(self, metadata: MediaMetadata) -> None:
        """Update MPRIS metadata."""
        if not self._player_interface:
            return

        try:
            self._player_interface.update_metadata(metadata)
            # Emit PropertiesChanged signal
            if self._bus:
                self._player_interface.emit_properties_changed({"Metadata": None})
            logger.debug(f"Updated MPRIS metadata: {metadata.title}")

        except Exception as e:
            logger.error(f"Failed to update MPRIS metadata: {e}")

    async def update_playback_state(self, state: str, position: float = 0.0) -> None:
        """Update MPRIS playback status."""
        if not self._player_interface:
            return

        try:
            self._player_interface.update_playback_status(state)
            self._player_interface._position = int(position * 1_000_000)  # microseconds

            # Emit PropertiesChanged signal
            if self._bus:
                self._player_interface.emit_properties_changed({"PlaybackStatus": None})

            logger.debug(f"Updated MPRIS playback state: {state}")

        except Exception as e:
            logger.error(f"Failed to update MPRIS playback state: {e}")

    async def update_volume(self, volume: int) -> None:
        """Update MPRIS volume."""
        if not self._player_interface:
            return

        try:
            self._player_interface.update_volume(volume)

            # Emit PropertiesChanged signal
            if self._bus:
                self._player_interface.emit_properties_changed({"Volume": None})

            logger.debug(f"Updated MPRIS volume: {volume}%")

        except Exception as e:
            logger.error(f"Failed to update MPRIS volume: {e}")
