from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Literal, NotRequired, Protocol, TypedDict, runtime_checkable

from ..sensor import Detection
from .api import PluginAPI

if TYPE_CHECKING:
    from ..camera import CameraDevice
    from ..storage import DeviceStorage
    from ..types import LoggerService

from ..storage import JsonSchema


class ImageMetadata(TypedDict):
    width: int
    height: int


class AudioMetadata(TypedDict):
    mimeType: Literal["audio/mpeg", "audio/wav", "audio/ogg"]


class MotionDetectionPluginResponse(TypedDict):
    detected: bool
    detections: list[Detection]
    videoData: NotRequired[bytes]


class ObjectDetectionPluginResponse(TypedDict):
    detected: bool
    detections: list[Detection]


class AudioDetectionPluginResponse(TypedDict):
    detected: bool
    detections: list[Detection]
    decibels: NotRequired[float]


class BasePlugin(ABC):
    storage_schema: list[JsonSchema] | None = None

    def __init__(self, logger: LoggerService, api: PluginAPI, storage: DeviceStorage) -> None:
        self.logger = logger
        self.api = api
        self.storage = storage

    @abstractmethod
    async def configureCameras(self, camera_devices: list[CameraDevice]) -> None: ...


@runtime_checkable
class MotionDetectionInterface(Protocol):
    async def testMotion(
        self, video_data: bytes, config: dict[str, Any]
    ) -> MotionDetectionPluginResponse | None: ...

    async def motionSettings(self) -> list[JsonSchema] | None: ...


@runtime_checkable
class ObjectDetectionInterface(Protocol):
    async def testObjects(
        self, image_data: bytes, metadata: ImageMetadata, config: dict[str, Any]
    ) -> ObjectDetectionPluginResponse | None: ...

    async def objectSettings(self) -> list[JsonSchema] | None: ...


@runtime_checkable
class AudioDetectionInterface(Protocol):
    async def testAudio(
        self, audio_data: bytes, metadata: AudioMetadata, config: dict[str, Any]
    ) -> AudioDetectionPluginResponse | None: ...

    async def audioSettings(self) -> list[JsonSchema] | None: ...
