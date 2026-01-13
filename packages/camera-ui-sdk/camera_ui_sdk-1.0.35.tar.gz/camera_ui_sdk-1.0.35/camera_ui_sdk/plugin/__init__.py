from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from enum import Enum
from typing import TYPE_CHECKING, Any, Literal, NotRequired, Protocol, TypedDict, cast, runtime_checkable

from ..sensor import (
    AudioFrameData,
    AudioResult,
    ClassifierResult,
    Detection,
    FaceResult,
    LicensePlateResult,
    MotionResult,
    ObjectResult,
    SensorType,
    VideoFrameData,
)

if TYPE_CHECKING:
    from ..camera import CameraDevice
    from ..manager import CoreManager, DeviceManager, DiscoveryManager
    from ..storage import DeviceStorage, JsonSchema, StorageController
    from ..types import LoggerService


PythonVersion = Literal["3.11", "3.12"]
"""Supported Python versions for Python plugins."""

APIListener = Callable[[], None] | Callable[[], Awaitable[None]]
"""Plugin API event listener type (sync or async)."""


class PluginRole(str, Enum):
    """
    Plugin role - determines what capabilities a plugin has.

    - Hub: Consumes sensors from cameras (e.g., HomeKit, MQTT)
    - SensorProvider: Provides sensors to any camera (e.g., object detection)
    - CameraController: Creates and controls cameras (e.g., Ring, Eufy)
    - CameraAndSensorProvider: Creates cameras AND provides sensors to any camera
    """

    Hub = "hub"
    """Hub plugins consume sensors but don't provide any (HomeKit, MQTT)."""

    SensorProvider = "sensorProvider"
    """Provides sensors to any camera (detection plugins)."""

    CameraController = "cameraController"
    """Creates and controls its own cameras (Ring, Eufy, ONVIF)."""

    CameraAndSensorProvider = "cameraAndSensorProvider"
    """Creates cameras AND provides sensors to any camera."""


class API_EVENT(Enum):
    """Plugin API event types."""

    FINISH_LAUNCHING = "finishLaunching"
    """Emitted when plugin initialization is complete."""

    SHUTDOWN = "shutdown"
    """Emitted when plugin is shutting down."""


class PluginContract(TypedDict):
    """
    Plugin contract - defines plugin name, role, and sensor types.

    Every plugin must export a contract that declares its capabilities.
    The contract is validated at plugin load time.

    Example:
        ```python
        contract: PluginContract = {
            "name": "My Detection Plugin",
            "role": PluginRole.SensorProvider,
            "provides": [SensorType.Object, SensorType.Face],
            "consumes": [],
        }
        ```
    """

    name: str
    """Plugin display name."""

    role: PluginRole
    """Plugin role determining capabilities."""

    provides: list[SensorType]
    """Sensor types this plugin provides."""

    consumes: list[SensorType]
    """Sensor types this plugin consumes."""

    pythonVersion: NotRequired[PythonVersion]
    """Python version requirement (Python plugins only)."""

    dependencies: NotRequired[list[str]]
    """Plugin dependencies (other plugin names)."""


class PluginInfo(TypedDict):
    """Plugin information including runtime ID."""

    id: str
    """Unique plugin instance ID."""

    name: str
    """Plugin display name."""

    contract: PluginContract
    """Plugin contract."""


class ImageMetadata(TypedDict):
    """Image metadata for detection test functions."""

    width: int
    """Image width in pixels."""

    height: int
    """Image height in pixels."""


class AudioMetadata(TypedDict):
    """Audio metadata for detection test functions."""

    mimeType: Literal["audio/mpeg", "audio/wav", "audio/ogg"]
    """Audio MIME type."""


class MotionDetectionPluginResponse(TypedDict):
    """Motion detection test response."""

    detected: bool
    """Whether motion was detected."""

    detections: list[Detection]
    """Detection results."""

    videoData: NotRequired[bytes]
    """Processed video data (optional)."""


class ObjectDetectionPluginResponse(TypedDict):
    """Object detection test response."""

    detected: bool
    """Whether objects were detected."""

    detections: list[Detection]
    """Detection results with labels."""


class AudioDetectionPluginResponse(TypedDict):
    """Audio detection test response."""

    detected: bool
    """Whether audio events were detected."""

    detections: list[Detection]
    """Detection results."""

    decibels: NotRequired[float]
    """Audio level in decibels."""


@runtime_checkable
class PluginAPI(Protocol):
    """
    Plugin API - injected into plugins at runtime.

    Provides access to system services and managers. The API is passed
    to the plugin constructor and should be stored for later use.

    Example:
        ```python
        class MyPlugin(CuiPlugin):
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


class CuiPlugin(ABC):
    """
    Base plugin class - all plugins must extend this.

    Plugins receive a logger, API, and storage instance in their constructor.
    The main entry point is configureCameras() which is called when cameras
    are assigned to the plugin.

    Example:
        ```python
        class MyPlugin(CuiPlugin):
            async def configureCameras(self, cameras: list[CameraDevice]) -> None:
                for camera in cameras:
                    sensor = MyMotionSensor()
                    camera.addSensor(sensor)
                    self.logger.log(f"Added sensor to {camera.name}")
        ```
    """

    def __init__(self, logger: LoggerService, api: PluginAPI, storage: DeviceStorage) -> None:
        """
        Initialize the plugin.

        Args:
            logger: Logger service for this plugin
            api: Plugin API for accessing system services
            storage: Plugin storage for configuration
        """
        self.logger = logger
        self.api = api
        self.storage = storage

    @abstractmethod
    async def configureCameras(self, camera_devices: list[CameraDevice]) -> None:
        """
        Configure cameras for this plugin.

        Called when cameras are assigned to this plugin. Add sensors,
        services, and set up event handlers here.

        Args:
            camera_devices: Camera devices assigned to this plugin
        """
        ...

    async def interfaceSchema(self) -> list[JsonSchema] | None:
        """
        Return interface schema for plugin configuration UI.

        Override to provide a configuration UI.

        Returns:
            JSON schema array or None
        """
        return None

    async def testMotion(
        self, video_data: bytes, config: dict[str, Any]
    ) -> MotionDetectionPluginResponse | None:
        """
        Test motion detection with video data.

        Override to support motion detection testing in UI.

        Args:
            video_data: Video data to test
            config: Plugin configuration

        Returns:
            Detection response or None
        """
        return None

    async def testObjects(
        self, image_data: bytes, metadata: ImageMetadata, config: dict[str, Any]
    ) -> ObjectDetectionPluginResponse | None:
        """
        Test object detection with image data.

        Override to support object detection testing in UI.

        Args:
            image_data: Image data to test
            metadata: Image dimensions
            config: Plugin configuration

        Returns:
            Detection response or None
        """
        return None

    async def testAudio(
        self, audio_data: bytes, metadata: AudioMetadata, config: dict[str, Any]
    ) -> AudioDetectionPluginResponse | None:
        """
        Test audio detection with audio data.

        Override to support audio detection testing in UI.

        Args:
            audio_data: Audio data to test
            metadata: Audio format info
            config: Plugin configuration

        Returns:
            Detection response or None
        """
        return None


def get_contract_validation_errors(contract: object) -> list[str]:
    """
    Validate a plugin contract and return validation errors.

    Args:
        contract: Contract object to validate

    Returns:
        Array of error messages (empty if valid)

    Example:
        ```python
        errors = get_contract_validation_errors(my_contract)
        if errors:
            print(f"Invalid contract: {errors}")
        ```
    """
    errors: list[str] = []

    if not contract or not isinstance(contract, dict):
        errors.append(
            f"Contract must be an object. Got: {'null' if contract is None else type(contract).__name__}"
        )
        return errors

    c = cast(Any, contract)
    valid_roles = [r.value for r in PluginRole]
    valid_sensor_types = [s.value for s in SensorType]

    # Check role
    if "role" not in c:
        errors.append('Missing required field: "role"')
    elif not isinstance(c.get("role"), str):
        role_value = c.get("role")
        errors.append(f'Field "role" must be a string. Got: {type(role_value).__name__}')
    elif c["role"] not in valid_roles:
        errors.append(f'Invalid role "{c["role"]}". Valid roles: {", ".join(valid_roles)}')

    # Check name
    if "name" not in c:
        errors.append('Missing required field: "name"')
    elif not isinstance(c["name"], str):
        errors.append(f'Field "name" must be a string. Got: {type(c["name"]).__name__}')
    elif len(c["name"]) == 0:
        errors.append('Field "name" cannot be empty')

    # Check provides
    if "provides" not in c:
        errors.append('Missing required field: "provides"')
    elif not isinstance(c["provides"], list):
        errors.append(f'Field "provides" must be an array. Got: {type(c["provides"]).__name__}')
    else:
        for sensor_type in c["provides"]:
            if sensor_type not in valid_sensor_types:
                errors.append(
                    f'Invalid sensor type in "provides": "{sensor_type}". Valid types: {", ".join(valid_sensor_types)}'
                )

    # Check consumes
    if "consumes" not in c:
        errors.append('Missing required field: "consumes"')
    elif not isinstance(c["consumes"], list):
        errors.append(f'Field "consumes" must be an array. Got: {type(c["consumes"]).__name__}')
    else:
        for sensor_type in c["consumes"]:
            if sensor_type not in valid_sensor_types:
                errors.append(
                    f'Invalid sensor type in "consumes": "{sensor_type}". Valid types: {", ".join(valid_sensor_types)}'
                )

    # Check optional pythonVersion
    if "pythonVersion" in c and c["pythonVersion"] not in ["3.11", "3.12"]:
        errors.append(f'Invalid pythonVersion "{c["pythonVersion"]}". Valid versions: 3.11, 3.12')

    # Check optional dependencies
    if "dependencies" in c and not isinstance(c["dependencies"], list):
        errors.append(f'Field "dependencies" must be an array. Got: {type(c["dependencies"]).__name__}')

    return errors


def validate_contract(contract: object) -> bool:
    """
    Check if a contract is valid.

    Args:
        contract: Contract to validate

    Returns:
        True if valid
    """
    return len(get_contract_validation_errors(contract)) == 0


def validate_contract_consistency(contract: PluginContract, plugin_name: str | None = None) -> None:
    """
    Validate contract consistency rules.

    Throws an error if the contract violates role-specific rules.

    Args:
        contract: Plugin contract
        plugin_name: Optional plugin name for error messages

    Raises:
        ValueError: If contract is inconsistent
    """
    prefix = f'Plugin "{plugin_name}": ' if plugin_name else ""

    match contract["role"]:
        case PluginRole.Hub:
            if len(contract["provides"]) > 0:
                raise ValueError(f"{prefix}Hub plugins cannot provide sensors.")
            if len(contract["consumes"]) == 0:
                raise ValueError(f"{prefix}Hub plugins must consume at least one sensor type.")

        case PluginRole.SensorProvider:
            if len(contract["provides"]) == 0:
                raise ValueError(f"{prefix}SensorProvider plugins must provide at least one sensor type.")

        case PluginRole.CameraAndSensorProvider:
            if len(contract["provides"]) == 0:
                raise ValueError(
                    f"{prefix}CameraAndSensorProvider plugins must provide at least one sensor type."
                )

        case PluginRole.CameraController:
            # CameraController can have empty or filled provides array
            pass


def is_provider(contract: PluginContract) -> bool:
    """
    Check if plugin provides sensors.

    Args:
        contract: Plugin contract

    Returns:
        True if plugin provides at least one sensor type
    """
    return len(contract["provides"]) > 0


def is_consumer(contract: PluginContract) -> bool:
    """
    Check if plugin consumes sensors.

    Args:
        contract: Plugin contract

    Returns:
        True if plugin consumes at least one sensor type
    """
    return len(contract["consumes"]) > 0


def is_hub(contract: PluginContract) -> bool:
    """
    Check if plugin is a hub.

    Args:
        contract: Plugin contract

    Returns:
        True if plugin role is Hub
    """
    return contract["role"] == PluginRole.Hub


def provides_sensor(contract: PluginContract, sensor_type: SensorType) -> bool:
    """
    Check if plugin provides a specific sensor type.

    Args:
        contract: Plugin contract
        sensor_type: Sensor type to check

    Returns:
        True if plugin provides the sensor type
    """
    return sensor_type in contract["provides"]


def consumes_sensor(contract: PluginContract, sensor_type: SensorType) -> bool:
    """
    Check if plugin consumes a specific sensor type.

    Args:
        contract: Plugin contract
        sensor_type: Sensor type to check

    Returns:
        True if plugin consumes the sensor type
    """
    return sensor_type in contract["consumes"]


def can_provide_sensors_to_any_cameras(contract: PluginContract) -> bool:
    """
    Check if plugin can provide sensors to any camera (not just its own).

    Args:
        contract: Plugin contract

    Returns:
        True if role is SensorProvider or CameraAndSensorProvider
    """
    return contract["role"] in (PluginRole.SensorProvider, PluginRole.CameraAndSensorProvider)


def is_camera_controller(contract: PluginContract) -> bool:
    """
    Check if plugin is a camera controller.

    Args:
        contract: Plugin contract

    Returns:
        True if plugin can create cameras
    """
    return can_create_cameras(contract)


def is_qualified_contract(contract: PluginContract) -> bool:
    """
    Check if contract has a valid role.

    Args:
        contract: Plugin contract

    Returns:
        True if role is a valid PluginRole
    """
    return contract["role"] in PluginRole


def can_create_cameras(contract: PluginContract) -> bool:
    """
    Check if plugin can create cameras.

    Args:
        contract: Plugin contract

    Returns:
        True if role is CameraController or CameraAndSensorProvider
    """
    return contract["role"] in (PluginRole.CameraController, PluginRole.CameraAndSensorProvider)


__all__ = [
    # Type Aliases
    "PythonVersion",
    "APIListener",
    # Enums
    "PluginRole",
    "API_EVENT",
    # Contract Types
    "PluginContract",
    "PluginInfo",
    # Test Function Types
    "ImageMetadata",
    "AudioMetadata",
    "MotionDetectionPluginResponse",
    "ObjectDetectionPluginResponse",
    "AudioDetectionPluginResponse",
    # Plugin API & Base Class
    "PluginAPI",
    "CuiPlugin",
    # Re-exported from sensor/types (for convenience)
    "VideoFrameData",
    "AudioFrameData",
    "MotionResult",
    "ObjectResult",
    "FaceResult",
    "AudioResult",
    "LicensePlateResult",
    "ClassifierResult",
    # Contract Validation
    "get_contract_validation_errors",
    "validate_contract",
    "validate_contract_consistency",
    # Contract Helpers
    "is_provider",
    "is_consumer",
    "is_hub",
    "provides_sensor",
    "consumes_sensor",
    "can_provide_sensors_to_any_cameras",
    "is_camera_controller",
    "is_qualified_contract",
    "can_create_cameras",
]
