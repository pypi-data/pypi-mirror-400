from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from enum import Enum
from typing import Any, Generic, Literal, Protocol, overload, runtime_checkable

from typing_extensions import TypedDict, TypeVar

from .base import Sensor, SensorCategory, SensorLike, SensorType
from .motion import Detection, DetectionLabel, VideoFrameData
from .spec import ObjectModelSpec


class ObjectProperty(str, Enum):
    Detected = "detected"
    Detections = "detections"
    Labels = "labels"


class ObjectSensorProperties(TypedDict):
    detected: bool
    detections: list[Detection]
    labels: list[DetectionLabel]


TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class ObjectSensorLike(SensorLike, Protocol):
    @property
    def type(self) -> SensorType:
        return SensorType.Object

    @overload
    def getPropertyValue(self, property: Literal[ObjectProperty.Detected]) -> bool | None: ...
    @overload
    def getPropertyValue(self, property: Literal[ObjectProperty.Detections]) -> list[Detection] | None: ...
    @overload
    def getPropertyValue(self, property: Literal[ObjectProperty.Labels]) -> list[DetectionLabel] | None: ...
    @overload
    def getPropertyValue(self, property: str) -> object | None: ...

    def onPropertyChanged(
        self, callback: Callable[[ObjectProperty, bool | list[Detection] | list[DetectionLabel]], None]
    ) -> Callable[[], None]: ...


class ObjectSensor(Sensor[ObjectSensorProperties, TStorage, str], Generic[TStorage]):
    _requires_frames = False

    def __init__(self, name: str = "Object Sensor") -> None:
        super().__init__(name)
        self.props.detected = False
        self.props.detections = []
        self.props.labels = []

    @property
    def type(self) -> SensorType:
        return SensorType.Object

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
    def detections(self) -> list[Detection]:
        return self.props.detections  # type: ignore[no-any-return]

    @detections.setter
    def detections(self, value: list[Detection]) -> None:
        self.props.detections = value
        labels = list({d["label"] for d in value})
        self.props.labels = labels

    @property
    def labels(self) -> list[DetectionLabel]:
        return self.props.labels  # type: ignore[no-any-return]

    @labels.setter
    def labels(self, value: list[DetectionLabel]) -> None:
        self.props.labels = value


class ObjectResult(TypedDict):
    detected: bool
    detections: list[Detection]


class ObjectDetectorSensor(ObjectSensor[TStorage], Generic[TStorage]):
    _requires_frames = True

    @property
    @abstractmethod
    def modelSpec(self) -> ObjectModelSpec: ...

    @abstractmethod
    async def detectObjects(self, frame: VideoFrameData) -> ObjectResult: ...
