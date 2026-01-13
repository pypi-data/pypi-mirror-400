from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from enum import Enum
from typing import TYPE_CHECKING, Any, Literal, NotRequired, Protocol, TypedDict, overload, runtime_checkable

if TYPE_CHECKING:
    from ..camera import CameraConfig, CameraConfigPartial, CameraDevice
    from ..plugin import BasePlugin
    from ..storage import JsonSchemaWithoutCallbacks


class DEVICE_MANAGER_EVENT(Enum):
    """Device manager event types."""

    CAMERA_SELECTED = "cameraSelected"
    """Emitted when a camera is selected/assigned to plugin."""

    CAMERA_DESELECTED = "cameraDeselected"
    """Emitted when a camera is deselected/unassigned from plugin."""


DeviceManagerSelectedListener = Callable[["CameraDevice"], None] | Callable[["CameraDevice"], Awaitable[None]]
"""Listener type for camera selected events."""

DeviceManagerDeselectedListener = Callable[[str], None] | Callable[[str], Awaitable[None]]
"""Listener type for camera deselected events."""

DeviceManagerListener = DeviceManagerSelectedListener | DeviceManagerDeselectedListener
"""Union type for all device manager listeners."""

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
    Device manager interface for camera CRUD operations.

    Provides methods to create, read, update, and delete cameras.
    Also emits events when cameras are selected/deselected for the plugin.

    Accessed via `api.deviceManager` in plugins.

    Example:
        ```python
        # Create a new camera
        camera = await api.deviceManager.createCamera(
            {"name": "Front Door", "videoConfig": {"source": "rtsp://..."}}
        )

        # Listen for camera selection events
        api.deviceManager.on(
            DEVICE_MANAGER_EVENT.CAMERA_SELECTED, lambda camera: (print(f"Camera selected: {camera.name}"))
        )
        ```
    """

    async def createCamera(self, cameraConfig: CameraConfig) -> CameraDevice:
        """
        Create a new camera.

        Args:
            cameraConfig: Camera configuration

        Returns:
            The created camera device
        """
        ...

    async def updateCamera(self, cameraIdOrName: str, cameraConfig: CameraConfigPartial) -> CameraDevice:
        """
        Update an existing camera.

        Args:
            cameraIdOrName: Camera ID or name
            cameraConfig: Partial configuration to update

        Returns:
            The updated camera device
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

    async def removeCamera(self, cameraIdOrName: str) -> None:
        """
        Remove a camera.

        Args:
            cameraIdOrName: Camera ID or name
        """
        ...

    @overload
    def on(
        self,
        event: Literal[DEVICE_MANAGER_EVENT.CAMERA_DESELECTED],
        listener: DeviceManagerDeselectedListener,
    ) -> Any: ...
    @overload
    def on(
        self, event: Literal[DEVICE_MANAGER_EVENT.CAMERA_SELECTED], listener: DeviceManagerSelectedListener
    ) -> Any: ...
    def on(self, event: DEVICE_MANAGER_EVENT, listener: DeviceManagerListener) -> Any:
        """Subscribe to device manager events."""
        ...

    @overload
    def once(
        self,
        event: Literal[DEVICE_MANAGER_EVENT.CAMERA_DESELECTED],
        listener: DeviceManagerDeselectedListener,
    ) -> Any: ...
    @overload
    def once(
        self, event: Literal[DEVICE_MANAGER_EVENT.CAMERA_SELECTED], listener: DeviceManagerSelectedListener
    ) -> Any: ...
    def once(self, event: DEVICE_MANAGER_EVENT, listener: DeviceManagerListener) -> Any:
        """Subscribe to device manager events (once)."""
        ...

    @overload
    def off(
        self,
        event: Literal[DEVICE_MANAGER_EVENT.CAMERA_DESELECTED],
        listener: DeviceManagerDeselectedListener,
    ) -> Any: ...
    @overload
    def off(
        self, event: Literal[DEVICE_MANAGER_EVENT.CAMERA_SELECTED], listener: DeviceManagerSelectedListener
    ) -> Any: ...
    def off(self, event: DEVICE_MANAGER_EVENT, listener: DeviceManagerListener) -> None:
        """Unsubscribe from device manager events."""
        ...

    @overload
    def removeListener(
        self,
        event: Literal[DEVICE_MANAGER_EVENT.CAMERA_DESELECTED],
        listener: DeviceManagerDeselectedListener,
    ) -> Any: ...
    @overload
    def removeListener(
        self, event: Literal[DEVICE_MANAGER_EVENT.CAMERA_SELECTED], listener: DeviceManagerSelectedListener
    ) -> Any: ...
    def removeListener(self, event: DEVICE_MANAGER_EVENT, listener: DeviceManagerListener) -> None:
        """Remove a listener from device manager events."""
        ...

    def removeAllListeners(self, event: DEVICE_MANAGER_EVENT | None = None) -> None:
        """Remove all listeners for an event."""
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


class ConnectResult(TypedDict):
    """Result of connecting to a discovered camera."""

    cameraId: str
    """ID of the created camera."""

    cameraName: str
    """Name of the created camera."""


class DiscoveryProvider(ABC):
    """
    Discovery provider interface for camera controller plugins.

    Implement this class to provide camera discovery functionality.
    The backend will call scan() periodically and connect() when users
    want to add a discovered camera.

    Example:
        ```python
        class OnvifDiscoveryProvider(DiscoveryProvider):
            async def scan(self) -> list[DiscoveredCamera]:
                devices = await discover_onvif_devices()
                return [{"id": d.urn, "name": d.name, "manufacturer": d.manufacturer} for d in devices]

            async def getConnectionSchema(self, camera: DiscoveredCamera) -> list[JsonSchemaWithoutCallbacks]:
                return [
                    {
                        "type": "string",
                        "key": "username",
                        "title": "Username",
                        "description": "Camera username",
                    },
                    {
                        "type": "string",
                        "key": "password",
                        "title": "Password",
                        "description": "...",
                        "format": "password",
                    },
                ]

            async def connect(self, camera: DiscoveredCamera, credentials: dict) -> ConnectResult:
                config = await probe_camera(camera, credentials)
                created = await api.deviceManager.createCamera(config)
                return {"cameraId": created.id, "cameraName": created.name}
        ```
    """

    @abstractmethod
    async def scan(self) -> list[DiscoveredCamera]:
        """
        Scan for cameras and return discovered devices.
        Called by backend when polling or when user triggers manual rescan.

        Returns:
            List of discovered cameras
        """
        ...

    @abstractmethod
    async def getConnectionSchema(self, camera: DiscoveredCamera) -> list[JsonSchemaWithoutCallbacks]:
        """
        Get connection schema for a specific discovered camera.
        Returns form fields for credentials/settings needed to connect.

        Args:
            camera: The discovered camera

        Returns:
            JSON schema array for the connection form
        """
        ...

    @abstractmethod
    async def connect(self, camera: DiscoveredCamera, credentials: dict[str, object]) -> ConnectResult:
        """
        Connect to a discovered camera and create it in the system.
        Provider is responsible for probing the device and calling
        api.deviceManager.createCamera() with the configuration.

        Args:
            camera: The discovered camera
            credentials: User-provided credentials from the connection form

        Returns:
            Result with created camera ID and name
        """
        ...


@runtime_checkable
class DiscoveryManager(Protocol):
    """
    Discovery manager interface for camera controller plugins.

    Manages camera discovery providers. Only available to plugins
    with role CameraController or CameraAndSensorProvider.

    Accessed via `api.discoveryManager` in plugins.

    Example:
        ```python
        # Register a discovery provider
        provider = MyDiscoveryProvider()
        await api.discoveryManager.registerProvider(provider)

        # Push cameras discovered asynchronously (e.g., after cloud login)
        cameras = await fetch_cameras_from_cloud()
        await api.discoveryManager.pushDiscoveredCameras(cameras)
        ```
    """

    async def registerProvider(self, provider: DiscoveryProvider) -> None:
        """
        Register a discovery provider.
        The backend will poll scan() and call connect() when users add cameras.

        Args:
            provider: The discovery provider implementation
        """
        ...

    async def unregisterProvider(self) -> None:
        """Unregister the discovery provider."""
        ...

    async def pushDiscoveredCameras(self, cameras: list[DiscoveredCamera]) -> None:
        """
        Push discovered cameras directly to the backend.
        Use this when cameras are discovered asynchronously (e.g., after login).
        Cameras will be immediately visible without waiting for next poll.

        Args:
            cameras: List of discovered cameras to push
        """
        ...


__all__ = [
    # Event enum
    "DEVICE_MANAGER_EVENT",
    # Listener types
    "DeviceManagerSelectedListener",
    "DeviceManagerDeselectedListener",
    "DeviceManagerListener",
    # Status type
    "ConnectionStatus",
    # Manager interfaces
    "CoreManager",
    "DeviceManager",
    "DiscoveryManager",
    # Discovery types
    "DiscoveredCamera",
    "DiscoveredCameraWithState",
    "ConnectResult",
    "DiscoveryProvider",
]
