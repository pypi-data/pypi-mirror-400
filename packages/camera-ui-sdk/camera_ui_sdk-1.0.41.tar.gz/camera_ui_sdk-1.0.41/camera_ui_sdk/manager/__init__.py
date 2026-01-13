from __future__ import annotations

from typing import TYPE_CHECKING, Literal, NotRequired, Protocol, TypedDict, runtime_checkable

if TYPE_CHECKING:
    from ..camera import CameraDevice
    from ..plugin import BasePlugin


ConnectionStatus = Literal["idle", "connecting", "connected", "error"]
"""Connection status for discovered cameras."""


@runtime_checkable
class CoreManager(Protocol):
    """
    Core manager interface for system operations.

    Provides access to system-level functionality like FFmpeg path,
    server addresses, and inter-plugin communication.

    Accessed via `api.coreManager` in plugins.

    Example:
        ```python
        # Get FFmpeg path for spawning processes
        ffmpeg_path = await api.coreManager.getFFmpegPath()

        # Get server addresses for stream URLs
        addresses = await api.coreManager.getServerAddresses()
        ```
    """

    async def connectToPlugin(self, pluginName: str) -> BasePlugin | None:
        """
        Connect to another plugin by name.

        Args:
            pluginName: Name of the plugin to connect to

        Returns:
            Plugin instance or None if not found. Cast to specific interface as needed.
        """
        ...

    async def getFFmpegPath(self) -> str:
        """
        Get the FFmpeg executable path.

        Returns:
            Path to FFmpeg binary
        """
        ...

    async def getServerAddresses(self) -> list[str]:
        """
        Get server addresses (IP addresses the server is listening on).

        Returns:
            List of server addresses
        """
        ...


@runtime_checkable
class DeviceManager(Protocol):
    """
    Device manager interface for camera operations.

    Provides methods to get cameras and push discovered cameras.
    Camera lifecycle is managed via BasePlugin callbacks (on_camera_added, on_camera_released).

    Accessed via `api.deviceManager` in plugins.

    Example:
        ```python
        # Get a camera by ID or name
        camera = await api.deviceManager.getCamera("Front Door")

        # Push discovered cameras (for cloud-based discovery)
        discovered = await fetch_cameras_from_cloud()
        await api.deviceManager.pushDiscoveredCameras(discovered)
        ```
    """

    async def pushDiscoveredCameras(self, cameras: list[DiscoveredCamera]) -> None:
        """
        Push discovered cameras to the backend.
        Use this when cameras are discovered asynchronously (e.g., after cloud login).
        Cameras will be immediately visible in the UI for adoption.

        Args:
            cameras: List of discovered cameras to push
        """
        ...

    async def getCamera(self, cameraIdOrName: str) -> CameraDevice | None:
        """
        Get a camera by ID or name.

        Args:
            cameraIdOrName: Camera ID or name

        Returns:
            Camera device or None if not found
        """
        ...


class DiscoveredCamera(TypedDict):
    """
    Discovered camera from a discovery provider.

    Represents a camera found during network scanning that can be
    connected to and added to the system.
    """

    id: str
    """Unique identifier for this discovered camera."""

    name: str
    """Display name of the camera."""

    manufacturer: NotRequired[str]
    """Camera manufacturer (optional)."""

    model: NotRequired[str]
    """Camera model (optional)."""


class DiscoveredCameraWithState(DiscoveredCamera):
    """
    Discovered camera with connection state.

    Extended version of DiscoveredCamera that includes connection
    status information for UI display.
    """

    provider: str
    """Provider plugin name."""

    connectionStatus: ConnectionStatus
    """Current connection status."""

    errorMessage: NotRequired[str]
    """Error message if connection failed."""


__all__ = [
    # Status type
    "ConnectionStatus",
    # Manager interfaces
    "CoreManager",
    "DeviceManager",
    # Discovery types
    "DiscoveredCamera",
    "DiscoveredCameraWithState",
]
