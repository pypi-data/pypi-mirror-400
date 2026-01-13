from __future__ import annotations

from collections.abc import Awaitable, Callable
from enum import Enum
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from ..manager import CoreManager, DeviceManager, DiscoveryManager
    from ..storage import StorageController

APIListener = Callable[[], None] | Callable[[], Awaitable[None]]
"""Plugin API event listener type (sync or async)."""


class API_EVENT(Enum):
    """Plugin API event types."""

    FINISH_LAUNCHING = "finishLaunching"
    """Emitted when plugin initialization is complete."""

    SHUTDOWN = "shutdown"
    """Emitted when plugin is shutting down."""


@runtime_checkable
class PluginAPI(Protocol):
    """
    Plugin API - injected into plugins at runtime.

    Provides access to system services and managers. The API is passed
    to the plugin constructor and should be stored for later use.

    Example:
        ```python
        class MyPlugin(BasePlugin):
            def __init__(self, logger, api, storage):
                super().__init__(logger, api, storage)
                # Access FFmpeg path
                ffmpeg = await api.coreManager.getFFmpegPath()
        ```
    """

    @property
    def coreManager(self) -> CoreManager:
        """Core manager for system operations (FFmpeg path, server addresses)."""
        ...

    @property
    def deviceManager(self) -> DeviceManager:
        """Device manager for camera CRUD operations."""
        ...

    @property
    def discoveryManager(self) -> DiscoveryManager:
        """Discovery manager for camera discovery (CameraController roles only)."""
        ...

    @property
    def storageController(self) -> StorageController:
        """Storage controller for persistent plugin configuration."""
        ...

    @property
    def storagePath(self) -> str:
        """Path to plugin storage directory."""
        ...

    def on(self, event: API_EVENT, f: APIListener) -> Any:
        """
        Subscribe to plugin lifecycle events.

        Args:
            event: Event type to subscribe to
            f: Event listener function (sync or async)

        Returns:
            Self for chaining
        """
        ...

    def once(self, event: API_EVENT, f: APIListener) -> Any:
        """
        Subscribe to plugin lifecycle events (once).

        Args:
            event: Event type to subscribe to
            f: Event listener function (sync or async)

        Returns:
            Self for chaining
        """
        ...

    def off(self, event: API_EVENT, f: APIListener) -> None:
        """
        Unsubscribe from plugin lifecycle events.

        Args:
            event: Event type to unsubscribe from
            f: Event listener function to remove
        """
        ...

    def removeListener(self, event: API_EVENT, f: APIListener) -> None:
        """
        Remove event listener.

        Args:
            event: Event type
            f: Event listener function to remove
        """
        ...

    def removeAllListeners(self, event: API_EVENT | None = None) -> None:
        """
        Remove all listeners for an event.

        Args:
            event: Optional event type (removes all if not specified)
        """
        ...
