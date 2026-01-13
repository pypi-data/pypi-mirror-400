from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from enum import Enum
from typing import Any, Generic, Literal, NotRequired, Protocol, overload, runtime_checkable

from typing_extensions import TypedDict, TypeVar

from .base import Sensor, SensorCategory, SensorLike, SensorType


class MotionProperty(str, Enum):
    Detected = "detected"
    Detections = "detections"
    Blocked = "blocked"


BASE_DETECTION_LABELS = ("motion", "person", "vehicle", "animal", "package", "face", "license_plate", "audio")

BaseDetectionLabel = Literal[
    "motion", "person", "vehicle", "animal", "package", "face", "license_plate", "audio"
]

DetectionLabel = BaseDetectionLabel | str


class BoundingBox(TypedDict):
    x: float
    y: float
    width: float
    height: float


class Detection(TypedDict):
    label: DetectionLabel
    confidence: float
    box: BoundingBox
    sourcePluginId: NotRequired[str]
    zone: NotRequired[str]


class MotionSensorProperties(TypedDict):
    detected: bool
    detections: list[Detection]
    blocked: bool


TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class MotionSensorLike(SensorLike, Protocol):
    @property
    def type(self) -> SensorType:
        return SensorType.Motion

    @overload
    def getPropertyValue(self, property: Literal[MotionProperty.Detected]) -> bool | None: ...
    @overload
    def getPropertyValue(self, property: Literal[MotionProperty.Detections]) -> list[Detection] | None: ...
    @overload
    def getPropertyValue(self, property: Literal[MotionProperty.Blocked]) -> bool | None: ...
    @overload
    def getPropertyValue(self, property: str) -> object | None: ...

    def onPropertyChanged(
        self, callback: Callable[[MotionProperty, bool | list[Detection]], None]
    ) -> Callable[[], None]: ...


class MotionSensor(Sensor[MotionSensorProperties, TStorage, str], Generic[TStorage]):
    _requires_frames = False

    def __init__(self, name: str = "Motion Sensor") -> None:
        super().__init__(name)
        self.props.detected = False
        self.props.detections = []
        self.props.blocked = False

    @property
    def type(self) -> SensorType:
        return SensorType.Motion

    @property
    def category(self) -> SensorCategory:
        return SensorCategory.Sensor

    @property
    def detected(self) -> bool:
        return self.props.detected  # type: ignore[no-any-return]

    @detected.setter
    def detected(self, value: bool) -> None:
        if self.props.blocked:
            return
        self.props.detected = value

    @property
    def detections(self) -> list[Detection]:
        return self.props.detections  # type: ignore[no-any-return]

    @detections.setter
    def detections(self, value: list[Detection]) -> None:
        if self.props.blocked:
            return
        self.props.detections = value

    @property
    def blocked(self) -> bool:
        return self.props.blocked  # type: ignore[no-any-return]


class MotionResult(TypedDict):
    detected: bool
    detections: list[Detection]


class VideoFrameData(TypedDict):
    cameraId: NotRequired[str]
    data: bytes
    width: int
    height: int
    format: Literal["nv12", "rgb", "rgba", "gray"]
    timestamp: NotRequired[int]


class MotionDetectorSensor(MotionSensor[TStorage], Generic[TStorage]):
    _requires_frames = True

    @abstractmethod
    async def detectMotion(self, frame: VideoFrameData) -> MotionResult: ...
