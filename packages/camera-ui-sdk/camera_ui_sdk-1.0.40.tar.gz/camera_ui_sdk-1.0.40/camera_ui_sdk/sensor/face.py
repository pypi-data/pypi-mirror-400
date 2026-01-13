from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from enum import Enum
from typing import Any, Generic, Literal, NotRequired, Protocol, overload, runtime_checkable

from typing_extensions import TypedDict, TypeVar

from .base import Sensor, SensorCategory, SensorLike, SensorType
from .motion import Detection, VideoFrameData
from .spec import ModelSpec


class FaceProperty(str, Enum):
    Detected = "detected"
    Faces = "faces"


class FaceLandmarks(TypedDict):
    leftEye: tuple[float, float]
    rightEye: tuple[float, float]
    nose: tuple[float, float]
    leftMouth: tuple[float, float]
    rightMouth: tuple[float, float]


class FaceDetection(Detection):
    identity: NotRequired[str]
    embedding: NotRequired[list[float]]
    landmarks: NotRequired[FaceLandmarks]


class FaceSensorProperties(TypedDict):
    detected: bool
    faces: list[FaceDetection]


TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class FaceSensorLike(SensorLike, Protocol):
    @property
    def type(self) -> SensorType:
        return SensorType.Face

    @overload
    def getPropertyValue(self, property: Literal[FaceProperty.Detected]) -> bool | None: ...
    @overload
    def getPropertyValue(self, property: Literal[FaceProperty.Faces]) -> list[FaceDetection] | None: ...
    @overload
    def getPropertyValue(self, property: str) -> object | None: ...

    def onPropertyChanged(
        self, callback: Callable[[FaceProperty, bool | list[FaceDetection]], None]
    ) -> Callable[[], None]: ...


class FaceSensor(Sensor[FaceSensorProperties, TStorage, str], Generic[TStorage]):
    _requires_frames = False

    def __init__(self, name: str = "Face Sensor") -> None:
        super().__init__(name)
        self.props.detected = False
        self.props.faces = []

    @property
    def type(self) -> SensorType:
        return SensorType.Face

    @property
    def category(self) -> SensorCategory:
        return SensorCategory.Sensor

    @property
    def detected(self) -> bool:
        return self.props.detected  # type: ignore[no-any-return]

    @detected.setter
    def detected(self, value: bool) -> None:
        self.props.detected = value

    @property
    def faces(self) -> list[FaceDetection]:
        return self.props.faces  # type: ignore[no-any-return]

    @faces.setter
    def faces(self, value: list[FaceDetection]) -> None:
        self.props.faces = value


class FaceResult(TypedDict):
    detected: bool
    faces: list[FaceDetection]


class FaceDetectorSensor(FaceSensor[TStorage], Generic[TStorage]):
    _requires_frames = True

    @property
    @abstractmethod
    def modelSpec(self) -> ModelSpec: ...

    @abstractmethod
    async def detectFaces(
        self, frame: VideoFrameData, personRegions: list[Detection] | None = None
    ) -> FaceResult: ...
